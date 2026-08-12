import streamlit as st
import pandas as pd
import os
import base64
from streamlit_gsheets import GSheetsConnection

# ================= CẤU HÌNH TRANG & GIAO DIỆN =================
st.set_page_config(page_title="KẾT QUẢ ĐĂNG KÝ TRIP", page_icon="🌿", layout="centered")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

qr_base64 = get_image_base64("TTCK.jpg")
thongtin_base64 = get_image_base64("THÔNG TIN TRIP POST.jpg")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2, h3, h4, .stTabs [data-baseweb="tab"] p { color: #2C5E1A !important; font-weight: bold; }
    
    .stButton>button { background-color: #D4AF37; color: #1A3C0F; font-weight: bold; border-radius: 8px; border: none; width: 100%; padding: 10px; }
    .stButton>button:hover { background-color: #2C5E1A; color: #FFFFFF; border: none; }
    .stTextInput>div>div>input { background-color: #F8F9FA; color: #333333; border: 1px solid #2C5E1A; border-radius: 5px; }
    .stSelectbox>div>div>div { border-color: #2C5E1A; }
    
    .section-title { background: linear-gradient(90deg, #2C5E1A 0%, #D4AF37 100%); color: white; padding: 12px 15px; border-radius: 8px 8px 0 0; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 20px; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); overflow: hidden; }
    .custom-table thead tr { background-color: #1A3C0F; } 
    .custom-table th { color: white; padding: 12px 14px; text-align: center; font-size: 15px; border: none; }
    .custom-table td { padding: 14px; border-bottom: 1px solid #EEEEEE; border-right: 1px solid #EEEEEE; text-align: center; font-weight: bold; color: #2C5E1A; background-color: #FFFFFF;}
    
    .payment-box { display: flex; flex-wrap: wrap; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); background-color: #FAFAFA; margin-bottom: 25px; }
    .payment-info { flex: 1.3; min-width: 250px; padding-right: 15px; }
    .payment-qr { flex: 1; min-width: 200px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    
    .highlight-val { color: #D4AF37; font-weight: bold; font-size: 16px;} 
    .info-row { margin-bottom: 15px; font-size: 15px; border-bottom: 1px dashed #EEEEEE; padding-bottom: 10px;}
    
    .metric-card { background-color: #FFFFFF; border: 1px solid #E0E6ED; border-top: 5px solid #2C5E1A; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;}
    .metric-title { font-size: 16px; color: #2C5E1A; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;}
    .metric-value { font-size: 28px; color: #D4AF37; font-weight: 900;}
    
    .cancel-alert { background-color: #F8D7DA; color: #721C24; padding: 20px; border-radius: 8px; border: 1px solid #F5C6CB; margin-bottom: 20px; text-align: center; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# URL Google Sheet
url = "https://docs.google.com/spreadsheets/d/1xwALxKMnTwXeP8Vy3BVJTuD0JpF981_mv_b4AjIaigA/edit"

@st.cache_data(ttl=5) # Giữ cache ngắn để admin update/user coi realtime
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_data = conn.read(spreadsheet=url, worksheet="Data App")
    df_config = conn.read(spreadsheet=url, worksheet="Thông số")
    
    # Xử lý số điện thoại về chuẩn chuỗi (text), tránh mất số 0
    df_data['SDT'] = df_data['SDT'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df_data, df_config, conn

try:
    df_data, df_config, conn = load_data()
except Exception as e:
    st.error(f"Lỗi kết nối dữ liệu: {e}")
    st.stop()

# Xử lý thông số E2, F2 cho thông báo
try:
    time_ck = int(df_config.iloc[0]['Thời gian CK']) if not pd.isna(df_config.iloc[0]['Thời gian CK']) else 0
    time_check = int(df_config.iloc[0]['Thời gian Check']) if not pd.isna(df_config.iloc[0]['Thời gian Check']) else 0
    wait_time = time_ck + time_check
except:
    wait_time = 15 # Default

# ================= PHẦN 1: USER - KẾT QUẢ ĐĂNG KÝ =================
st.markdown("<h1 style='text-align: center;'>KẾT QUẢ ĐĂNG KÝ <br> TRIP ĐÊM HUYỀN BÍ</h1>", unsafe_allow_html=True)

phone_input = st.text_input("Nhập số điện thoại của bạn (đã dùng đăng ký):", placeholder="Ví dụ: 0901234567")

if st.button("TRA CỨU KẾT QUẢ 🚀"):
    if phone_input:
        clean_input = phone_input.strip().lstrip('0')
        df_data['Phone_Compare'] = df_data['SDT'].str.lstrip('0')
        matched_rows = df_data[df_data['Phone_Compare'] == clean_input]
        
        if not matched_rows.empty:
            for idx, row in matched_rows.iterrows():
                dot_dk = row['Đợt ĐK']
                sdt = row['SDT']
                status = str(row['Trạng thái CK']).strip().upper()
                sl_dk = int(row['SL']) if pd.notna(row['SL']) else 1
                
                # Logic cắt Tên - Năm sinh
                ds_nguoi = str(row['DS người']).split(',')
                first_name = ds_nguoi[0].split('-')[0].strip() if ds_nguoi else "Bạn"
                
                # BÀI TOÁN LỐ SLOT: Tính toán Cumsum (Cộng dồn theo Timestamp)
                df_dot = df_data[df_data['Đợt ĐK'] == dot_dk].sort_values(by='Timestamp').copy()
                df_dot['CumSum_SL'] = pd.to_numeric(df_dot['SL'], errors='coerce').fillna(0).cumsum()
                
                # Lấy số lượng giới hạn của đợt này từ tab Thông số
                limit_row = df_config[df_config['Nội dung option'] == dot_dk]
                max_slot = int(limit_row['SL giới hạn'].values[0]) if not limit_row.empty else 30
                
                # Tìm STT (Cumsum) của user hiện tại
                user_cumsum = df_dot.loc[df_dot['SDT'] == sdt, 'CumSum_SL'].values[0]
                
                if user_cumsum > max_slot:
                    # User nằm trong nhóm lố slot
                    if (user_cumsum - sl_dk) < max_slot:
                        # Điền 1 mình lố giới hạn còn lại
                        st.error(f"Xin lỗi {first_name}, do số lượng bạn đăng ký ({sl_dk} người) đã vượt quá số lượng slot còn lại của đợt này. Bạn vui lòng liên hệ Zalo 0902800318 để được BTC hỗ trợ thêm nha!")
                    else:
                        # Điền cùng lúc bị kẹt ở sau
                        st.error(f"Thành thật xin lỗi {first_name} 😭 Do ở cùng một thời điểm có quá nhiều người cùng gửi form nên đăng ký của bạn được ghi nhận khi đợt trip đã kín chỗ. Hẹn gặp bạn trong đợt tiếp theo nha!")
                else:
                    # NẰM TRONG SLOT HỢP LỆ
                    if status == "HỦY SLOT":
                        st.markdown(f"<div class='cancel-alert'><strong>Xin lỗi đăng ký của {first_name} đã bị HỦY vì quá thời hạn thanh toán mất rồi.</strong></div>", unsafe_allow_html=True)
                        
                    elif status == "ĐANG CẬP NHẬT":
                        st.success(f"🎉 Chúc mừng {first_name} đã đăng ký thành công, thông tin đăng ký của bạn như sau:")
                        st.write(f"**Đợt Đăng ký:** {dot_dk}")
                        st.write(f"**SĐT người đại diện:** {sdt}")
                        st.write(f"**Số lượng đăng ký:** {sl_dk} người")
                        
                        # Bảng DS Người
                        table_html = "<table class='custom-table'><thead><tr><th>Họ và Tên</th><th>Năm sinh</th></tr></thead><tbody>"
                        for ng in ds_nguoi:
                            parts = ng.split('-')
                            t = parts[0].strip() if len(parts)>0 else ""
                            ns = parts[1].strip() if len(parts)>1 else ""
                            table_html += f"<tr><td>{t}</td><td>{ns}</td></tr>"
                        table_html += "</tbody></table>"
                        st.markdown(table_html, unsafe_allow_html=True)
                        
                        # Box Thanh Toán
                        tong_tien = row['Tổng tiền']
                        han_chot = row['Hạn chót CK']
                        tg_con = row['Thời gian còn lại']
                        noidung_ck = f"TRIP - {sdt}"
                        
                        img_tag = f"<img src='data:image/jpeg;base64,{qr_base64}' alt='QR Code'>" if qr_base64 else "Đang cập nhật QR"
                        
                        payment_html = f"""
                        <div class='section-title'>THÔNG TIN THANH TOÁN</div>
                        <div class='payment-box'>
                            <div class='payment-info'>
                                <div class='info-row'><strong>💰 Tổng số tiền:</strong> <span class='highlight-val'>{tong_tien}</span></div>
                                <div class='info-row'><strong>⏳ Hạn chót CK:</strong> <span class='highlight-val'>{han_chot}</span></div>
                                <div class='info-row'><strong>⏱️ Thời gian còn lại:</strong> <span class='highlight-val'>{tg_con}</span></div>
                                <div style='margin-top: 15px;'><strong>NỘI DUNG CHUYỂN KHOẢN:</strong></div>
                                <div style='background-color:#E8F5E9; border:1px solid #2C5E1A; padding:10px; border-radius:5px; font-weight:bold; color:#2C5E1A; font-size:16px; margin-bottom:5px;'>{noidung_ck}</div>
                                <div style='font-size:13px; color:#555;'><i>(Vui lòng chuyển đúng nội dung)</i></div>
                            </div>
                            <div class='payment-qr'>{img_tag}</div>
                        </div>
                        """
                        st.markdown(payment_html, unsafe_allow_html=True)
                        st.warning(f"🔄 Sau khi chuyển khoản xong, chậm nhất {wait_time} phút sau kết quả nhận chuyển khoản sẽ được cập nhật. Bạn làm mới (refresh) trang để xem kết quả nhé.")
                        
                    elif status == "CHỐT ĐƠN THÀNH CÔNG":
                        st.success(f"🎉 Chúc mừng {first_name} đã CHỐT ĐƠN THÀNH CÔNG, hoàn tất việc đăng ký.")
                        st.write("BTC đã nhận được:")
                        st.write(f"- **Số tiền chuyển khoản:** {row['Quang đã nhận']}")
                        st.write(f"- **Số lượng đăng ký:** {sl_dk} người")
                        st.write("BTC xin gửi lại thông tin cần thiết cho chuyến đi, nhà mình nhớ lưu lại hình ảnh nha:")
                        if thongtin_base64:
                            st.markdown(f"<img src='data:image/jpeg;base64,{thongtin_base64}' style='width:100%; border-radius:10px;'>", unsafe_allow_html=True)
                        else:
                            st.info("Đang cập nhật hình ảnh thông tin chuyến đi...")
        else:
            st.error("Không tìm thấy số điện thoại này. Vui lòng kiểm tra lại!")
    else:
        st.warning("Vui lòng nhập số điện thoại.")

# ================= PHẦN 2: ADMIN ONLY =================
st.sidebar.markdown("### ⚙️ FOR ADMIN ONLY")
admin_pass = st.sidebar.text_input("Nhập mật khẩu:", type="password")

if admin_pass == "0519":
    st.sidebar.success("Xác thực thành công!")
    st.markdown("---")
    st.markdown("## KHU VỰC QUẢN TRỊ ADMIN")
    
    admin_tabs = st.tabs(["📊 Thống kê Số Lượng", "💰 Thống kê Chi Phí", "📝 Chỉnh sửa Cấu hình gốc"])
    
    # Lấy list đợt đăng ký có trong sheet Data
    list_dots = df_data['Đợt ĐK'].dropna().unique().tolist()
    
    # TAB A: THỐNG KÊ SỐ LƯỢNG
    with admin_tabs[0]:
        selected_dot_A = st.selectbox("Chọn Đợt để xem thống kê:", ["All"] + list_dots, key="sel_A")
        
        def render_stats_for_dot(dot_name, df_filtered):
            st.markdown(f"<div class='section-title'>{dot_name.upper()}</div>", unsafe_allow_html=True)
            
            # Tính toán
            limit = df_config.loc[df_config['Nội dung option'] == dot_name, 'SL giới hạn'].values
            limit_val = limit[0] if len(limit) > 0 else 0
            
            sl_dang_cap_nhat = df_filtered[df_filtered['Trạng thái CK'] == 'ĐANG CẬP NHẬT']['SL'].apply(pd.to_numeric, errors='coerce').sum()
            sl_chot_don = df_filtered[df_filtered['Trạng thái CK'] == 'CHỐT ĐƠN THÀNH CÔNG']['SL'].apply(pd.to_numeric, errors='coerce').sum()
            sl_huy = df_filtered[df_filtered['Trạng thái CK'] == 'HỦY SLOT']['SL'].apply(pd.to_numeric, errors='coerce').sum()
            sl_tong = sl_dang_cap_nhat + sl_chot_don
            
            # Doanh thu (Xóa text thừa, chuyển thành số)
            def clean_money(x):
                try:
                    return int(''.join(filter(str.isdigit, str(x))))
                except: return 0
                
            dt_dukien = df_filtered[df_filtered['Trạng thái CK'].isin(['ĐANG CẬP NHẬT', 'CHỐT ĐƠN THÀNH CÔNG'])]['Tổng tiền'].apply(clean_money).sum()
            dt_thucte = df_filtered[df_filtered['Trạng thái CK'] == 'CHỐT ĐƠN THÀNH CÔNG']['Quang đã nhận'].apply(clean_money).sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>SỐ LƯỢNG ĐĂNG KÝ</div>
                    <div class='metric-value'>{int(sl_tong)} / {limit_val}</div>
                    <div style='font-size:14px; margin-top:10px;'>
                        🟢 Đang cập nhật: {int(sl_dang_cap_nhat)} <br>
                        ✅ Chốt đơn: {int(sl_chot_don)} <br>
                        ❌ Hủy slot: {int(sl_huy)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>DOANH THU</div>
                    <div class='metric-value'>{dt_thucte:,.0f} đ</div>
                    <div style='font-size:14px; margin-top:10px;'>
                        Dự kiến thu: {dt_dukien:,.0f} đ
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("#### Danh sách khách đã chốt đơn")
            df_chot = df_filtered[df_filtered['Trạng thái CK'] == 'CHỐT ĐƠN THÀNH CÔNG']
            if not df_chot.empty:
                ds_list = []
                for _, r in df_chot.iterrows():
                    for ng in str(r['DS người']).split(','):
                        parts = ng.split('-')
                        ds_list.append({"Tên": parts[0].strip() if len(parts)>0 else "", "Năm sinh": parts[1].strip() if len(parts)>1 else ""})
                st.dataframe(pd.DataFrame(ds_list), use_container_width=True)
            else:
                st.info("Chưa có khách hàng chốt đơn thành công.")
                
        if selected_dot_A == "All":
            for d in list_dots:
                render_stats_for_dot(d, df_data[df_data['Đợt ĐK'] == d])
        else:
            render_stats_for_dot(selected_dot_A, df_data[df_data['Đợt ĐK'] == selected_dot_A])

    # TAB B: THỐNG KÊ CHI PHÍ
    with admin_tabs[1]:
        selected_dot_B = st.selectbox("Chọn Đợt tính chi phí:", list_dots, key="sel_B")
        
        # Đếm số khách chốt đơn của đợt này
        df_dot_B = df_data[(df_data['Đợt ĐK'] == selected_dot_B) & (df_data['Trạng thái CK'] == 'CHỐT ĐƠN THÀNH CÔNG')]
        khach_chot_don = df_dot_B['SL'].apply(pd.to_numeric, errors='coerce').sum()
        khach_chot_don = int(khach_chot_don) if pd.notna(khach_chot_don) else 0
        
        st.write(f"**Tổng số người (CHỐT ĐƠN THÀNH CÔNG):** {khach_chot_don} người")
        
        # Lấy data chi phí từ tab Thông số
        df_cp = df_config[['Chi phí tổ chức', 'Unit cost', 'Loại chi phí']].dropna(subset=['Chi phí tổ chức'])
        df_cp = df_cp[df_cp['Chi phí tổ chức'] != '']
        
        list_dropdowns = df_cp[df_cp['Loại chi phí'] == 'Dropdown']['Chi phí tổ chức'].tolist()
        selected_opts = st.multiselect("Chọn các hạng mục phát sinh (Dropdown):", list_dropdowns)
        
        cost_data = []
        total_cost = 0
        
        for _, r in df_cp.iterrows():
            ten_cp = r['Chi phí tổ chức']
            u_cost = pd.to_numeric(r['Unit cost'], errors='coerce')
            if pd.isna(u_cost): u_cost = 0
            l_cp = r['Loại chi phí']
            
            if l_cp == "Cố định":
                sl = 1
                thanh_tien = u_cost * sl
                cost_data.append([ten_cp, f"{u_cost:,.0f}", sl, f"{thanh_tien:,.0f}"])
                total_cost += thanh_tien
            elif l_cp == "Theo đầu người":
                sl = khach_chot_don
                thanh_tien = u_cost * sl
                cost_data.append([ten_cp, f"{u_cost:,.0f}", sl, f"{thanh_tien:,.0f}"])
                total_cost += thanh_tien
            elif l_cp == "Dropdown" and ten_cp in selected_opts:
                sl = 1
                thanh_tien = u_cost * sl
                cost_data.append([ten_cp, f"{u_cost:,.0f}", sl, f"{thanh_tien:,.0f}"])
                total_cost += thanh_tien
                
        cost_data.append(["**TỔNG CỘNG**", "", "", f"**{total_cost:,.0f}**"])
        df_cost_display = pd.DataFrame(cost_data, columns=["Chi phí", "Unit Cost", "Số lượng", "Thành tiền (VNĐ)"])
        
        st.markdown("<div class='section-title'>BẢNG DỰ TOÁN CHI PHÍ</div>", unsafe_allow_html=True)
        st.markdown(df_cost_display.to_html(escape=False, index=False, classes='custom-table'), unsafe_allow_html=True)

    # TAB C: CHỈNH SỬA GỐC
    with admin_tabs[2]:
        st.warning("⚠️ Mọi thay đổi ở đây sẽ ghi đè trực tiếp lên tab 'Thông số' của Google Sheet.")
        
        # Copy df để update
        df_update = df_config.copy()
        
        with st.form("update_config_form"):
            st.markdown("### 1. Cụm Scheme vé")
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1: ve = st.number_input("Vé 1 người", value=float(df_update.loc[0, 'Vé 1 người']) if pd.notna(df_update.loc[0, 'Vé 1 người']) else 0)
            with col_v2: sl_km = st.number_input("SL khuyến mãi", value=float(df_update.loc[0, 'SL khuyến mãi']) if pd.notna(df_update.loc[0, 'SL khuyến mãi']) else 0)
            with col_v3: km = st.number_input("Scheme khuyến mãi", value=float(df_update.loc[0, 'Scheme khuyến mãi']) if pd.notna(df_update.loc[0, 'Scheme khuyến mãi']) else 0)
            
            st.markdown("### 2. Cụm Thời gian")
            col_t1, col_t2 = st.columns(2)
            with col_t1: tg_ck = st.number_input("Thời gian CK (phút)", value=float(df_update.loc[0, 'Thời gian CK']) if pd.notna(df_update.loc[0, 'Thời gian CK']) else 0)
            with col_t2: tg_check = st.number_input("Thời gian Check (phút)", value=float(df_update.loc[0, 'Thời gian Check']) if pd.notna(df_update.loc[0, 'Thời gian Check']) else 0)
            
            st.markdown("### 3. Cụm Số lượng giới hạn (2 Đợt)")
            col_d1, col_d2 = st.columns(2)
            # Lấy data hiện tại
            d1_name = df_update.loc[0, 'Nội dung option'] if len(df_update) > 0 and pd.notna(df_update.loc[0, 'Nội dung option']) else ""
            d1_limit = float(df_update.loc[0, 'SL giới hạn']) if len(df_update) > 0 and pd.notna(df_update.loc[0, 'SL giới hạn']) else 30
            d2_name = df_update.loc[1, 'Nội dung option'] if len(df_update) > 1 and pd.notna(df_update.loc[1, 'Nội dung option']) else ""
            d2_limit = float(df_update.loc[1, 'SL giới hạn']) if len(df_update) > 1 and pd.notna(df_update.loc[1, 'SL giới hạn']) else 30
            
            with col_d1: opt1 = st.text_input("Tên đợt 1", value=str(d1_name))
            with col_d2: lim1 = st.number_input("SL đợt 1", value=d1_limit)
            with col_d1: opt2 = st.text_input("Tên đợt 2", value=str(d2_name))
            with col_d2: lim2 = st.number_input("SL đợt 2", value=d2_limit)
            
            st.markdown("### 4. Cụm Chi phí tổ chức")
            st.caption("Chỉnh sửa trực tiếp trên bảng bên dưới (Có thể click đúp vào ô để gõ)")
            
            cp_cols = ['Chi phí tổ chức', 'Unit cost', 'Loại chi phí']
            # Đảm bảo dataframe có đủ các cột để hiển thị data editor
            if 'Loại chi phí' not in df_update.columns:
                df_update['Loại chi phí'] = ""
                
            df_cp_edit = df_update[cp_cols].copy().dropna(how='all')
            # Fix số dòng trống để admin có thể add thêm
            if len(df_cp_edit) < 10: 
                extra_rows = pd.DataFrame([["", 0, "Cố định"]]*5, columns=cp_cols)
                df_cp_edit = pd.concat([df_cp_edit, extra_rows], ignore_index=True)
                
            edited_cp = st.data_editor(
                df_cp_edit, 
                column_config={
                    "Loại chi phí": st.column_config.SelectboxColumn(
                        "Loại chi phí", options=["Cố định", "Theo đầu người", "Dropdown"], required=True
                    )
                },
                num_rows="dynamic",
                use_container_width=True
            )
            
            submitted = st.form_submit_button("LƯU THAY ĐỔI LÊN GOOGLE SHEET 💾")
            if submitted:
                # Gán lại cụm Vé
                df_update.loc[0, 'Vé 1 người'] = ve
                df_update.loc[0, 'SL khuyến mãi'] = sl_km
                df_update.loc[0, 'Scheme khuyến mãi'] = km
                
                # Gán lại thời gian
                df_update.loc[0, 'Thời gian CK'] = tg_ck
                df_update.loc[0, 'Thời gian Check'] = tg_check
                
                # Gán lại Đợt
                df_update.loc[0, 'Nội dung option'] = opt1
                df_update.loc[0, 'SL giới hạn'] = lim1
                df_update.loc[1, 'Nội dung option'] = opt2
                df_update.loc[1, 'SL giới hạn'] = lim2
                
                # Cập nhật cụm chi phí
                # Reset lại toàn bộ cột K, L, M
                df_update['Chi phí tổ chức'] = None
                df_update['Unit cost'] = None
                df_update['Loại chi phí'] = None
                
                for i, r in edited_cp.iterrows():
                    if pd.notna(r['Chi phí tổ chức']) and str(r['Chi phí tổ chức']).strip() != "":
                        df_update.loc[i, 'Chi phí tổ chức'] = r['Chi phí tổ chức']
                        df_update.loc[i, 'Unit cost'] = r['Unit cost']
                        df_update.loc[i, 'Loại chi phí'] = r['Loại chi phí']
                
                try:
                    conn.update(worksheet="Thông số", data=df_update)
                    st.success("✅ Đã cập nhật dữ liệu thành công lên Google Sheet! Hãy làm mới trang để thấy thay đổi.")
                    st.cache_data.clear() # Clear cache để app đọc lại data mới nhất
                except Exception as e:
                    st.error(f"Lỗi khi cập nhật lên Google Sheet: {e}. Bạn vui lòng kiểm tra lại quyền truy cập (File secrets.toml đã cấp quyền Editor chưa?)")
