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

# Hàm format tiền VNĐ (VD: 1500000 -> 1.500.000 VNĐ)
def format_vnd(amount):
    try:
        clean_amount = ''.join(filter(str.isdigit, str(amount)))
        if not clean_amount: return "0 VNĐ"
        return f"{int(clean_amount):,}".replace(',', '.') + " VNĐ"
    except:
        return str(amount)

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    h1, h2, h3, h4, .stTabs [data-baseweb="tab"] p { color: #2C5E1A !important; font-weight: bold; }
    
    .stButton>button { background-color: #D4AF37; color: #1A3C0F; font-weight: bold; border-radius: 8px; border: none; width: 100%; padding: 10px; }
    .stButton>button:hover { background-color: #2C5E1A; color: #FFFFFF; border: none; }
    .stTextInput>div>div>input { background-color: #F8F9FA; color: #333333; border: 1px solid #2C5E1A; border-radius: 5px; font-size: 16px; font-weight: bold;}
    
    /* Giao diện Bảng */
    .section-title { background: linear-gradient(90deg, #2C5E1A 0%, #D4AF37 100%); color: white; padding: 12px 15px; border-radius: 8px 8px 0 0; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .custom-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 20px; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); overflow: hidden; }
    .custom-table thead tr { background-color: #1A3C0F; } 
    .custom-table th { color: white; padding: 12px 14px; text-align: center; font-size: 15px; border: none; }
    .custom-table td { padding: 14px; border-bottom: 1px solid #EEEEEE; border-right: 1px solid #EEEEEE; text-align: center; font-weight: bold; color: #2C5E1A; background-color: #FFFFFF;}
    
    /* Box Thanh toán */
    .payment-box { display: flex; flex-wrap: wrap; border: 1px solid #E0E6ED; border-top: none; border-radius: 0 0 8px 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); background-color: #FAFAFA; margin-bottom: 25px; }
    .payment-info { flex: 1.3; min-width: 250px; padding-right: 15px; }
    .payment-qr { flex: 1; min-width: 200px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    
    .highlight-val { color: #D4AF37; font-weight: bold; font-size: 16px;} 
    .info-row { margin-bottom: 15px; font-size: 15px; border-bottom: 1px dashed #EEEEEE; padding-bottom: 10px;}
    
    .cancel-alert { background-color: #F8D7DA; color: #721C24; padding: 20px; border-radius: 8px; border: 1px solid #F5C6CB; margin-bottom: 20px; text-align: center; line-height: 1.6; }
    
    /* Box thông tin đăng ký (Gradient) */
    .info-card { background: linear-gradient(135deg, #F9FBE7 0%, #FFFDE7 100%); padding: 20px; border-left: 6px solid #2C5E1A; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .info-card p { margin-bottom: 8px; font-size: 16px; }
    .info-card strong { color: #2C5E1A; }
    .info-card span { color: #D4AF37; font-weight: bold; font-size: 17px;}
    </style>
""", unsafe_allow_html=True)

# Lấy data
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    df_data = conn.read(spreadsheet=url, worksheet="Data App")
    df_config = conn.read(spreadsheet=url, worksheet="Thông số")
    df_data['SDT'] = df_data['SDT'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df_data, df_config

try:
    df_data, df_config = load_data()
except Exception as e:
    st.error(f"Lỗi kết nối dữ liệu: {e}")
    st.stop()

try:
    time_ck = int(df_config.iloc[0]['Thời gian CK']) if not pd.isna(df_config.iloc[0]['Thời gian CK']) else 0
    time_check = int(df_config.iloc[0]['Thời gian Check']) if not pd.isna(df_config.iloc[0]['Thời gian Check']) else 0
    wait_time = time_ck + time_check
except:
    wait_time = 15

# ================= PHẦN 1: USER - KẾT QUẢ ĐĂNG KÝ =================
st.markdown("<h1 style='text-align: center;'>KẾT QUẢ ĐĂNG KÝ <br> TRIP ĐÊM HUYỀN BÍ</h1>", unsafe_allow_html=True)

# Label số điện thoại in hoa, bôi đậm, có màu
st.markdown("<p style='color: #2C5E1A; font-weight: 900; font-size: 16px; text-transform: uppercase; margin-bottom: 5px;'>NHẬP SỐ ĐIỆN THOẠI CỦA BẠN (ĐÃ DÙNG ĐĂNG KÝ):</p>", unsafe_allow_html=True)
phone_input = st.text_input("SDT", label_visibility="collapsed", placeholder="Ví dụ: 0901234567")

if st.button("TRA CỨU KẾT QUẢ 🚀"):
    if phone_input:
        clean_input = phone_input.strip().lstrip('0')
        df_data['Phone_Compare'] = df_data['SDT'].str.lstrip('0')
        matched_rows = df_data[df_data['Phone_Compare'] == clean_input]
        
        if not matched_rows.empty:
            for idx, row in matched_rows.iterrows():
                dot_dk = row['Đợt ĐK']
                # Xử lý bù số 0 ở đầu SĐT nếu bị mất
                sdt = row['SDT']
                sdt_display = f"0{str(sdt).lstrip('0')}"
                
                status = str(row['Trạng thái CK']).strip().upper()
                sl_dk = int(row['SL']) if pd.notna(row['SL']) else 1
                
                ds_nguoi = str(row['DS người']).split(',')
                first_name = ds_nguoi[0].split('-')[0].strip() if ds_nguoi else "Bạn"
                
                # Tính lố slot
                df_dot = df_data[df_data['Đợt ĐK'] == dot_dk].sort_values(by='Timestamp').copy()
                df_dot['CumSum_SL'] = pd.to_numeric(df_dot['SL'], errors='coerce').fillna(0).cumsum()
                
                limit_row = df_config[df_config['Nội dung option'] == dot_dk]
                max_slot = int(limit_row['SL giới hạn'].values[0]) if not limit_row.empty else 30
                
                user_cumsum = df_dot.loc[df_dot['SDT'] == sdt, 'CumSum_SL'].values[0]
                
                if user_cumsum > max_slot:
                    if (user_cumsum - sl_dk) < max_slot:
                        st.error(f"Xin lỗi {first_name}, do số lượng bạn đăng ký ({sl_dk} người) đã vượt quá số lượng slot còn lại của đợt này. Bạn vui lòng liên hệ Zalo 0902800318 để được BTC hỗ trợ thêm nha!")
                    else:
                        st.error(f"Thành thật xin lỗi {first_name} 😭 Do ở cùng một thời điểm có quá nhiều người cùng gửi form nên đăng ký của bạn được ghi nhận khi đợt trip đã kín chỗ. Hẹn gặp bạn trong đợt tiếp theo nha!")
                else:
                    # Giao diện Box Thông tin đăng ký (Dùng chung cho Đang Cập Nhật & Chốt Đơn)
                    info_card_html = f"""
                    <div class='info-card'>
                        <p><strong>Đợt Đăng ký:</strong> <span>{dot_dk}</span></p>
                        <p><strong>SĐT người đại diện:</strong> <span>{sdt_display}</span></p>
                        <p style='margin-bottom:0;'><strong>Số lượng đăng ký:</strong> <span>{sl_dk} người</span></p>
                    </div>
                    """
                    
                    if status == "HỦY SLOT":
                        st.markdown(f"<div class='cancel-alert'><strong>Xin lỗi đăng ký của {first_name} đã bị HỦY vì quá thời hạn thanh toán mất rồi.</strong></div>", unsafe_allow_html=True)
                        
                    elif status == "ĐANG CẬP NHẬT":
                        st.success(f"🎉 Chúc mừng {first_name} đã đăng ký thành công, thông tin đăng ký của bạn như sau:")
                        st.markdown(info_card_html, unsafe_allow_html=True)
                        
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
                        tong_tien = format_vnd(row['Tổng tiền'])
                        han_chot = row['Hạn chót CK']
                        tg_con = row['Thời gian còn lại']
                        noidung_ck = f"TRIP - {sdt_display}"
                        
                        img_tag = f"<img src='data:image/jpeg;base64,{qr_base64}' alt='QR Code'>" if qr_base64 else "Đang cập nhật QR"
                        
                        st.markdown("<div class='section-title'>THÔNG TIN THANH TOÁN</div>", unsafe_allow_html=True)
                        st.markdown("<div class='payment-box'><div class='payment-info'>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='info-row'><strong>💰 Tổng số tiền:</strong> <span class='highlight-val'>{tong_tien}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='info-row'><strong>⏳ Hạn chót CK:</strong> <span class='highlight-val'>{han_chot}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='info-row'><strong>⏱️ Thời gian còn lại:</strong> <span class='highlight-val'>{tg_con}</span></div>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2C5E1A; margin-bottom: 5px;'>THÔNG TIN CHUYỂN KHOẢN:</div>", unsafe_allow_html=True)
                        st.markdown("<div style='font-size: 15px; margin-bottom: 5px;'>Tô Văn Quang - Vietcombank<br>STK:</div>", unsafe_allow_html=True)
                        # Nút copy cho STK
                        st.code("0251001799405", language=None)
                        
                        st.markdown("<div style='margin-top: 10px; font-weight: bold; color: #2C5E1A; margin-bottom: 5px;'>NỘI DUNG CHUYỂN KHOẢN:</div>", unsafe_allow_html=True)
                        # Nút copy cho Nội dung
                        st.code(noidung_ck, language=None)
                        
                        st.markdown("<div style='margin-top: 10px; text-align: center;'><span style='color: red; font-weight: bold; font-size: 16px;'>⚠️ Vui lòng chuyển đúng nội dung</span></div>", unsafe_allow_html=True)
                        
                        st.markdown("</div><div class='payment-qr'>" + img_tag + "</div></div>", unsafe_allow_html=True)
                        
                        st.warning(f"🔄 Sau khi chuyển khoản xong, chậm nhất {wait_time} phút sau kết quả nhận chuyển khoản sẽ được cập nhật. Bạn làm mới (refresh) trang để xem kết quả nhé.")
                        
                    elif status == "CHỐT ĐƠN THÀNH CÔNG":
                        st.success(f"🎉 Chúc mừng {first_name} đã CHỐT ĐƠN THÀNH CÔNG, hoàn tất việc đăng ký.")
                        
                        # Áp dụng box gradient sang trọng cho phần chốt đơn
                        st.markdown(info_card_html, unsafe_allow_html=True)
                        
                        # Box xác nhận tiền (Highlight đẹp)
                        st.markdown(f"""
                        <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; border: 1px solid #A5D6A7; margin-bottom: 20px;'>
                            <p style='margin: 0; color: #2E7D32; font-size: 15px;'>✅ BTC đã nhận được thanh toán:</p>
                            <p style='margin: 5px 0 0 0; font-size: 18px; color: #1B5E20;'><strong>Số tiền chuyển khoản:</strong> <span style='color: #D4AF37;'>{format_vnd(row['Tổng tiền'])}</span></p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Highlight text kêu gọi lưu hình
                        st.markdown(f"""
                        <div style='text-align: center; margin: 25px 0 15px 0; padding: 10px; border-top: 2px dashed #2C5E1A; border-bottom: 2px dashed #2C5E1A;'>
                            <h4 style='color: #2C5E1A; margin: 0; font-size: 17px;'>🌿 BTC xin gửi lại thông tin cần thiết cho chuyến đi 🌿</h4>
                            <p style='color: #D4AF37; font-weight: bold; margin-top: 5px; font-size: 15px;'>Nhà mình nhớ lưu lại hình ảnh nha!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if thongtin_base64:
                            st.markdown(f"<img src='data:image/jpeg;base64,{thongtin_base64}' style='width:100%; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                        else:
                            st.info("Đang cập nhật hình ảnh thông tin chuyến đi...")
        else:
            st.error("Không tìm thấy số điện thoại này. Vui lòng kiểm tra lại!")

# (Giữ nguyên PHẦN 2: ADMIN ONLY y như code cũ tui đã gửi nhé, không cần sửa gì)
