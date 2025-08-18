import re


def extract_from_court_decision(full_text: str) -> str:
    """
    Trích lọc các phần quan trọng từ một văn bản Bản án Tòa án.

    Tìm các tiêu đề chính như "NỘI DUNG VỤ ÁN", "NHẬN THẤY", "XÉT THẤY"
    và lấy toàn bộ nội dung từ tiêu đề đầu tiên tìm thấy cho đến cuối.
    """
    # Các từ khóa tiêu đề bắt đầu phần nội dung chính của một bản án
    start_keywords = ["NỘI DUNG VỤ ÁN:", "NHẬN THẤY:", "XÉT THẤY:"]

    start_index = -1

    # Tìm vị trí của từ khóa xuất hiện sớm nhất
    for keyword in start_keywords:
        index = full_text.find(keyword)
        if index != -1:
            if start_index == -1 or index < start_index:
                start_index = index

    if start_index != -1:
        # Nếu tìm thấy, cắt từ vị trí đó đến hết
        print(" -> Đã nhận diện là Bản án. Bắt đầu trích lọc...")
        return full_text[start_index:]

    # Nếu không tìm thấy từ khóa nào, trả về toàn bộ văn bản
    return full_text


def extract_from_legal_decree(full_text: str) -> str:
    """
    Trích lọc các phần quan trọng từ một Văn bản Luật (Quyết định, Nghị định...).

    Tìm các tiêu đề chương/điều đầu tiên như "Chương I", "Điều 1."
    và lấy toàn bộ nội dung từ đó.
    """
    # Tìm vị trí của "Chương I" hoặc "Điều 1."
    match_chapter = re.search(r"Chương I", full_text, re.IGNORECASE)
    match_article = re.search(r"Điều 1\.", full_text)

    start_index = -1

    if match_chapter:
        start_index = match_chapter.start()
    elif match_article:
        start_index = match_article.start()

    if start_index != -1:
        # Nếu tìm thấy, cắt từ vị trí đó đến hết
        print(" -> Đã nhận diện là Văn bản Luật. Bắt đầu trích lọc...")
        return full_text[start_index:]

    # Nếu không tìm thấy, trả về toàn bộ văn bản
    return full_text


def extract_key_sections(full_text: str) -> str:
    """
    Hàm chính để tự động nhận diện loại văn bản và trích lọc.
    """
    # Ưu tiên kiểm tra xem có phải là Bản án không, vì nó có các tiêu đề đặc trưng
    if "NHÂN DANH NƯỚC CỘNG HÒA" in full_text and "Bản án số:" in full_text:
        return extract_from_court_decision(full_text)
    # Nếu không, giả định nó là một Văn bản Luật
    else:
        return extract_from_legal_decree(full_text)


# --- VÍ DỤ SỬ DỤNG ---
if __name__ == "__main__":
    # Giả sử đây là nội dung đầy đủ của file "BanAn_198-2018-DSST.txt"
    full_court_decision_text = """
    TÒA ÁN NHÂN DÂN HUYỆN AN PHÚ - TỈNH AN GIANG
    Bản án số: 198/2018/DS-ST
    Ngày: 14/11/2018
    V/v “Tranh chấp quyền sử dụng đất và bồi thường thiệt hại do công trình xây dựng gây ra”
    NHÂN DANH NƯỚC CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
    ... (các thông tin linh tinh khác) ...
    NỘI DUNG VỤ ÁN:
    Nguyên đơn: Bà Phan Thị G (sinh năm 1953) và Ông Võ Văn B (sinh năm 1950)
    Trình bày: Năm 2015, ông bà xây nhà kho...
    ... (toàn bộ nội dung còn lại của bản án) ...
    """

    # Giả sử đây là nội dung đầy đủ của file "02-2025_QĐ-UBND.txt"
    full_legal_decree_text = """
    QUYẾT ĐỊNH
    Ban hành Quy định chức năng, nhiệm vụ, quyền hạn và cơ cấu tổ chức của Sở Tư pháp Thành phố Hồ Chí Minh
    Căn cứ Luật Tổ chức chính quyền địa phương ngày 16 tháng 6 năm 2025;
    ... (các căn cứ khác) ...
    Điều 3. Trách nhiệm tổ chức thực hiện
    ...
    QUY ĐỊNH
    Chức năng, nhiệm vụ, quyền hạn và cơ cấu tổ chức của Sở Tư pháp Thành phố Hồ Chí Minh
    Chương I: VỊ TRÍ, CHỨC NĂNG
    Điều 1. Vị trí
    Sở Tư pháp là cơ quan chuyên môn thuộc Ủy ban nhân dân Thành phố Hồ Chí Minh...
    ... (toàn bộ nội dung còn lại của quy định) ...
    """

    print("--- Thử nghiệm với Bản án Tòa án ---")
    extracted_text_1 = extract_key_sections(full_court_decision_text)
    print(
        "Văn bản sau khi trích lọc:\n", extracted_text_1[:300], "..."
    )  # In ra 300 ký tự đầu

    print("\n" + "=" * 50 + "\n")

    print("--- Thử nghiệm với Văn bản Luật ---")
    extracted_text_2 = extract_key_sections(full_legal_decree_text)
    print(
        "Văn bản sau khi trích lọc:\n", extracted_text_2[:300], "..."
    )  # In ra 300 ký tự đầu
