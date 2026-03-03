import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# --- PHẦN 1: AI TỰ SINH KỊCH BẢN (MẪU LOGIC) ---
def ai_generate_tasks(event_name):
    # Đây là nơi AI sẽ tự suy luận các đầu việc dựa trên kinh nghiệm setup
    # Ở đây tôi làm mẫu 1 bộ khung chuẩn cho Lễ Công Bố của TVU
    tasks = [
        {"Giờ": "07:30", "Hạng mục": "Đón khách", "Nội dung": "Đón đại biểu tại sảnh E21, cài hoa ngực, dẫn vào vị trí", "Phụ trách": "Tổ Lễ tân"},
        {"Giờ": "08:00", "Hạng mục": "Chào cờ", "Nội dung": "Hát quốc ca trên nền nhạc không lời, nghiêm chỉnh", "Phụ trách": "Toàn thể"},
        {"Giờ": "08:15", "Hạng mục": "Tuyên bố lý do", "Nội dung": "Giới thiệu đại biểu Bộ GD&ĐT, Lãnh đạo tỉnh và BGH", "Phụ trách": "MC"},
        {"Giờ": "08:45", "Hạng mục": "Công bố Quyết định", "Nội dung": "Đại diện Bộ GD&ĐT đọc và trao Quyết định lên Đại học", "Phụ trách": "BGH"},
        {"Giờ": "10:30", "Hạng mục": "Kết thúc", "Nội dung": "Tặng quà lưu niệm và mời đại biểu dự tiệc trà", "Phụ trách": "Văn phòng"}
    ]
    return pd.DataFrame(tasks)

# --- PHẦN 2: XUẤT FILE WORD CHUẨN HÀNH CHÍNH ---
def export_to_word(df, event_name):
    doc = Document()
    
    # 1. Header (UBND Tỉnh - ĐHTV | Quốc hiệu)
    table = doc.add_table(rows=1, cols=2)
    table.autofit = True
    
    # Bên trái: Cơ quan chủ quản
    left_cell = table.cell(0, 0).paragraphs[0]
    left_cell.add_run("UBND TỈNH TRÀ VINH\n").bold = True
    left_cell.add_run("ĐẠI HỌC TRÀ VINH\n").bold = True
    left_cell.add_run("Số: 0001/KB-ĐHTV").italic = True
    left_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Bên phải: Quốc hiệu
    right_cell = table.cell(0, 1).paragraphs[0]
    right_cell.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    right_cell.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    right_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Thêm gạch chân dưới Quốc hiệu
    
    # 2. Tiêu đề văn bản
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"\nKỊCH BẢN TỔNG THỂ\n{event_name.upper()}")
    run.bold = True
    run.font.size = Pt(16)

    # 3. Căn cứ
    doc.add_paragraph("Căn cứ các quy định hiện hành và nhu cầu tổ chức sự kiện của Nhà trường;")
    doc.add_paragraph(f"Hiệu trưởng Trường Đại học Trà Vinh ban hành kịch bản tổ chức {event_name} với các nội dung chi tiết sau:")

    # 4. Bảng kịch bản
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = 'Table Grid'
    hdr_cells = t.rows[0].cells
    for i, column in enumerate(df.columns):
        hdr_cells[i].text = column

    for index, row in df.iterrows():
        row_cells = t.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)

    # 5. Nơi nhận
    doc.add_paragraph("\nNơi nhận:")
    doc.add_paragraph("- Ban Giám hiệu (để b/c);\n- Các phòng ban liên quan;\n- Lưu VT, VP.")

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- PHẦN 3: GIAO DIỆN WEBAPP ---
st.title("🚀 AI EVENT PLANNER - TVU EDITION")

event_input = st.text_input("Nhập tên sự kiện (VD: Lễ công bố lên Đại học):", "")

if st.button("AI Tự lập kịch bản"):
    if event_input:
        st.session_state.data = ai_generate_tasks(event_input)
        st.success("AI đã hoàn thành dự thảo! Mời ông kiểm tra và chỉnh sửa bên dưới.")

if 'data' in st.session_state:
    # Cho phép người dùng chỉnh sửa trực tiếp trên Dashboard
    st.subheader("📊 DASHBOARD ĐIỀU CHỈNH")
    edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
    
    # Nút xuất file Word
    word_file = export_to_word(edited_df, event_input)
    st.download_button(
        label="📥 XUẤT FILE WORD (CHUẨN HÀNH CHÍNH)",
        data=word_file,
        file_name=f"Kich_ban_{event_input}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
