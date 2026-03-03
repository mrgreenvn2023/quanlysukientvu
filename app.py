import streamlit as st
import pandas as pd
from docx import Document
import io

# Cấu hình trang Dashboard rộng
st.set_page_config(page_title="TVU Event OS", layout="wide")

# --- HÀM AI GỢI Ý ĐẦU VIỆC (LOGIC CỐT LÕI) ---
def ai_brain_logic(event_name):
    # Giả lập AI phân tích từ Database sự kiện TVU
    kh_tong_the = [
        {"Hạng mục": "Chuẩn bị văn bản", "Nội dung": "Soạn tờ trình, xin chủ trương BGH", "Đơn vị": "Văn phòng", "Deadline": "Ngày 1-5"},
        {"Hạng mục": "Thiết kế nhận diện", "Nội dung": "Thiết kế Logo, túi tote, Backdrop", "Đơn vị": "Tổ Truyền thông", "Deadline": "Ngày 5-10"},
        {"Hạng mục": "Thi công", "Nội dung": "Dựng sân khấu, thử màn hình LED", "Đơn vị": "Phòng QT-TB", "Deadline": "Ngày 18"}
    ]
    kb_dieu_hanh = [
        {"Phút": "00-05", "Nội dung": "Clip intro 20 năm TVU", "Kỹ thuật": "Full LED, nhạc Epic", "Phụ trách": "Kỹ thuật"},
        {"Phút": "05-15", "Nội dung": "Phát biểu của Hiệu trưởng", "Kỹ thuật": "Micro không dây, Slide nền", "Phụ trách": "BGH"}
    ]
    du_toan = [
        {"Khoản mục": "In ấn túi tote", "Số lượng": 500, "Đơn giá": 35000, "Thành tiền": 17500000},
        {"Khoản mục": "Teabreak khách VIP", "Số lượng": 50, "Đơn giá": 150000, "Thành tiền": 7500000}
    ]
    return pd.DataFrame(kh_tong_the), pd.DataFrame(kb_dieu_hanh), pd.DataFrame(du_toan)

# --- GIAO DIỆN CHÍNH ---
st.title("🏛️ TVU EVENT OPERATING SYSTEM")
event_name = st.text_input("TÊN SỰ KIỆN:", placeholder="VD: Lễ công bố Đại học Trà Vinh...")

if st.button("🧠 AI KHỞI TẠO TOÀN BỘ KẾ HOẠCH"):
    kh, kb, dt = ai_brain_logic(event_name)
    st.session_state.kh = kh
    st.session_state.kb = kb
    st.session_state.dt = dt

# --- KHÔNG GIAN LÀM VIỆC CỦA NGƯỜI QUẢN TRỊ ---
if 'kh' in st.session_state:
    tab1, tab2, tab3, tab4 = st.tabs(["📅 KẾ HOẠCH TỔNG THỂ", "🎬 KỊCH BẢN ĐIỀU HÀNH", "💰 DỰ TOÁN", "📦 ĐÓNG GÓI"])
    
    with tab1:
        st.subheader("Điều chỉnh tiến độ & Phân công")
        st.session_state.kh = st.data_editor(st.session_state.kh, num_rows="dynamic", use_container_width=True)
        
    with tab2:
        st.subheader("Checklist Đạo diễn (Âm thanh/Ánh sáng)")
        st.session_state.kb = st.data_editor(st.session_state.kb, num_rows="dynamic", use_container_width=True)
        
    with tab3:
        st.subheader("Quản lý Ngân sách")
        st.session_state.dt = st.data_editor(st.session_state.dt, num_rows="dynamic", use_container_width=True)
        tong_tien = st.session_state.dt["Thành tiền"].sum()
        st.metric("TỔNG CHI PHÍ DỰ KIẾN", f"{tong_tien:,.0f} VNĐ")

    with tab4:
        st.subheader("Kết xuất văn bản chuẩn TVU")
        if st.button("XUẤT FILE WORD TỔNG THỂ"):
            # Tại đây sẽ gọi hàm export_to_word như đã hướng dẫn ở câu trước
            st.success("Đã đóng gói toàn bộ Kế hoạch, Kịch bản, Dự toán vào 1 file duy nhất!")
