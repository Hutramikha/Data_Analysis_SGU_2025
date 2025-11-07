import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Load dữ liệu từ file Excel ---
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, skiprows=5) 
    df.rename(columns={
        "NGÀY": "date",
        "GIÁ MỞ CỬA": "open",
        "GIÁ CAO NHẤT": "high",
        "GIÁ THẤP NHẤT": "low",
        "GIÁ ĐÓNG CỬA": "close",
        "KHỐI LƯỢNG": "volume",
        "THAY ĐỔI GIÁ": "price_change",
        "% THAY ĐỔI": "percent_change"
    }, inplace=True)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    df = df.sort_values("date")
    df["SMA_50"] = df["close"].rolling(window=50).mean()
    return df

# --- Monte Carlo Simulation ---
def monte_carlo_simulation(df, n=200, t=30):
    last_price = df["close"].iloc[-1]
    returns = df["close"].pct_change().dropna()
    mu, sigma = returns.mean(), returns.std()
    simulations = np.zeros((n, t))
    for i in range(n):
        simulations[i] = last_price * np.cumprod(1 + np.random.normal(mu, sigma, t))
    return simulations

# --- Giao diện Streamlit ---
st.set_page_config(page_title="VN-INDEX 30 Dashboard", layout="wide")
st.title("📈 Financial Dashboard - VN-INDEX 30")

file = st.sidebar.file_uploader("📂 Tải lên file Excel dữ liệu VN30", type=["xlsx"])
if file:
    df = load_data(file)

    # --- Sidebar chọn khoảng thời gian ---
    start_date = st.sidebar.date_input("Từ ngày", value=df["date"].min())
    end_date = st.sidebar.date_input("Đến ngày", value=df["date"].max())
    filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

    # --- Chọn tab hiển thị ---
    tab = st.sidebar.radio("Chọn tab", ["Summary", "Chart", "Statistics", "Monte Carlo Simulation"])

    # --- Tab 1: Summary ---
    if tab == "Summary":
        st.subheader("📊 Tổng quan VN30")
        latest = filtered_df.iloc[-1]
        previous = filtered_df.iloc[-2]
        col1, col2, col3 = st.columns(3)
        col1.metric("Giá đóng cửa", f"{latest['close']:.2f}", f"{latest['close'] - previous['close']:.2f}")
        col2.metric("Khối lượng", f"{latest['volume']:.0f}")
        col3.metric("Thay đổi giá", f"{latest['price_change']:.2f} ({latest['percent_change']:.2f}%)")

        st.write("📅 Dữ liệu gần nhất:")
        st.dataframe(filtered_df.tail(5))

    # --- Tab 2: Chart ---
    elif tab == "Chart":
        st.subheader("📈 Biểu đồ giá VN30")
        chart_type = st.selectbox("Chọn loại biểu đồ", ["Line", "Candlestick"])
        fig = go.Figure()

        if chart_type == "Line":
            fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["close"], mode="lines", name="Close"))
            fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["SMA_50"], mode="lines", name="SMA 50"))
        else:
            fig.add_trace(go.Candlestick(
                x=filtered_df["date"],
                open=filtered_df["open"],
                high=filtered_df["high"],
                low=filtered_df["low"],
                close=filtered_df["close"],
                name="Candlestick"
            ))
            fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["SMA_50"], mode="lines", name="SMA 50"))

        fig.update_layout(xaxis_title="Ngày", yaxis_title="Giá", height=600)
        st.plotly_chart(fig, use_container_width=True)

    # --- Tab 3: Statistics ---
    elif tab == "Statistics":
        st.subheader("📊 Thống kê VN30")
        col1, col2, col3 = st.columns(3)
        col1.metric("Giá cao nhất", f"{filtered_df['high'].max():.2f}")
        col2.metric("Giá thấp nhất", f"{filtered_df['low'].min():.2f}")
        col3.metric("Biến động (std)", f"{filtered_df['close'].std():.2f}")

        st.write("📈 Tỷ suất sinh lời:")
        returns = filtered_df["close"].pct_change().dropna()
        st.line_chart(returns)

    # --- Tab 4: Monte Carlo Simulation ---
    elif tab == "Monte Carlo Simulation":
        st.subheader("🎲 Mô phỏng giá VN30 trong 30 ngày tới")
        simulations = monte_carlo_simulation(filtered_df)
        for i in range(min(10, simulations.shape[0])):
            st.line_chart(simulations[i])

        ending_prices = simulations[:, -1]
        VaR_95 = np.percentile(ending_prices, 5)
        st.write(f"📉 Value at Risk (VaR) ở mức 95%: **{filtered_df['close'].iloc[-1] - VaR_95:.2f} điểm**")
        st.write("🔚 Phân phối giá kết thúc:")
        st.bar_chart(pd.Series(ending_prices).value_counts().sort_index())

else:
    st.warning("Vui lòng tải lên file Excel dữ liệu VN30 để bắt đầu.")
