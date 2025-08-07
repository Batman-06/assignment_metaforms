import json

def construct_prompt(schema_info, cleaned_text):
    required_str = "\n".join(f"- {field}" for field in schema_info['flattened_required'])
    constraints_lines = []
    for field, c in schema_info['enums_patterns'].items():
        parts = []
        if 'enum' in c: parts.append(f"enum values: {c['enum']}")
        if 'pattern' in c: parts.append(f"pattern: {c['pattern']}")
        constraints_lines.append(f"{field}: {', '.join(parts)}")
    constraints_str = "\n".join(constraints_lines) if constraints_lines else "None"
    
    prompt = f"""
Extract all information from the text below and structure it strictly according to the provided JSON Schema.

Required fields (including nested) you must include (across all possible composed/alternative branches):
{required_str}

Field constraints (enums and regex pattern constraints):
{constraints_str}

JSON Schema:
{schema_info['minified']}

Text:
{cleaned_text}

Output only a valid JSON object that strictly adheres to the schema, including nested objects and arrays. Do not include any explanations or extra text.
""".strip()
    return prompt
