import docx
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from pyprojroot import here
import yaml
import traceback

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY1"))

# PROMPT "FEW-SHOT" 
full_prompt = """
You are an expert data processing assistant. Your task is to read the company description text and generate high-quality Question-Answer (Q&A) pairs based *only* on the provided text.

You MUST return the output as a **valid JSON array (list)** of objects. Each object must contain "Question" and "Answer" keys.

---EXAMPLE START---

**Input Text:**
"CubeTriangle is a cutting-edge consumer electronics company headquartered in the vibrant city of Ottawa, Canada.
Motto: 'Connecting Innovation, Transforming Lifestyles.'
Company Philosophy: CubeTriangle places a strong emphasis on eco-conscious manufacturing."

**Output JSON:**
[
    {{
      "Question": "Where is CubeTriangle headquartered?",
      "Answer": "CubeTriangle is headquartered in Ottawa, Canada."
    }},
    {{
      "Question": "What is the company motto?",
      "Answer": "'Connecting Innovation, Transforming Lifestyles.'"
    }},
    {{
      "Question": "What is the core philosophy of CubeTriangle?",
      "Answer": "The company places a strong emphasis on eco-conscious manufacturing, ensuring that each product aligns with sustainable practices."
    }}
]
---EXAMPLE END---

Now, process the following text and generate the JSON output in the exact same format.
Try to generate as many relevant questions as possible covering all departments and details.

---TEXT START---
{text_content}
---TEXT END---
"""

def extract_text_from_docx(docx_path):
    """read word"""
    try:
        doc = docx.Document(docx_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip(): 
                full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error read file Word: {e}")
        return None

def generate_qa_from_text(text_content, model_name='gemini-2.5-flash'):
    try:
        model = genai.GenerativeModel(model_name)
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )
        prompt = full_prompt.format(text_content=text_content)
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc() 
        return None

def save_json_file(all_qa_data_list, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_qa_data_list, f, ensure_ascii=False, indent=4)
        
    print(f"Total : {len(all_qa_data_list)} Q&A to output path : {output_path}")

if __name__ == "__main__":
    with open(here("./config/config.yml")) as cfg:
        app_config = yaml.load(cfg, Loader=yaml.FullLoader)

    company_desc_docx_path = here(app_config["raw_data_dir"]["company_description_doc_dir"]) 
    json_output_path = here(app_config["json_dir"]["company_description_json_dir"])

    raw_text = extract_text_from_docx(company_desc_docx_path)
    
    if raw_text:
        json_response_string = generate_qa_from_text(raw_text)
        
        if json_response_string:
                qa_data = json.loads(json_response_string)
                
                if isinstance(qa_data, list) and qa_data:
                    save_json_file(qa_data, json_output_path)
                else:
                    print("Error Q&A list not valid.")
                    
    else:
        print("Error read file Word.")