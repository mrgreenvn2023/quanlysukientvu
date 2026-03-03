import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import google.generativeai as genai
import io
import json

# --- 1. CẤU HÌNH AI VỚI KEY CỦA ÔNG ---
GOOGLE_API_KEY = "AIzaSyCkYx-gXZxLpNssiO1VgOmCJZZ00biUdvc"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="TVU Event OS - Smart Planner", layout="wide")

# --- 2. HÀM AI XỬ LÝ LOGIC ---
def ask_ai_for_event_data(event_name):
    prompt = f"""
    Bạn là một chuyên gia lập kế hoạch sự kiện cấp cao, am hiểu văn hóa Đại học Trà Vinh (TVU).
    Hãy lập kế hoạch toàn diện cho sự kiện: "{event_name}".
    
    Yêu cầu chi tiết:
    1. Kế hoạch tổng thể: Từ khâu xin chủ trương, thành lập BTC, truyền thông, thiết kế (túi tote, backdrop), thi công sân khấu đến tổng duyệt.
    2. Kịch bản điều hành: Chi tiết từng mốc thời gian, lời dẫn tóm tắt, yêu cầu kỹ thuật (âm thanh, LED).
    3. Dự toán: Liệt kê các khoản chi phí thực tế (VND).

    TRẢ VỀ DUY NHẤT ĐỊNH DẠNG JSON (KHÔNG GIẢI THÍCH) THEO MẪU SAU:
    {{
      "ke_hoach": [
        {{"Hạng mục": "Chuẩn bị văn bản", "Nội dung": "Soạn tờ trình xin chủ trương BGH", "Phụ trách": "Văn phòng", "Hạn": "Ngày 1"}},
        {{"Hạng mục": "Thiết kế", "Nội dung": "Thiết kế bộ nhận diện và túi tote TVU", "Phụ trách": "Tổ Truyền thông", "Hạn": "Ngày 5"}}
      ],
      "kich_ban": [
        {{"Giờ": "08:00", "Nội dung": "Chào cờ, tuyên bố lý do", "Kỹ thuật": "Nhạc quốc ca, LED hình cờ", "Điều phối": "MC"}}
      ],
      "du_toan": [
        {{"Khoản mục": "In túi vải Tote có Logo", "Số lượng": 500, "Đơn giá": 35000, "Thành tiền": 17500000}}
      ]
    }}
    """
    response = model.generate_content(prompt)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_json)
    return pd.DataFrame(data['ke_hoach']), pd.DataFrame(data['kich_ban']), pd.DataFrame(data['du_toan'])

# --- 3. HÀM XUẤT FILE WORD CHUẨN ---
def export_to_word(name, df_kh, df_kb, df_dt):
    doc = Document()
    # Header
    table = doc.add_table(rows=1, cols=2)
    l_cell = table.cell(0, 0).paragraphs[0]
    l_cell.add_run("UBND TỈNH TRÀ VINH\n").bold = True
    l_cell.add_run("ĐẠI HỌC TRÀ VINH\n").bold = True
    l_cell.add_run("Số:      /KH-ĐHTV").italic = True
    
    r_cell = table.cell(0, 1).paragraphs[0]
    r_cell.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    r_cell.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    r_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\nKẾ HOẠCH TỔNG THỂ VÀ KỊCH BẢN\n{name.upper()}")
    run.bold = True
    run.font.size = Pt(14)

    doc.add_paragraph(f"Hiệu trưởng Đại học Trà Vinh ban hành kế hoạch tổ chức {name} với các nội dung sau:")

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

    doc.add_paragraph("\nNơi nhận:\n- BGH (để b/c);\n- Các đơn vị;\n- Lưu VP.")
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🏛️ TVU EVENT OPERATING SYSTEM")
st.markdown("---")

ev_name = st.text_input("Tên sự kiện:", placeholder="Ví dụ: Lễ công bố Đại học Trà Vinh")

if st.button("🪄 AI TỰ ĐỘNG Lập Kế Hoạch Chi Tiết"):
    if ev_name:
        with st.spinner("AI đang thiết kế kịch bản và dự toán..."):
            try:
                kh, kb, dt = ask_ai_for_event_data(ev_name)
                st.session_state.kh = kh
                st.session_state.kb = kb
                st.session_state.dt = dt
                st.success("Đã hoàn tất! Mời ông kiểm tra các Tab bên dưới.")
            except Exception as e:
                st.error(f"Lỗi: {e}. Thử bấm lại nhé!")

if 'kh' in st.session_state:
    t1, t2, t3, t4 = st.tabs(["📅 KẾ HOẠCH", "🎬 KỊCH BẢN MC", "💰 DỰ TOÁN", "📄 XUẤT VĂN BẢN"])
    
    with t1:
        st.session_state.kh = st.data_editor(st.session_state.kh, num_rows="dynamic", use_container_width=True)
    with t2:
        st.session_state.kb = st.data_editor(st.session_state.kb, num_rows="dynamic", use_container_width=True)
    with t3:
        st.session_state.dt = st.data_editor(st.session_state.dt, num_rows="dynamic", use_container_width=True)
        st.metric("TỔNG DỰ TOÁN", f"{st.session_state.dt['Thành tiền'].astype(float).sum():,.0f} VNĐ")
    with t4:
        if st.button("📦 ĐÓNG GÓI VÀ TẢI FILE WORD"):
            word_file = export_to_word(ev_name, st.session_state.kh, st.session_state.kb, st.session_state.dt)
            st.download_button("📥 TẢI XUỐNG FILE .DOCX", data=word_file, file_name=f"Ke_hoach_{ev_name}.docx")
