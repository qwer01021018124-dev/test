import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 🔌 구글 시트 연동 로직 셋업
# ==========================================
@st.cache_resource # 매번 로그인하지 않도록 캐싱
def init_connection():
    # Streamlit Secrets에서 인증 정보 가져오기
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scopes
    )
    client = gspread.authorize(creds)
    return client

# 클라이언트 연결 및 시트 불러오기 (시트 URL 또는 이름 사용)
client = init_connection()
# 연결할 구글 시트의 링크를 secrets.toml에 넣어두고 불러옵니다.
SHEET_URL = st.secrets["spreadsheet"]["url"] 
sheet = client.open_by_url(SHEET_URL).sheet1 # 첫 번째 워크시트 선택

# ==========================================
# 📱 웹페이지 UI 및 비즈니스 로직
# ==========================================
st.set_page_config(page_title="내 손안의 가계부", layout="centered")

st.title("💰 나만의 쓱싹 가계부")
st.markdown("스마트폰과 PC에서 언제든 기록하세요!")
st.divider()

# --- 수입/지출 입력 칸 ---
st.subheader("📝 새로운 내역 입력")

with st.form("money_form", clear_on_submit=True): # 제출 후 폼 초기화 옵션 추가
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("날짜", date.today())
        type_input = st.radio("구분", ["지출 💸", "수입 💰"], horizontal=True)
    with col2:
        category_input = st.selectbox("카테고리", ["식비", "교통비", "쇼핑", "문화생활", "월급", "기타"])
        amount_input = st.number_input("금액 (원)", min_value=0, step=1000)
    
    memo_input = st.text_input("상세 내용 (예: 점심 국밥)")
    
    submitted = st.form_submit_button("가계부에 기록하기")

# 버튼이 눌렸을 때 -> 구글 시트로 데이터 쏘기 (Write)
if submitted:
    with st.spinner('구글 시트에 기록 중입니다...'):
        # 시트에 한 줄 추가 (append_row)
        new_row = [str(date_input), type_input, category_input, amount_input, memo_input]
        sheet.append_row(new_row)
        
    st.success(f"✅ {date_input} / {category_input} / {amount_input:,}원 기록이 완료되었습니다!")

st.divider()

# --- 구글 시트에서 데이터 불러와서 보여주기 (Read) ---
st.subheader("📊 내역 확인하기")

# 시트에 있는 모든 데이터 가져오기
data = sheet.get_all_records()

if data:
    # 데이터가 있으면 판다스 데이터프레임으로 변환해서 표출
    df = pd.DataFrame(data)
    # 최신 데이터가 위로 오게 정렬 (옵션)
    df = df.sort_values(by="날짜", ascending=False).reset_index(drop=True)
    st.dataframe(df, use_container_width=True)
else:
    st.info("아직 기록된 내역이 없습니다. 첫 지출을 기록해 보세요!")