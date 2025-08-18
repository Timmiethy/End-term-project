import os
import re
import docx
import pdfplumber

# --- Cấu hình Đường dẫn ---
try:
    PROJECT_ROOT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
    CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "cleaned")
except NameError:
    PROJECT_ROOT = "."  # Fallback
    RAW_DATA_PATH = "data/raw"
    CLEANED_DATA_PATH = "data/cleaned"

# --- TỪ ĐIỂN SỬA LỖI OCR MỞ RỘNG ---
REPLACEMENT_MAP = {
    " N N N N N N N M N N P ": " CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM ",
    "N N Ụ N": "NỘI DUNG",
    "N ẬN ỊN N": "NHẬN ĐỊNH CỦA TÒA ÁN",
    "Q Ế ỊN": "QUYẾT ĐỊNH",
    "NHÂN DANH NƢỚC": "NHÂN DANH NƯỚC",
    "ñ": "đ",
    "ð": "đ",
    "D": "D",
    "d": "d",
    "ủ": "ủ",
    "ã": "ã",
    "ỉ": "ỉ",
    "òa": "òa",
    "ký": "ký",
    "ý": "ý",
    "ồ": "ồ",
    "ầ": "ầ",
    "xã": "xã",
    "hồ": "hồ",
    "phần": "phần",
    "gần": "gần",
    "iê n": "iên",
    "iế": "iế",
    "i n quan": "liên quan",
    " V/v:": " V/v:",
    "b i đơn": "bị đơn",
    " u ê đơ": "nguyên đơn",
    " à": " bà",
    " ô g": " ông",
    " v i": " với",
    " n n": " nên",
    "tro g": "trong",
    " ườ g hợp": " trường hợp",
    " khô g": " không",
    " qu đị h": " quy định",
    " h h vi": " hành vi",
    " h h sự": " hình sự",
    "ph p uật": "pháp luật",
    "x t xử": "xét xử",
    # Thêm các lỗi phổ biến khác bạn có thể tìm thấy
}


def clean_text_advanced(text: str) -> str:
    """
    Hàm làm sạch văn bản nâng cao, xử lý nhiều loại lỗi OCR và cấu trúc.
    """
    # 1. Sửa các ký tự lỗi OCR phổ biến dựa trên từ điển
    for bad_pattern, good_pattern in REPLACEMENT_MAP.items():
        text = text.replace(bad_pattern, good_pattern)

    # 2. Lọc bỏ các dòng nhiễu
    lines = text.split("\n")
    cleaned_lines = []
    noise_patterns = [
        re.compile(r"^\s*\d+\s*$"),  # Dòng chỉ chứa số trang
        re.compile(r"CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM.*Độc lập", re.IGNORECASE),
        re.compile(r"^NHÂN DANH NƯỚC CỘNG HÒA", re.IGNORECASE),
        re.compile(r"^\s*TM\. HỘI ĐỒNG XÉT XỬ", re.IGNORECASE),
        re.compile(r"^\s*THẨM PHÁN – CHỦ TỌA", re.IGNORECASE),
        re.compile(r"^\s*Nơi nhận:$", re.IGNORECASE),
    ]
    for line in lines:
        is_noise = False
        if line.strip() == "":  # Bỏ qua dòng trống
            continue
        for pattern in noise_patterns:
            if pattern.search(line):
                is_noise = True
                break
        if not is_noise:
            cleaned_lines.append(line.strip())

    text = "\n".join(cleaned_lines)

    # 3. Nối các câu bị ngắt dòng bất thường (ví dụ: cuối dòng không có dấu chấm)
    text = re.sub(r"([a-zà-ỹ])\n([a-zà-ỹ])", r"\1 \2", text)

    # 4. Chuẩn hóa khoảng trắng và dấu câu
    text = re.sub(r"\s+([.,:;!?])", r"\1", text)  # Xóa khoảng trắng trước dấu câu
    text = re.sub(r"\s+", " ", text).strip()  # Thay thế nhiều khoảng trắng bằng một

    return text


def process_all_files():
    """
    Duyệt qua tất cả các file trong thư mục RAW, trích xuất nội dung,
    làm sạch và lưu vào thư mục CLEANED.
    """
    print(f"Bắt đầu xử lý file từ: {RAW_DATA_PATH}")
    if not os.path.exists(CLEANED_DATA_PATH):
        os.makedirs(CLEANED_DATA_PATH)
        print(f"Đã tạo thư mục: {CLEANED_DATA_PATH}")

    files_processed = 0
    for filename in os.listdir(RAW_DATA_PATH):
        if not (
            filename.lower().endswith(".docx") or filename.lower().endswith(".pdf")
        ):
            continue  # Bỏ qua các file không phải docx hoặc pdf

        file_path = os.path.join(RAW_DATA_PATH, filename)
        content = ""

        try:
            print(f"\n[+] Đang xử lý file: {filename}")
            if filename.lower().endswith(".docx"):
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
            elif filename.lower().endswith(".pdf"):
                with pdfplumber.open(file_path) as pdf:
                    content = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"

            cleaned_content = clean_text_advanced(content)

            if cleaned_content:
                base_filename = os.path.splitext(filename)[0]
                output_filename = f"{base_filename}.txt"
                output_path = os.path.join(CLEANED_DATA_PATH, output_filename)

                with open(output_path, "w", encoding="utf-8") as output_file:
                    output_file.write(cleaned_content)

                print(f"    -> Đã xử lý và lưu thành công file: {output_filename}")
                files_processed += 1
            else:
                print(
                    f"    -> Cảnh báo: Không trích xuất được nội dung từ file {filename}"
                )

        except Exception as e:
            print(f"    !!! Lỗi khi xử lý file {filename}: {e}")

    print(f"\nHoàn tất! Đã xử lý tổng cộng {files_processed} file.")


if __name__ == "__main__":
    process_all_files()
