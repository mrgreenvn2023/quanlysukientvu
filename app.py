import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import google.generativeai as genai
import io

# --- 1. CẤU HÌNH AI (Thay 'YOUR_API_KEY' bằng Key của ông) ---
genai.configure(api_key="AIzaSyCkYx-gXZxLpNssiO1VgOmCJZZ00biUdvc")
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="TVU Event OS", layout="wide")

# --- 2. HÀM GỌI AI ĐỂ SINH DỮ LIỆU CHI TIẾT ---
def ask_ai_for_plan(event_name):
    prompt = f"""
    Bạn là chuyên gia setup sự kiện đại học cấp cao. Hãy lập kế hoạch cho sự kiện: {event_name} tại Đại học Trà Vinh.
    Trả về kết quả dưới dạng cấu trúc bảng gồm 3 phần:
    1. Kế hoạch tổng thể (Hạng mục, Nội dung, Đơn vị phụ trách, Thời hạn).
    2. Kịch bản điều hành chi tiết (Thời gian, Nội dung, Kỹ thuật/Âm thanh, Người điều phối).
    3. Dự toán sơ bộ (Khoản mục, Đơn giá, Số lượng).
    Lưu ý: Phân vai cho các đơn vị như: Ban Giám hiệu, Văn phòng, Phòng QT-TB, Đoàn Thanh niên.
    """
    response = model.generate_content(prompt)
    return response.text

# --- 3. HÀM XUẤT VĂN BẢN CHUẨN NGHỊ ĐỊNH 30 ---
def export_full_doc(event_name, df_kh, df_kb, df_dt):
    doc = Document()
    # Header: UBND Tỉnh - ĐHTV
    table = doc.add_table(rows=1, cols=2)
    l_cell = table.cell(0, 0).paragraphs[0]
    l_cell.add_run("UBND TỈNH TRÀ VINH\n").bold = True
    l_cell.add_run("ĐẠI HỌC TRÀ VINH\n").bold = True
    l_cell.add_run("Số:      /KH-ĐHTV").italic = True
    
    r_cell = table.cell(0, 1).paragraphs[0]
    r_cell.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    r_cell.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    r_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Tiêu đề
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\nKẾ HOẠCH TỔNG THỂ VÀ KỊCH BẢN\n{event_name.upper()}")
    run.bold = True
    run.font.size = Pt(14)

    doc.add_paragraph(f"Căn cứ nhiệm vụ trọng tâm năm 2026, Hiệu trưởng Đại học Trà Vinh ban hành kế hoạch tổ chức {event_name} như sau:")

    # Thêm các bảng dữ liệu vào Word (Kế hoạch, Kịch bản, Dự toán)
    for title, df in [("I. KẾ HOẠCH CHUẨN BỊ", df_kh), ("II. KỊCH BẢN CHI TIẾT", df_kb), ("III. DỰ TOÁN KINH PHÍ", df_dt)]:
        doc.add_heading(title, level=1)
        t = doc.add_table(rows=1, cols=len(df.columns))
        t.style = 'Table Grid'
        for i, col in enumerate(df.columns):
            t.rows[0].cells[i].text = col
        for _, row in df.iterrows():
            row_cells = t.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)

    # Nơi nhận
    doc.add_paragraph("\nNơi nhận:\n- BGH (để b/c);\n- Các đơn vị liên quan;\n- Lưu VP.")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- 4. GIAO DIỆN NGƯỜI DÙNG ---
st.header("🏛️ HỆ ĐIỀU HÀNH SỰ KIỆN TVU (AI POWERED)")

with st.container(border=True):
    event_name = st.text_input("Tên sự kiện cần tổ chức:", placeholder="Lễ công bố Đại học Trà Vinh...")
    if st.button("🪄 AI TỰ ĐỘNG LẬP DỰ THẢO TOÀN DIỆN"):
        with st.spinner("AI đang tính toán nguồn lực và lập kịch bản..."):
            # Ở đây tôi dùng dữ liệu giả lập để demo nhanh, thực tế sẽ gọi hàm ask_ai_for_plan
            st.session_state.kh = pd.DataFrame([{"Hạng mục": "Hợp đồng in ấn", "Nội dung": "In 500 túi tote TVU", "Phụ trách": "Văn phòng", "Hạn": "15/05"}])
            st.session_state.kb = pd.DataFrame([{"Giờ": "08:00", "Nội dung": "Phát biểu khai mạc", "Kỹ thuật": "Nhạc nhẹ", "Điều phối": "MC"}])
            st.session_state.dt = pd.DataFrame([{"Khoản mục": "Sản xuất túi tote", "Số lượng": 500, "Đơn giá": 35000, "Thành tiền": 17500000}])
            st.success("Đã hoàn thành dự thảo!")

# --- 5. DASHBOARD QUẢN TRỊ ---
if 'kh' in st.session_state:
    tab1, tab2, tab3, tab4 = st.tabs(["📅 KẾ HOẠCH", "🎬 KỊCH BẢN", "💰 DỰ TOÁN", "📄 ĐÓNG GÓI"])
    
    with tab1:
        st.session_state.kh = st.data_editor(st.session_state.kh, num_rows="dynamic", use_container_width=True, key="kh_edit")
    with tab2:
        st.session_state.kb = st.data_editor(st.session_state.kb, num_rows="dynamic", use_container_width=True, key="kb_edit")
    with tab3:
        st.session_state.dt = st.data_editor(st.session_state.dt, num_rows="dynamic", use_container_width=True, key="dt_edit")
    with tab4:
        st.info("Kiểm tra kỹ các thông tin trước khi đóng gói văn bản hành chính.")
        if st.button("📦 XUẤT FILE WORD TỔNG THỂ"):
            word_data = export_full_doc(event_name, st.session_state.kh, st.session_state.kb, st.session_state.dt)
            st.download_button("📥 TẢI VỀ FILE WORD", data=word_data, file_name=f"Ke_hoach_{event_name}.docx")
