import fitz  
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import re
from pyprojroot import here
import yaml

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY3"))


# Prompt "Few-Shot"
full_prompt = """
You are an expert data processing assistant. Your task is to read product manual text and generate high-quality **Instruction-Response** pairs based *only* on the provided text.

You MUST return the output as a **valid JSON array (list)** of objects, structured exactly as shown in the example. Each object in the array must contain "**instruction**" and "**response**" keys (case-sensitive).

---EXAMPLE START---

**Input Text:**
"Powering On/Off: Press and hold the side button to power on your CubeTriangle Alpha Smartphone. To power off, press and hold the side button and either volume button, then swipe to power off on the screen.
Using Facial Recognition: Unlock your CubeTriangle Alpha Smartphone with facial recognition by looking directly at the front camera. Ensure proper lighting conditions for optimal performance.
Charging the Device: Charge your CubeTriangle Alpha Smartphone using the provided USB-C cable and power adapter. Connect the cable to the device, and plug the adapter into a power source. Enjoy fast charging with the 65W capability for quick and efficient charging. Capturing Photos: Activate the camera by opening the Camera app or using the dedicated shortcut.
Use the triple-lens camera system for high-quality photos. Experiment with different modes and settings for a personalized photography experience.
Customizing Display Settings: Adjust the display settings of your CubeTriangle Alpha Smartphone by navigating to 'Settings' and selecting 'Display.' Customize features such as brightness, color balance, and screen timeout to suit your preferences."

**Output JSON:**
[
    {{
    "instruction": "Explain how to Power On/Off the CubeTriangle Alpha Smartphone.",
    "response": "To power on, press and hold the side button to power on your CubeTriangle Alpha Smartphone. To power off, press and hold the side button and either volume button, then swipe to power off on the screen."
    }},
    {{
    "instruction": "Provide instructions for using Facial Recognition on the CubeTriangle Alpha Smartphone.",
    "response": "Unlock your CubeTriangle Alpha Smartphone with facial recognition by looking directly at the front camera. Ensure proper lighting conditions for optimal performance."
    }},
    {{
    "instruction": "Guide on charging the CubeTriangle Alpha Smartphone.",
    "response": "Charge your CubeTriangle Alpha Smartphone using the provided USB-C cable and power adapter. Connect the cable to the device, and plug the adapter into a power source. Enjoy fast charging with the 65W capability for quick and efficient charging."
    }},
    {{
    "instruction": "How to capture photos using the CubeTriangle Alpha Smartphone?",
    "response": "Activate the camera by opening the Camera app or using the dedicated shortcut. Use the triple-lens camera system for high-quality photos. Experiment with different modes and settings for a personalized photography experience."
    }},
    {{
    "instruction": "Explain the process of customizing display settings on the CubeTriangle Alpha Smartphone.",
    "response": "Adjust the display settings of your CubeTriangle Alpha Smartphone by navigating to 'Settings' and selecting 'Display.' Customize features such as brightness, color balance, and screen timeout to suit your preferences."
    }}
]
---EXAMPLE END---

Now, process the following text and generate the JSON output in the exact same format.

---TEXT START---
{text_content}
---TEXT END---
"""

def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    return text

def generate_qa_from_text(text_content):
    """Request content to API of Gemini and reponse JSON Q&A."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Output is Json
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )
        # full prompt
        prompt = full_prompt.format(text_content=text_content)
        # call api
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    
    except Exception as e:
        print(f"Error gemini : {e}")
        print(f"Error gemini : {type(e)}")
        return None


def save_json_file(data_string, output_path):
    data = json.loads(data_string)
    
    # Đảm bảo thư mục đầu ra tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Đã lưu thành công file JSON vào: {output_path}")
    return output_path
        

if __name__ == "__main__":
    with open(here("./config/config.yml")) as cfg:
        app_config = yaml.load(cfg, Loader=yaml.FullLoader)

    product_manual_pdf_dir = here(
        app_config["raw_data_dir"]["product_manual_pdf_dir"])
    json_dir = here(app_config["json_dir"]["product_manual_json_dir"])

    
    raw_text = extract_text_from_pdf(product_manual_pdf_dir) 
    if raw_text:
        json_response_string = generate_qa_from_text(raw_text)
        if json_response_string:
            result = save_json_file(json_response_string, json_dir)
            print(result)