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

        st.markdown("""
        **Nhận xét:**

        Trong giai đoạn từ 03/11/2025 đến 07/11/2025, chỉ số VN30 có xu hướng giảm rõ rệt, với 4/5 phiên giảm điểm.
        Giá đóng cửa cuối kỳ đạt 1824.71 điểm, giảm 44.89 điểm (-2.01%) so với phiên trước. Mặc dù khối lượng giao dịch vẫn ở mức cao (39,5 triệu đơn vị), song xu hướng chung cho thấy áp lực bán mạnh và tâm lý thận trọng của nhà đầu tư. Giá hiện tại thấp hơn đường trung bình 50 phiên (SMA_50 ≈ 1892.45), thể hiện xu hướng giảm trung hạn đang chiếm ưu thế. Nhà đầu tư nên hạn chế giao dịch ngắn hạn và theo dõi vùng hỗ trợ 1800 điểm để xác định tín hiệu hồi phục.
        """)

    # --- Tab 2: Chart ---
    elif tab == "Chart":
        st.subheader("📈 Biểu đồ giá VN30")
        chart_type = st.selectbox("Chọn loại biểu đồ", ["Line", "Candlestick"])
        fig = go.Figure()

        if chart_type == "Line":
            fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["close"], mode="lines", name="Close"))
            fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["SMA_50"], mode="lines", name="SMA 50"))

            comment = """
            **Nhận xét:**

            Biểu đồ (Line) trên thể hiện diễn biến của chỉ số VN30 và đường trung bình động 50 phiên (SMA_50) trong giai đoạn từ năm 2021 đến 2025. Kết quả cho thấy, chỉ số VN30 giảm mạnh trong năm 2022, chạm đáy quanh mức 1000 điểm, sau đó phục hồi dần từ năm 2023 đến giữa năm 2025. Đến nửa cuối năm 2025, xu hướng tăng chững lại và xuất hiện tín hiệu điều chỉnh khi giá đóng cửa giảm xuống dưới đường SMA_50. Nhìn chung, giai đoạn nghiên cứu cho thấy thị trường đã trải qua chu kỳ giảm – hồi phục – tăng trưởng, và hiện đang bước vào pha điều chỉnh ngắn hạn.
            """
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
            comment = """
            **Nhận xét:**
             
            Biểu đồ (Candlestick) trên thể hiện diễn biến giá của chỉ số VN30 dưới dạng biểu đồ nến, kết hợp với đường trung bình động 50 phiên (SMA_50) trong giai đoạn từ năm 2021 đến 2025. Quan sát cho thấy, chỉ số VN30 giảm mạnh trong năm 2022, sau đó hình thành xu hướng hồi phục rõ rệt từ năm 2023 đến giữa năm 2025. Đường SMA_50 thể hiện xu hướng tăng ổn định trong giai đoạn này, đóng vai trò là ngưỡng hỗ trợ động cho giá. Tuy nhiên, kể từ nửa cuối năm 2025, xuất hiện tín hiệu điều chỉnh khi các nến giá bắt đầu cắt xuống dưới đường SMA_50, phản ánh sự suy yếu của đà tăng và tâm lý thận trọng của nhà đầu tư. Nhìn chung, giai đoạn nghiên cứu cho thấy thị trường VN30 trải qua chu kỳ giảm – hồi phục – tăng trưởng mạnh, và đang chuyển sang pha điều chỉnh ngắn hạn trong thời điểm cuối kỳ quan sát.            
            """

        fig.update_layout(xaxis_title="Ngày", yaxis_title="Giá", height=600)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(comment)

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

        st.markdown("""
        **Nhận xét:**
             
        Biểu đồ thống kê cho thấy chỉ số VN30 trong giai đoạn nghiên cứu có mức dao động khá lớn, với giá cao nhất đạt 2055.85 điểm và thấp nhất 863.31 điểm, phản ánh sự biến động mạnh của thị trường chứng khoán Việt Nam trong những năm gần đây. Độ lệch chuẩn đạt 214.51 cho thấy rủi ro biến động giá cao, đặc trưng của giai đoạn thị trường có nhiều yếu tố bất ổn. Biểu đồ tỷ suất sinh lời thể hiện sự dao động liên tục quanh mức trung bình, với nhiều đợt tăng giảm đột biến, cho thấy thị trường chịu tác động mạnh từ cả yếu tố kinh tế vĩ mô và tâm lý nhà đầu tư. Nhìn chung, VN30 duy trì xu hướng biến động mạnh nhưng vẫn tiềm ẩn cơ hội đầu tư đối với nhà đầu tư có khẩu vị rủi ro cao.    
        """)

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

        st.markdown("""
        **Nhận xét:**
             
        Kết quả (Monte Carlo) cho thấy mức Value at Risk (VaR) ở ngưỡng 95% đạt khoảng 179.25 điểm, phản ánh rủi ro tiềm ẩn khi thị trường biến động bất lợi trong ngắn hạn. Phân phối giá kết thúc cho thấy sự phân tán giá trị tương đối hẹp, cho thấy kịch bản mô phỏng tập trung quanh mức giá hiện tại. Điều này cho thấy trong điều kiện bình thường, VN30 có khả năng duy trì xu hướng ổn định trong ngắn hạn, song vẫn tiềm ẩn rủi ro giảm giá đáng kể khi thị trường chịu tác động tiêu cực.
        """)

else:
    st.warning("Vui lòng tải lên file Excel dữ liệu VN30 để bắt đầu.")
