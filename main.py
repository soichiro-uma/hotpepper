import hotpepper
import streamlit as st

print("OK")
st.title("シミュレーション結果")
st.sidebar.title("データを入力してください")

#インプットパラメータ
count = st.sidebar.selectbox(
    '何軒分表示しますか？',
    list(range(1,11)))
keyword = '心斎橋駅'
# keyword = st.text_input("どの駅周辺を調べますか？")
turnover_rate = 2
business_days = 23
hourly_wage = 1000
employee = st.sidebar.slider("従業員数は何人ですか？",0,30,5)
rent = 200000
other = 100000



result = hotpepper.hotpepper(count,keyword,turnover_rate,business_days,hourly_wage,employee,rent,other)
st.dataframe(result.style.highlight_max(axis=0))