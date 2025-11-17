import re
import fitz
import re
import json
from pyprojroot import here
import yaml

def extract_product_specification(pdf_path: str) -> list:
    """
    Extracts information of product : name , feature, price

    Parameters:
    - pdf_path (str): The file path to the PDF document.
    - output_json_path (str): The file path to save the extracted question-answer pairs in JSON format.

    Returns:
    - str: The file path to the saved JSON file containing the extracted question-answer pairs.
    """

    full_text = ""
    # Open the PDF file
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            full_text += pdf_document[page_num].get_text()

    # Define a regular expression to information
    pattern = re.compile(
        r"Product name:\s*(.*?)\s*"      # name
        r"Product features:\s*(.*?)\s*"  # features
        r"Price:\s*(.*?)"              # price
        r"(?=\nProduct name:|\Z)",
        re.DOTALL  # Đây là chìa khóa để xử lý ngắt trang
    )
    # Find all matches in the text
    matches = pattern.findall(full_text)

    products_list = []
    # Process each match and create a dictionary
    for match in matches:
        name = match[0].strip()
        features_raw = match[1].strip()
        price = match[2].strip()

        # Làm sạch các dòng tính năng (loại bỏ dòng trống)
        features_list = [f.strip() for f in features_raw.split('\n') if f.strip()]

        products_list.append({
            "name": name,
            "features": features_list,
            "price": price
        })
    
    return products_list

    # if products_list:
    #     with open(output_json_path, "w", encoding="utf-8") as json_file:
    #         json.dump(products_list, json_file, ensure_ascii=False, indent=2)
    #     print(f"Đã trích xuất thành công {len(products_list)} sản phẩm và lưu vào '{output_json_path}'!")


def create_qa_dataset(products_list:list, qa_output_path: str) -> str:
    """
    Create Question-Answer (Q&A) pair from product list

    Parameters:
    - products_list (list) : list product with information : name , feature, price
    - qa_output_path (str): The file path to save the extracted question-answer pairs in JSON format.

    Returns:
    - str: The file path to the saved JSON file containing the extracted question-answer pairs.
    """
    
    qa_dataset = []
    
    # --- 2. Lặp qua từng sản phẩm và tạo Q&A ---
    for product in products_list:
        name = product.get("name")
        price = product.get("price")
        features_list = product.get("features", [])

        # Chuyển đổi danh sách [tính năng 1, tính năng 2] thành
        features_str = ", ".join(features_list)

        # 1. Tạo câu hỏi về TÍNH NĂNG (chỉ khi có tính năng)
        if features_str:
            qa_dataset.append({
                "Question": f"What are the features of {name}?",
                "Answer": features_str
            })

        # 2. Tạo câu hỏi về GIÁ (chỉ khi có giá)
        if price:
            qa_dataset.append({
                "Question": f"How much does {name} cost?",
                "Answer": price
            })

    # --- 3. Ghi kết quả ra file Q&A JSON ---
    if qa_dataset:
        try:
            with open(qa_output_path, "w", encoding="utf-8") as json_file:
                json.dump(qa_dataset, json_file, ensure_ascii=False, indent=2)
            print(f"Đã tạo thành công {len(qa_dataset)} cặp Q&A và lưu vào '{qa_output_path}'!")
            return qa_output_path
        except Exception as e:
            print(f"Lỗi khi ghi file Q&A '{qa_output_path}': {e}")
            return None
    else:
        print("Không có cặp Q&A nào được tạo.")
        return None
    
if __name__ =="__main__":
    with open(here("./config/config.yml")) as cfg:
        app_config = yaml.load(cfg, Loader=yaml.FullLoader)

    product_specifications_pdf_dir = here(
        app_config["raw_data_dir"]["product_specifications_pdf_dir"])
    json_dir = here(app_config["json_dir"]["product_specifications_json_dir"])
    products_list = extract_product_specification(
        product_specifications_pdf_dir)
    qa_dataset_json_path = create_qa_dataset(products_list, qa_output_path=json_dir)
    print(f"Q&A pairs extracted and saved to: {qa_dataset_json_path}")