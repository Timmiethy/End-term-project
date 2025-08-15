import os
import re  # Thêm thư viện Regular Expression để làm sạch tốt hơn
import docx
import PyPDF2

# --- Cấu hình Đường dẫn ---
# Giả sử file cleaner.py đang nằm trong src/data_processing/
# Chúng ta cần đi lùi 2 cấp để đến thư mục gốc của dự án
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw')
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'cleaned')

def clean_text(text):
    """
    Hàm này làm sạch văn bản thô:
    - Loại bỏ các ký tự xuống dòng.
    - Thay thế nhiều khoảng trắng liên tiếp bằng một khoảng trắng duy nhất.
    - Xóa khoảng trắng ở đầu và cuối văn bản.
    """
    # Thay thế các ký tự xuống dòng bằng khoảng trắng
    processed_text = text.replace('\n', ' ').replace('\r', '')
    # Thay thế nhiều khoảng trắng bằng một khoảng trắng
    processed_text = re.sub(' +', ' ', processed_text)
    # Xóa khoảng trắng ở đầu và cuối
    return processed_text.strip()

def process_all_files():
    """
    Duyệt qua tất cả các file trong thư mục RAW, trích xuất nội dung,
    làm sạch và lưu vào thư mục CLEANED.
    """
    print(f"Bắt đầu xử lý file từ: {RAW_DATA_PATH}")

    # Đảm bảo thư mục cleaned tồn tại
    if not os.path.exists(CLEANED_DATA_PATH):
        os.makedirs(CLEANED_DATA_PATH)
        print(f"Đã tạo thư mục: {CLEANED_DATA_PATH}")

    files_processed = 0
    for filename in os.listdir(RAW_DATA_PATH):
        file_path = os.path.join(RAW_DATA_PATH, filename)
        content = ''
        
        try:
            if filename.endswith('.docx'):
                doc = docx.Document(file_path)
                content = '\n'.join([para.text for para in doc.paragraphs])

            elif filename.endswith('.pdf'):
                # --- PHẦN HOÀN THIỆN LOGIC ĐỌC FILE PDF ---
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page in reader.pages:
                        content += page.extract_text()
            else:
                # Bỏ qua các file không phải .docx hoặc .pdf
                continue

            # Làm sạch nội dung vừa trích xuất
            cleaned_content = clean_text(content)
            
            # Nếu có nội dung sau khi làm sạch
            if cleaned_content:
                # --- PHẦN HOÀN THIỆN LOGIC LƯU FILE ---
                # Tạo tên file mới với đuôi .txt
                base_filename = os.path.splitext(filename)[0]
                output_filename = f"{base_filename}.txt"
                output_path = os.path.join(CLEANED_DATA_PATH, output_filename)
                
                # Lưu file với encoding utf-8 để hỗ trợ tiếng Việt
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(cleaned_content)
                
                print(f"-> Đã xử lý và lưu thành công file: {output_filename}")
                files_processed += 1

        except Exception as e:
            print(f"!!! Lỗi khi xử lý file {filename}: {e}")

    print(f"\nHoàn tất! Đã xử lý tổng cộng {files_processed} file.")

if __name__ == '__main__':
    process_all_files()
