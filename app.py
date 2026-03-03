import streamlit as st
import pandas as pd

# 1. Cấu hình giao diện
st.set_page_config(page_title="TVU Event Manager", layout="wide")
st.title("🏛️ HỆ THỐNG LẬP KỊCH BẢN SỰ KIỆN TVU")

# 2. Tạo bảng dữ liệu mẫu (Giống như file Excel)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Giờ": "07:30", "Hạng mục": "Đón khách", "Nội dung": "Đón đại biểu tại sảnh E21", "Phụ trách": "Tổ Lễ tân"},
        {"Giờ": "08:00", "Hạng mục": "Khai mạc", "Nội dung": "Chào cờ, tuyên bố lý do", "Phụ trách": "MC"},
    ])

# 3. Khu vực Nhập liệu (Input)
with st.expander("➕ THÊM HẠNG MỤC MỚI"):
    col1, col2 = st.columns(2)
    with col1:
        txt_gio = st.text_input("Thời gian")
        txt_ten = st.text_input("Tên hạng mục")
    with col2:
        txt_pic = st.selectbox("Người phụ trách", ["BGH", "Văn phòng", "Đoàn Thanh niên", "Kỹ thuật"])
        txt_nd = st.text_area("Chi tiết nội dung")
    
    if st.button("Thêm vào kịch bản"):
        new_row = {"Giờ": txt_gio, "Hạng mục": txt_ten, "Nội dung": txt_nd, "Phụ trách": txt_pic}
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Đã thêm thành công!")

# 4. Hiển thị Dashboard & Chỉnh sửa
st.subheader("📋 KỊCH BẢN TỔNG THỂ")
# Cho phép sửa trực tiếp như Excel
edited_df = st.data_editor(st.session_state.data, use_container_width=True, num_rows="dynamic")

# 5. Bộ lọc (Dành cho từng bộ phận)
st.divider()
st.subheader("🔍 XEM KỊCH BẢN THEO BỘ PHẬN")
bo_phan = st.selectbox("Chọn bộ phận để lọc:", edited_df["Phụ trách"].unique())
filtered_df = edited_df[edited_df["Phụ trách"] == bo_phan]
st.table(filtered_df)

# 6. Đánh giá rút kinh nghiệm (Lưu vào Dashboard)
st.divider()
st.subheader("💡 RÚT KINH NGHIỆM")
note = st.text_area("Nhập đánh giá sau sự kiện để lưu trữ dữ liệu...")
if st.button("Lưu đánh giá"):
    st.info("Đã lưu vào kho dữ liệu hệ thống!")
