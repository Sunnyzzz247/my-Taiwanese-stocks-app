import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox
from datetime import timedelta
st.title("Hi,there!")
st.write("這是一個簡單的股票查詢系統，歡迎來到這裡！")

# 側邊控制欄
st.sidebar.title("控制面板")
option = st.sidebar.selectbox("選擇一個選項：", ["首頁", "選項2", "選項3"])
st.write(f"目前頁面為{option}")

#----------------------------分欄佈局------------------------#
col1, col2 = st.columns(2)
with col1:
    stock = None
    data = None
    #-----------------------------搜尋功能------------------------#

    # 讀取 CSV
    df = pd.read_csv("stockmarket.csv")

    # 搜尋函式
    def search_function(searchterm: str):

        if not searchterm:
            return []  # 如果搜尋詞為空，回傳空列表 

        # 模糊搜尋
        result = df[
            df["公司名稱"].astype(str).str.contains(searchterm, case=False)
            |
            df["公司簡稱"].astype(str).str.contains(searchterm, case=False)
            |
            df["公司代號"].astype(str).str.contains(searchterm)
        ]

        # 回傳選項列表
        return (
            result["公司名稱"]
            + " ("
            + result["公司代號"].astype(str)
            + ")"
        ).tolist()


    # 搜尋框
    selected_value = st_searchbox(
        search_function,
        placeholder="輸入公司名稱或代號"
    )

    
    if selected_value:
        code = selected_value.split("(")[1].replace(")", "")
        ticker = code + ".TW"

    #-----------------------------搜尋功能------------------------#
    if selected_value:
        stock=yf.Ticker(ticker)
    
    search_way=st.selectbox("請選擇查詢方式:", ["快速查詢", "自定義查詢"])
    st.write("\n")

    if search_way=="快速查詢" and selected_value:
        st.write("___快速查詢___")
        time = st.selectbox("請選擇近期時間段:", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
        data= stock.history(period=time, auto_adjust=True)
        
    elif search_way=="自定義查詢" and selected_value:
        st.write("___自定義查詢___")
        start = st.date_input("開始日期:")
        end = st.date_input("結束日期:")
        data= stock.history(start=start, end=end+timedelta(days=1), auto_adjust=True)
        if data.empty:
            st.warning("此區間無交易資料，可能是假日，請重新選擇日期！")
        if start > end:
            st.warning("開始日期不能晚於結束日期，請重新選擇日期！")
    #按鈕       
    buttom=st.button("查詢")


with col2:
#---------------------------------修改資料格式---------------------------------#
    if data is not None:
        data = data.reset_index() 
        # 1.將日期從索引轉換為普通列，用新的dataframe覆蓋舊的
        # 2.第二種寫法:data.reset_index(replace=True)
        data = data.rename(columns={"Date": "日期", "Open": "開盤價", "High": "最高價", "Low": "最低價", "Close": "收盤價", "Volume": "成交量"})
        data = data[["日期", "開盤價", "最高價", "最低價", "收盤價", "成交量"]]
        # 1.重新排列"列"的順序(也可在上面那行直接排序)
        # 2.選擇要顯示的列，其他列會被刪除
        st.dataframe(data,hide_index=True) #隱藏索引列
#---------------------------------修改資料格式---------------------------------#  
    # 按鈕指令
    if buttom and stock:
        st.write(selected_value)
        st.write(data)
    elif buttom and (stock is None):
        st.write("請輸入股票代碼！")
#----------------------------分欄佈局------------------------#
