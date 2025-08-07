import sys
import json
from preprocessing import preprocess_schema_file, preprocess_text_file
from prompt_construciton import construct_prompt
from api_call_gemini import call_gemini


def main():
    print("Please enter the required file paths:")

    schema_path = input("Enter path to JSON Schema file: ").strip()
    input_text_path = input("Enter path to input text file: ").strip()
    output_json_path = input("Enter path to save output JSON file: ").strip()

    if not schema_path or not input_text_path or not output_json_path:
        print("Error: All file paths must be provided!", file=sys.stderr)
        sys.exit(1)

    print(f"\nUsing:\nSchema: {schema_path}\nInput Text: {input_text_path}\nOutput JSON: {output_json_path}")
    

    # Preprocessing
    print(f"Loading and preprocessing schema from '{schema_path}'...")
    schema_info = preprocess_schema_file(schema_path)

    print(f"Loading and preprocessing text from '{input_text_path}'...")
    cleaned_text = preprocess_text_file(input_text_path)

    # Prompt construction
    print("Constructing prompt...")
    prompt = construct_prompt(schema_info, cleaned_text)

    # API call
    # U can change temperature parameter here
    model_name = "gemini-1.5-flash-latest"
    temperature_value = 0.0
    print(f"Calling Gemini API with model '{model_name}'...")
    raw_output = call_gemini(prompt, model_name=model_name, temperature=temperature_value)

    if raw_output is None:
        print("No output received from the LLM API. Exiting.", file=sys.stderr)
        sys.exit(1)

    # print("Cleaning LLM output...")
    cleaned_output_str = (raw_output)

    # Parse output as JSON
    try:
        llm_parsed_json = json.loads(cleaned_output_str)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse LLM output as JSON: {e}", file=sys.stderr)
        error_file = output_json_path + ".error.txt"
        with open(error_file, "w", encoding="utf-8") as ef:
            ef.write(raw_output)
        print(f"Raw output saved to '{error_file}'. Exiting.", file=sys.stderr)
        sys.exit(1)

    

    # Save output JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(llm_parsed_json, f, indent=2, ensure_ascii=False)
    print(f"LLM output successfully saved to '{output_json_path}'.")


if __name__ == "__main__":
    main()

