import os
import google.generativeai as genai

def llm_call(prompt, model="gemini-2.5-flash", max_output_tokens=512, temperature=0.0, **kwargs):
    """Call Gemini API"""
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set")
    
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model_client = genai.GenerativeModel(model)
    
    response = model_client.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
    )
    
    return response.text