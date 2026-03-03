import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import google.generativeai as genai
import io
import json

# --- 1. CẤU HÌNH AI (ĐÃ FIX LỖI MODEL) ---
GOOGLE_API_KEY = "AIzaSyCkYx-gXZxLpNssiO1VgOmCJZZ00biUdvc"
genai.configure(api_key=GOOGLE_API_KEY)
# Sử dụng 'gemini-1.5-flash-latest' để đảm bảo luôn cập nhật phiên bản mới nhất
model = genai.GenerativeModel('gemini-1.5-flash-latest')

st.set_page_config(page_title="TVU Event OS - v1.2", layout="wide")

# --- 2. HÀM AI XỬ LÝ (ÉP KIỂU JSON CHẶT CHẼ) ---
def ask_ai_for_event_data(event_name):
    prompt = f"""
    Bạn là chuyên gia sự kiện TVU. Hãy lập kế hoạch: "{event_name}".
    TRẢ VỀ DUY NHẤT JSON (KHÔNG GIẢI THÍCH):
    {{
      "ke_hoach": [{{"Hạng mục": "...", "Nội dung": "...", "Phụ trách": "...", "Hạn": "..."}}],
      "kich_ban": [{{"Giờ": "...", "Nội dung": "...", "Kỹ thuật": "...", "Điều phối": "..."}}],
      "du_toan": [{{"Khoản mục": "...", "Số lượng": 0, "Đơn giá": 0, "Thành tiền": 0}}]
    }}
    Lưu ý: Đổ ra ít nhất 10-15 dòng cho mỗi phần để đảm bảo tính chi tiết.
    """
    response = model.generate_content(prompt)
    # Làm sạch chuỗi trả về từ AI
    raw_text = response.text.strip()
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
    
    data = json.loads(raw_text)
    return pd.DataFrame(data['ke_hoach']), pd.DataFrame(data['kich_ban']), pd.DataFrame(data['du_toan'])

# --- 3. HÀM XUẤT FILE WORD (CHUẨN HÀNH CHÍNH) ---
def export_to_word(name, df_kh, df_kb, df_dt):
    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    table.columns[0].width = Pt(200)
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

    doc.add_paragraph(f"Hiệu trưởng Đại học Trà Vinh ban hành kế hoạch tổ chức {name}:")

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
st.title("🏛️ TVU EVENT OPERATING SYSTEM (Fixed v1.2)")

ev_name = st.text_input("Tên sự kiện:", value="Lễ công bố Đại học Trà Vinh")

if st.button("🪄 AI TỰ ĐỘNG Lập Kế Hoạch"):
    with st.spinner("AI đang 'nhai' dữ liệu, đợi tí nhe..."):
        try:
            kh, kb, dt = ask_ai_for_event_data(ev_name)
            st.session_state.kh = kh
            st.session_state.kb = kb
            st.session_state.dt = dt
            st.success("Xong rồi ông ơi! Kiểm tra mấy cái thẻ (Tab) ở dưới nhé.")
        except Exception as e:
            st.error(f"Vẫn còn lỗi: {e}. Thử bấm lại lần nữa xem sao.")

if 'kh' in st.session_state:
    t1, t2, t3, t4 = st.tabs(["📅 KẾ HOẠCH", "🎬 KỊCH BẢN MC", "💰 DỰ TOÁN", "📄 XUẤT VĂN BẢN"])
    
    with t1:
        st.session_state.kh = st.data_editor(st.session_state.kh, num_rows="dynamic", use_container_width=True)
    with t2:
        st.session_state.kb = st.data_editor(st.session_state.kb, num_rows="dynamic", use_container_width=True)
    with t3:
        # Tự động tính Thành tiền nếu ông sửa Số lượng hoặc Đơn giá
        df_dt = st.data_editor(st.session_state.dt, num_rows="dynamic", use_container_width=True)
        df_dt['Thành tiền'] = df_dt['Số lượng'].astype(float) * df_dt['Đơn giá'].astype(float)
        st.session_state.dt = df_dt
        st.metric("TỔNG TIỀN DỰ KIẾN", f"{df_dt['Thành tiền'].sum():,.0f} VNĐ")
    with t4:
        if st.button("📦 XUẤT FILE WORD"):
            word_file = export_to_word(ev_name, st.session_state.kh, st.session_state.kb, st.session_state.dt)
            st.download_button("📥 TẢI FILE WORD CHUẨN", data=word_file, file_name=f"Ke_hoach_{ev_name}.docx")
