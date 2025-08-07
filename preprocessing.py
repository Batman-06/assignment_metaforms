import json
import re
import copy

def remove_comments(obj):
    # Recursively remove $comment from dict or list
    if isinstance(obj, dict):
        return {k: remove_comments(v) for k, v in obj.items() if k != '$comment'}
    elif isinstance(obj, list):
        return [remove_comments(item) for item in obj]
    else:
        return obj

def resolve_refs(schema, root=None):
    # Recursively resolve internal $ref, only within the file
    
    if root is None:
        root = schema
    if isinstance(schema, dict):
        if '$ref' in schema:
            ref_path = schema['$ref']
            if not ref_path.startswith('#/'):
                raise ValueError(f"Only internal $ref supported: {ref_path}")
            target = root
            for part in ref_path.lstrip('#/').split('/'):
                target = target[part]
            merged = copy.deepcopy(target)
            merged.update({k: v for k, v in schema.items() if k != '$ref'})
            return resolve_refs(merged, root)
        else:
            return {k: resolve_refs(v, root) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [resolve_refs(item, root) for item in schema]
    else:
        return schema

def flatten_required(schema, path=""):
    
    # Collects all required property paths from JSON Schema, 
    # handling anyOf, oneOf, allOf.
    
    required_paths = []

    # For allOf
    if 'allOf' in schema:
        for subschema in schema['allOf']:
            required_paths.extend(flatten_required(subschema, path))
    # For anyOf/oneOf, union all requireds (for LLM prompt unionization)
    for keyword in ['anyOf', 'oneOf']:
        if keyword in schema:
            seen = set()
            for subschema in schema[keyword]:
                for rp in flatten_required(subschema, path):
                    if rp not in seen:
                        required_paths.append(rp)
                        seen.add(rp)
    # Standard required
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    for req_key in required:
        current_path = f"{path}.{req_key}" if path else req_key
        if current_path not in required_paths:
            required_paths.append(current_path)
        prop_schema = properties.get(req_key, {})
        if prop_schema.get("type") == "object":
            required_paths.extend(flatten_required(prop_schema, current_path))
        elif prop_schema.get("type") == "array" and isinstance(prop_schema.get("items"), dict):
            items = prop_schema.get("items", {})
            if items.get("type") == "object":
                array_path = f"{current_path}[]"
                required_paths.extend(flatten_required(items, array_path))

    return required_paths

def extract_enums_patterns(schema, path=""):
    
    # Recursively extract enums and regex pattern constraints from schema properties,
    # handling allOf, anyOf, oneOf.
    
    constraints = {}
    if not isinstance(schema, dict): return constraints
    # allOf: collect all constraints
    if 'allOf' in schema:
        for subschema in schema['allOf']:
            constraints.update(extract_enums_patterns(subschema, path))
    # anyOf/oneOf: union constraints
    for keyword in ['anyOf', 'oneOf']:
        if keyword in schema:
            for subschema in schema[keyword]:
                constraints.update(extract_enums_patterns(subschema, path))
    properties = schema.get("properties", {})
    for prop_key, prop_value in properties.items():
        current_path = f"{path}.{prop_key}" if path else prop_key
        entry = {}
        if 'enum' in prop_value:
            entry['enum'] = prop_value['enum']
        if 'pattern' in prop_value:
            entry['pattern'] = prop_value['pattern']
        if entry:
            constraints[current_path] = entry
        if prop_value.get("type") == "object":
            constraints.update(extract_enums_patterns(prop_value, current_path))
        if prop_value.get("type") == "array" and isinstance(prop_value.get("items"), dict):
            items = prop_value.get("items")
            if items.get("type") == "object":
                constraints.update(extract_enums_patterns(items, current_path + "[]"))
    return constraints

def minify_json(schema):
    return json.dumps(schema, separators=(',', ':'))

def clean_text(text):
    """Normalize whitespace, remove basic HTML and control characters."""
    text = text.strip()
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text

def preprocess_schema_file(schema_path):
    with open(schema_path, 'r', encoding='utf-8') as f:
        raw_schema = json.load(f)
    schema_no_comments = remove_comments(raw_schema)
    schema_resolved = resolve_refs(schema_no_comments)
    flattened_required = flatten_required(schema_resolved)
    enums_patterns = extract_enums_patterns(schema_resolved)
    return {
        "raw": raw_schema,
        "clean": schema_no_comments,
        "resolved": schema_resolved,
        "flattened_required": flattened_required,
        "enums_patterns": enums_patterns,
        "minified": minify_json(schema_resolved)
    }

def preprocess_text_file(text_path):
    with open(text_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return clean_text(raw)
