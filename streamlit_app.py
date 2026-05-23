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


col1, col2 = st.columns(2) #分欄佈局

with col1:  #左側欄位
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
            df["公司名稱"].astype(str).str.contains(searchterm, case=False, regex=False)
            |
            df["公司簡稱"].astype(str).str.contains(searchterm, case=False, regex=False)
            |
            df["公司代號"].astype(str).str.contains(searchterm, regex=False)
        ]

        # 回傳選項列表
        return (
            result["公司名稱"]
            + " ("
            + result["公司代號"].astype(str)
            + ")"
        ).tolist()

    try:
    # 搜尋框
        selected_value = st_searchbox(
            search_function,
            placeholder="輸入公司名稱或代號"
        )
    except NameError:
        st.warning("請重新輸入數字或文字！")

    
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
        time = st.selectbox("請選擇近期時間段:", ["一天", "五天", "一個月", "三個月", "六個月", "一年", "兩年", "五年", "十年", "今年以來", "全部資料"])
        if time:
            key=["一天", "五天", "一個月", "三個月", "六個月", "一年", "兩年", "五年", "十年", "今年以來", "全部資料"]
            value=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
            time_dict = dict(zip(key, value))
        
    elif search_way=="自定義查詢" and selected_value:
        st.write("___自定義查詢___")
        start = st.date_input("開始日期:")
        end = st.date_input("結束日期:")
    #按鈕       
    buttom=st.button("查詢")


with col2:  #右側欄位
#--------------------------------------按鈕指令---------------------------------------#
    if search_way=="快速查詢" and stock and buttom:
        st.write(selected_value)
        data= stock.history(period=time_dict[time], auto_adjust=True)
        #---------------------------------修改資料格式---------------------------------#
        if data is not None:
            data = data.reset_index() 
            # 1.將日期從索引轉換為普通列，用新的dataframe覆蓋舊的
            # 2.第二種寫法:data.reset_index(replace=True)
            data = data.rename(columns={"Date": "日期", "Open": "開盤價", "High": "最高價", "Low": "最低價", "Close": "收盤價", "Volume": "成交量(千股)"})
            data = data[["日期", "開盤價", "最高價", "最低價", "收盤價", "成交量(千股)"]]
            # 1.重新排列"列"的順序(也可在上面那行直接排序)
            # 2.選擇要顯示的列，其他列會被刪除
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime("%Y-%m-%d") #將日期格式轉換為"年-月-日"
            data["成交量(千股)"] //= 1000 #將成交量單位轉換為千股
            st.dataframe(data,hide_index=True) #隱藏索引列
        #---------------------------------修改資料格式---------------------------------#  

    elif search_way=="自定義查詢" and stock and buttom:
        st.write(selected_value)
        data= stock.history(start=start, end=end+timedelta(days=1), auto_adjust=True) 

        if data.empty:
            st.warning("此區間無交易資料，可能是假日，請重新選擇日期！")
        elif start > end:
            st.warning("開始日期不能晚於結束日期，請重新選擇日期！")
        else:
        #---------------------------------修改資料格式---------------------------------#
            if data is not None:
                data = data.reset_index() 
                data = data.rename(columns={"Date": "日期", "Open": "開盤價", "High": "最高價", "Low": "最低價", "Close": "收盤價", "Volume": "成交量(千股)"})
                data = data[["日期", "開盤價", "最高價", "最低價", "收盤價", "成交量(千股)"]]
                data["日期"] = pd.to_datetime(data["日期"]).dt.strftime("%Y-%m-%d") 
                data["成交量(千股)"] //= 1000
                st.dataframe(data,hide_index=True) 
        #---------------------------------修改資料格式---------------------------------#  
            
    elif buttom and stock is None:
        st.warning("請輸入股票代碼！")
#--------------------------------------按鈕指令---------------------------------------#
