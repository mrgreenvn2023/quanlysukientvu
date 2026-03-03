import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import google.generativeai as genai
import io
import json

# --- 1. CẤU HÌNH AI (BẢN V1.4 FIX LỖI 404) ---
GOOGLE_API_KEY = "AIzaSyDX1yM5RSPjb4b8iX6Quoz59HQkQoheVGw"
genai.configure(api_key=GOOGLE_API_KEY)

# Cách gọi model an toàn nhất để tránh lỗi version
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="TVU Event OS - v1.4", layout="wide")

# --- 2. HÀM AI XỬ LÝ ---
def ask_ai_for_event_data(event_name):
    prompt = f"""
    Bạn là chuyên gia sự kiện tại Đại học Trà Vinh (TVU). 
    Hãy lập hồ sơ chi tiết cho sự kiện: "{event_name}".
    
    Yêu cầu trả về JSON chuẩn (KHÔNG GIẢI THÍCH):
    {{
      "ke_hoach": [{{"Hạng mục": "...", "Nội dung": "...", "Phụ trách": "...", "Hạn": "..."}}],
      "kich_ban": [{{"Giờ": "...", "Nội dung": "...", "Kỹ thuật": "...", "Điều phối": "..."}}],
      "du_toan": [{{"Khoản mục": "...", "Số lượng": 0, "Đơn giá": 0, "Thành tiền": 0}}]
    }}
    Lưu ý: Đổ ra ít nhất 10 dòng công việc thực tế.
    """
    # Sử dụng phương thức generate_content cơ bản
    response = model.generate_content(prompt)
    
    # Xử lý chuỗi JSON cẩn thận
    text = response.text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    data = json.loads(text.strip())
    return pd.DataFrame(data['ke_hoach']), pd.DataFrame(data['kich_ban']), pd.DataFrame(data['du_toan'])

# --- 3. HÀM XUẤT WORD CHUẨN ---
def export_to_word(name, df_kh, df_kb, df_dt):
    doc = Document()
    # Tạo Header 2 cột
    table = doc.add_table(rows=1, cols=2)
    l_cell = table.cell(0, 0).paragraphs[0]
    l_cell.add_run("UBND TỈNH TRÀ VINH\n").bold = True
    l_cell.add_run("ĐẠI HỌC TRÀ VINH\n").bold = True
    l_cell.add_run("Số:      /KH-ĐHTV").italic = True
    
    r_cell = table.cell(0, 1).paragraphs[0]
    r_cell.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    r_cell.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    r_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\nKẾ HOẠCH TỔNG THỂ VÀ KỊCH BẢN\n{name.upper()}")
    run.bold = True
    run.font.size = Pt(14)

    doc.add_paragraph(f"Căn cứ tình hình thực tế, Đại học Trà Vinh ban hành kế hoạch tổ chức {name}:")

    for title, df in [("I. KẾ HOẠCH", df_kh), ("II. KỊCH BẢN", df_kb), ("III. DỰ TOÁN", df_dt)]:
        doc.add_heading(title, level=1)
        t = doc.add_table(rows=1, cols=len(df.columns))
        t.style = 'Table Grid'
        for i, col in enumerate(df.columns):
            t.rows[0].cells[i].text = col
        for _, row in df.iterrows():
            row_cells = t.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)

    doc.add_paragraph("\nNơi nhận:\n- BGH (để b/c);\n- Lưu VP.")
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- 4. GIAO DIỆN ---
st.title("🏛️ TVU EVENT OS (Ultra Stable v1.4)")

ev_name = st.text_input("Nhập tên sự kiện:", value="Lễ công bố Đại học Trà Vinh")

if st.button("🪄 AI TỰ ĐỘNG Lập Kế Hoạch"):
    with st.spinner("AI đang 'nặn' kịch bản cho ông..."):
        try:
            kh, kb, dt = ask_ai_for_event_data(ev_name)
            st.session_state.kh = kh
            st.session_state.kb = kb
            st.session_state.dt = dt
            st.success("Ngon rồi ông ơi! Dữ liệu đã về máy.")
        except Exception as e:
            st.error(f"Lỗi rồi: {e}. Ông kiểm tra lại API Key hoặc bấm thử lại nhé!")

if 'kh' in st.session_state:
    t1, t2, t3, t4 = st.tabs(["📅 KẾ HOẠCH", "🎬 KỊCH BẢN", "💰 DỰ TOÁN", "📄 XUẤT FILE"])
    
    with t1:
        st.session_state.kh = st.data_editor(st.session_state.kh, num_rows="dynamic", use_container_width=True)
    with t2:
        st.session_state.kb = st.data_editor(st.session_state.kb, num_rows="dynamic", use_container_width=True)
    with t3:
        df_dt = st.data_editor(st.session_state.dt, num_rows="dynamic", use_container_width=True)
        # Ép kiểu dữ liệu để tính toán
        try:
            df_dt['Thành tiền'] = pd.to_numeric(df_dt['Số lượng']) * pd.to_numeric(df_dt['Đơn giá'])
            st.metric("TỔNG TIỀN", f"{df_dt['Thành tiền'].sum():,.0f} VNĐ")
        except: pass
    with t4:
        if st.button("📦 XUẤT FILE WORD"):
            word_file = export_to_word(ev_name, st.session_state.kh, st.session_state.kb, st.session_state.dt)
            st.download_button("📥 TẢI FILE WORD", data=word_file, file_name=f"Ke_hoach_{ev_name}.docx")
