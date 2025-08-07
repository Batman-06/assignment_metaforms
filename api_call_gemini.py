import os
import sys
import google.generativeai as genai


os.environ["GEMINI_API_KEY"] = 'UP API KEY'

try:
   
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)

except ValueError as e:
    print(e, file=sys.stderr)
    sys.exit(1)


def call_gemini(prompt: str, model_name: str = "gemini-1.5-flash-latest", temperature: float = 0.0) -> str | None:
    """
    Calls the Gemini API to generate content from a prompt.

    Args:
        prompt (str): The text prompt to send.
        model_name (str): The Gemini model to use.
        temperature (float): Sampling temperature for generation.

    Returns:
        str: The generated text response from Gemini, or None on error.
    """
    try:
        # Instantiate the model
        model = genai.GenerativeModel(model_name=model_name)

        # Set up generation configuration
        generation_config = genai.types.GenerationConfig(
            temperature=1,
            response_mime_type="application/json"
        )

        # Call the generate_content method on the model instance
        response = model.generate_content(
            contents=prompt,
            generation_config=generation_config,
        )

        # Return the generated text
        return response.text
    
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}", file=sys.stderr)
        return None

