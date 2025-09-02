from docx import Document

def docx_to_txt(input_path: str, output_path: str):
    doc = Document(input_path)
    with open(output_path, "w", encoding="utf-8") as f:
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:  # nếu có nội dung
                f.write(text + "\n")  # ghi xong xuống dòng
            else:
                f.write("\n")  # giữ dòng trống giữa các đoạn

# Ví dụ dùng
docx_to_txt("../document/data.docx", "output.txt")
