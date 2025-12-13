import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="Customer360 — Demo PRO v3 (VN)", layout="wide")

# -------------------------- Dữ liệu demo (2 khách) --------------------------
now = pd.Timestamp("2018-09-01")

customers = pd.read_csv("../../data/2_clean/customers.csv")
orders = pd.read_csv("../../data/2_clean/orders.csv")
featured_df = pd.read_csv("../../data/3_model/featured_data.csv")
clustered_df = pd.read_csv("../../data/3_model/clustered_data.csv")
customer360_df = featured_df.merge(
    clustered_df[["customer_unique_id", "ClusterLabel"]],
    on="customer_unique_id",
    how="left",
)

# -------------------------- Hàm phụ trợ an toàn --------------------------
def rank_to_1_5(series):
    """Chuyển rank thành 1..5 an toàn cho tập nhỏ"""
    if series.nunique() == 0:
        return pd.Series([1] * len(series), index=series.index)
    ranks = series.rank(method="first")
    maxr = ranks.max()
    scaled = (ranks - 1) / max(1, maxr - 1) * 4 + 1
    return scaled.fillna(1).round().astype(int)


def fmt_money(x):
    try:
        return f"R$ {x:,.2f}"
    except:
        return "R$ 0.00"


def validate_date(ts):
    ts = pd.to_datetime(ts)
    return ts.strftime("%d-%m-%Y %H:%M:%S")


# -------------------------- Giao diện Streamlit (Tiếng Việt) --------------------------
st.markdown("<h1 style='text-align: center;'>Customer360</h1>", unsafe_allow_html=True)

st.sidebar.header("Tùy chọn")
selected_customer = st.sidebar.selectbox(
    "Chọn khách", customer360_df["customer_unique_id"].tolist()
)

cust_row = customer360_df[
    customer360_df["customer_unique_id"] == selected_customer
].iloc[0]

# -------------------------- Tabs chính --------------------------
tab_profile, tab_behavior, tab_orders, tab_debug = st.tabs(
    ["Hồ sơ & KPI", "Biểu đồ hành vi", "Lịch sử đơn", "Dữ liệu thô"]
)

with tab_profile:
    st.subheader("⚡ KPI")
    # -------------------------- KPI --------------------------
    st.markdown(
        """
        <style>
        .kpi-row { display:flex; gap:12px; align-items:stretch; }
        .kpi-card {
            background: linear-gradient(90deg, rgba(255,255,255,0.85), rgba(250,250,255,0.85));
            border: 1px solid rgba(0,0,0,0.06);
            padding: 12px;
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(12,38,63,0.06);
            min-height:72px;
        }
        .kpi-card b { font-size:14px; display:block; margin-bottom:6px; }
        .kpi-card .value { font-size:18px; font-weight:600; }
        .profile-block {
            background: rgba(255,255,255,0.6);
            border-radius: 10px;
            padding: 12px;
            border: 1px solid rgba(0,0,0,0.04);
        }
        .spacer { height:6px; }
        /* Responsive tweak */
        @media (max-width: 640px) {
        .kpi-card { padding:10px; font-size:14px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------- KPI --------------------------
    with st.container():
        cols = st.columns([1, 1, 1, 1, 1])
        cols[0].markdown(
            f"<div class='kpi-card'><b>👤 Khách hàng</b><div class='value'>{selected_customer}</div></div>",
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f"<div class='kpi-card'><b>💰 Tổng chi tiêu</b><div class='value'>{fmt_money(cust_row['monetary'])}</div></div>",
            unsafe_allow_html=True,
        )
        cols[2].markdown(
            f"<div class='kpi-card'><b>🛒 Số đơn đã giao</b><div class='value'>{cust_row['delivered_orders']}</div></div>",
            unsafe_allow_html=True,
        )
        cols[3].markdown(
            f"<div class='kpi-card'><b>📅 Tỷ lệ đơn / tháng</b><div class='value'>{cust_row['orders_per_month']:.2f}</div></div>",
            unsafe_allow_html=True,
        )
        cols[4].markdown(
            f"<div class='kpi-card'><b>🧑‍🤝‍🧑 Nhóm</b><div class='value'>{cust_row['ClusterLabel']}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    # -------------------------- Địa điểm --------------------------
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns([1, 1, 1, 1])
    row2_col1.markdown(
        "<div class='profile-block'>"
        f"<b>📍 Địa điểm:</b><br>"
        f"Thành phố: {cust_row['customer_city']}<br>"
        f"Bang: {cust_row['customer_state']}"
        "</div>",
        unsafe_allow_html=True,
    )

    # Cột còn lại trống để giữ đều cột, tránh lệch hàng (vẫn giữ chính xác nội dung: &nbsp;)
    row2_col2.markdown("&nbsp;", unsafe_allow_html=True)
    row2_col3.markdown("&nbsp;", unsafe_allow_html=True)
    row2_col4.markdown("&nbsp;", unsafe_allow_html=True)

    st.markdown("---")

    # ----------------------- Thông tin chi tiết ----------------------
    st.subheader("📝 Hồ sơ khách")
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.write(f"**Lần mua đầu:** {validate_date(cust_row['first_purchase'])}")
        st.write(f"**Lần mua cuối:** {validate_date(cust_row['last_purchase'])}")
        st.write(
            f"**Thời gian kể từ đơn đầu tiên:** {int(cust_row['customer_age_days'])} ngày"
        )
        st.write(
            f"**Thời gian hoạt động khách (customer_lifetime_days):** {int(cust_row['customer_lifetime_days'])} ngày"
        )
        st.write(
            f"**Thời gian kể từ đơn gần nhất (Recency):** {int(cust_row['recency_days'])} ngày"
        )
        st.write(f"**Tổng số đơn hàng (Frequency):** {int(cust_row['total_orders'])}")
        st.write(f"**Số đơn đã giao:** {int(cust_row['delivered_orders'])}")
        st.write(
            f"**Giá trị trung bình/đơn:** {fmt_money(cust_row['avg_order_value'])}"
        )

    with col_b:
        st.write(f"**Loại thanh toán ưa thích:** {cust_row['preferred_payment_type']}")
        st.write(
            f"**Điểm đánh giá trung bình:** {cust_row['avg_review_score']:.2f}"
            if not pd.isna(cust_row["avg_review_score"])
            else "Đánh giá: N/A"
        )
        st.write(f"**Độ đa dạng danh mục** {cust_row.get('top_3_categories','N/A')}")
        st.write(
            f"**Điểm RFM (R{cust_row['r_score']} F{cust_row['f_score']} M{cust_row['m_score']}):** {cust_row['rfm_score']}"
        )
        st.write(
            f"**Số đơn giao đúng hạn:** {int(cust_row['num_of_on_time_delivery'])}"
        )
        st.write(f"**Số đơn giao trễ:** {int(cust_row['num_of_late_delivery'])}")
        st.write(f"**Tỷ lệ giao trễ:** {cust_row['late_rate']:.2f}")
        st.write(
            f"**Thời gian giao trung bình:** {cust_row['avg_delivery_days']:.1f} ngày"
        )

    st.markdown("---")
    # ----------------------- Insight ----------------------
    st.subheader("💡 Gợi ý nhanh")

    insights = []

    cluster = cust_row["ClusterLabel"]

    # ✅ Insight theo ClusterLabel với đầy đủ Ý nghĩa và Hành động
    if cluster == "BigDeal":
        insights.append("🟪 **BigDeal**")
        insights.append(
            "**Ý nghĩa:** Khách hàng có giá trị đơn hàng cực cao nhưng mua không thường xuyên, đại diện cho các giao dịch lớn mang tính quyết định."
        )
        insights.append(
            "**Hành động:** Chăm sóc chọn lọc và theo dõi sát, ưu tiên xây dựng niềm tin thay vì kích cầu bằng giảm giá."
        )
    elif cluster == "Valuable":
        insights.append("🟤 **Valuable**")
        insights.append(
            "**Ý nghĩa:** Khách hàng có tần suất mua khá cao và giá trị chi tiêu vượt trội so với nhóm thông thường, là nguồn doanh thu ổn định."
        )
        insights.append(
            "**Hành động:** Giữ chân bằng chương trình khách hàng thân thiết và cá nhân hóa đề xuất để tối đa hóa giá trị vòng đời."
        )
    elif cluster == "Core":
        insights.append("🟥 **Core**")
        insights.append(
            "**Ý nghĩa:** Đây là nhóm khách hàng có tần suất mua sắm cao, giá trị đơn hàng lớn và thời gian mua gần đây dao động từ ngắn đến trung bình. Họ chính là lực lượng tạo ra phần lớn doanh thu cho doanh nghiệp."
        )
        insights.append(
            "**Hành động:**\n- Gửi lời cảm ơn, đề xuất sản phẩm liên quan.\n- Ưu tiên chăm sóc cao nhất với đặc quyền riêng và trải nghiệm vượt trội để duy trì sự trung thành tuyệt đối."
        )
    elif cluster == "Nurture":
        insights.append("🟦 **Nurture**")
        insights.append(
            "**Ý nghĩa:** Cụm này là những khách hàng vừa mới mua hàng (Recency thấp) nhưng giá trị đơn hàng không cao và cũng không thường xuyên mua hàng."
        )
        insights.append(
            "**Hành động:** Tập trung xây dựng mối quan hệ với khách hàng, cung cấp dịch vụ khách hàng tốt và khuyến mãi để khuyến khích mua thường xuyên hơn."
        )
    elif cluster == "Re-Engage":
        insights.append("🟥 **Re-Engage**")
        insights.append(
            "**Ý nghĩa:** Cụm này là những khách hàng chi tiêu trung bình thấp và đã không mua hàng trong một thời gian dài (Recency cao), cũng không thường xuyên mua hàng. Đây là nhóm có nguy cơ rời bỏ."
        )
        insights.append(
            "**Hành động:** Sử dụng chiến dịch marketing và ưu đãi giảm giá đặc biệt để thu hút họ quay lại."
        )
    elif cluster == "Develop":
        insights.append("🟩 **Develop**")
        insights.append(
            "**Ý nghĩa:** Đây là nhóm khách hàng chi tiêu trung bình cao và mới mua hàng gần đây, dù không mua thường xuyên. Họ đã bộc lộ giá trị, nhưng mức độ gắn kết vẫn đang ở giai đoạn đầu."
        )
        insights.append(
            "**Hành động:** Kích thích lần mua thứ 2–3 thông qua tặng kèm sản phẩm và gợi ý sản phẩm liên quan, kết hợp ưu đãi cá nhân hóa và truyền thông giá trị sản phẩm để xây dựng niềm tin và thúc đẩy khách quay lại."
        )
    else:
        insights.append("✅ Không có hành động cấp bách theo nhóm khách.")

    # Hiển thị các insight
    for it in insights:
        st.markdown(f"- {it}")
    st.caption(
        "Ghi chú: Insight được thiết lập theo nhóm, có khả năng sai số với từng khách hàng riêng biệt."
    )

with tab_behavior:

    customers = pd.read_csv("../../data/2_clean/customers.csv")
    order_items = pd.read_csv("../../data/2_clean/order_items.csv")
    payments = pd.read_csv("../../data/2_clean/payments.csv")
    products = pd.read_csv("../../data/2_clean/products.csv")
    reviews = pd.read_csv("../../data/2_clean/reviews.csv")
    geolocation = pd.read_csv("../../data/2_clean/geolocation.csv")
    sellers = pd.read_csv("../../data/2_clean/sellers.csv")

    st.header("📊 Phân tích hành vi chi tiết")

    # --- BƯỚC 1: CHUẨN BỊ DỮ LIỆU CHI TIẾT CHO KHÁCH HÀNG NÀY ---
    related_cust_ids = customers[customers["customer_unique_id"] == selected_customer][
        "customer_id"
    ]

    # Lọc đơn hàng của khách này
    cust_orders_detail = orders[orders["customer_id"].isin(related_cust_ids)].copy()

    # Đảm bảo dữ liệu thời gian
    if "order_purchase_timestamp" in cust_orders_detail.columns:
        cust_orders_detail["order_purchase_timestamp"] = pd.to_datetime(
            cust_orders_detail["order_purchase_timestamp"]
        )
        cust_orders_detail["month_year"] = (
            cust_orders_detail["order_purchase_timestamp"].dt.to_period("M").astype(str)
        )
        cust_orders_detail["hour"] = cust_orders_detail[
            "order_purchase_timestamp"
        ].dt.hour
        cust_orders_detail["day_of_week"] = cust_orders_detail[
            "order_purchase_timestamp"
        ].dt.day_name()

    if cust_orders_detail.empty:
        st.warning("Không tìm thấy dữ liệu đơn hàng chi tiết cho khách này.")
    else:
        # --- BƯỚC 2: VẼ BIỂU ĐỒ ---

        # 1. Timeline Chi tiêu (Nếu có dữ liệu tiền)
        st.subheader("1. Xu hướng chi tiêu theo thời gian")

        df1 = cust_orders_detail.merge(payments, on="order_id", how="left")

        has_value = "payment_value" in df1.columns

        # Chuyển sang datetime nếu chưa
        df1["order_purchase_timestamp"] = pd.to_datetime(
            df1["order_purchase_timestamp"]
        )

        # Tạo cột month_year dạng "YYYY-MM"
        df1["month_year"] = (
            df1["order_purchase_timestamp"].dt.to_period("M").astype(str)
        )

        if has_value:
            # Group theo tháng
            monthly_spend = (
                df1.groupby("month_year")["payment_value"].sum().reset_index()
            )

            fig_trend = px.bar(
                monthly_spend,
                x="month_year",
                y="payment_value",
                text_auto=".2s",
                title="Tổng chi tiêu qua các tháng",
                labels={"month_year": "Tháng", "payment_value": "Chi tiêu (BRL)"},
                color="payment_value",
                color_continuous_scale="Blues",
            )
            fig_trend.update_traces(textposition="outside")
            st.plotly_chart(fig_trend, use_container_width=True)

        else:
            st.warning("Dữ liệu không có cột 'payment_value' để vẽ biểu đồ chi tiêu.")

        st.markdown("---")

        # 2. Thói quen mua sắm (Giờ & Danh mục)
        col_b1, col_b2 = st.columns(2)

        with col_b1:
            st.subheader("2. Khung giờ mua sắm ('Giờ vàng')")
            # Histogram theo giờ trong ngày
            hourly_counts = (
                cust_orders_detail["hour"].value_counts().sort_index().reset_index()
            )
            hourly_counts.columns = ["hour", "count"]

            fig_hour = px.bar(
                hourly_counts,
                x="hour",
                y="count",
                title="Tần suất mua hàng theo giờ",
                labels={"hour": "Giờ trong ngày (0-23)", "count": "Số đơn"},
                range_x=[0, 23],
            )
            # Highlight giờ mua nhiều nhất
            fig_hour.update_traces(marker_color="#FF4B4B")
            st.plotly_chart(fig_hour, use_container_width=True)

            # Insight ngắn
            peak_hour = hourly_counts.sort_values("count", ascending=False).iloc[0][
                "hour"
            ]
            st.caption(
                f"💡 **Gợi ý:** Nên gửi thông báo khuyến mãi vào khoảng **{peak_hour}h - {peak_hour+1}h**."
            )

        with col_b2:
            st.subheader("3. Danh mục ưa thích")

            df3 = cust_orders_detail.merge(order_items, on="order_id", how="left")
            df3 = df3.merge(products, on="product_id", how="left")

            has_cat = "product_category_name" in df3.columns

            if has_cat:
                cat_counts = df3["product_category_name"].value_counts().reset_index()
                cat_counts.columns = ["product_category_name", "count"]

                fig_cat = px.pie(
                    cat_counts,
                    values="count",
                    names="product_category_name",
                    hole=0.6,
                    title="Top danh mục sản phẩm",
                )
                fig_cat.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Không có dữ liệu danh mục sản phẩm.")

        st.markdown("---")

        # 3. RFM Radar & Đánh giá
        col_c1, col_c2 = st.columns([1, 1])

        with col_c1:
            st.subheader("4. Sức khỏe khách hàng (RFM)")
            rfm_vals = [cust_row["r_score"], cust_row["f_score"], cust_row["m_score"]]

            fig_radar = go.Figure()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=rfm_vals + [rfm_vals[0]],
                    theta=[
                        "Recency",
                        "Frequency",
                        "Monetary",
                        "Recency",
                    ],
                    fill="toself",
                    name=str(selected_customer),
                    line_color="#00CC96",
                )
            )
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0, 5.5], tickfont=dict(size=10)
                    ),
                ),
                margin=dict(t=30, b=30),
                showlegend=False,
                height=350,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption("Càng co cụm càng tốt")

        with col_c2:
            st.subheader("5. Mức độ hài lòng")
            # Lọc review của đúng khách hàng này
            df5 = cust_orders_detail.merge(reviews, on="order_id", how="left")

            if "review_score" in df5.columns:
                cust_reviews = df5["review_score"].dropna()
                if not cust_reviews.empty:
                    avg_score = cust_reviews.mean()
                    st.metric("Điểm đánh giá trung bình", f"{avg_score:.1f} / 5.0")

                    fig_rev = px.histogram(
                        cust_reviews,
                        x="review_score",
                        nbins=5,
                        range_x=[0.5, 5.5],
                        title="Phân bố điểm đánh giá của khách",
                        color_discrete_sequence=["#FFA15A"],
                    )
                    fig_rev.update_layout(
                        bargap=0.2, xaxis_title="Điểm (Sao)", yaxis_title="Số lần"
                    )
                    st.plotly_chart(fig_rev, use_container_width=True)
                else:
                    st.info("Khách hàng này chưa để lại đánh giá nào.")
            else:
                st.warning("Không có cột review_score.")

with tab_orders:
    st.header("Lịch sử đơn hàng")
    customers = pd.read_csv("../../data/2_clean/customers.csv")

    customer_orders_df = customers[["customer_unique_id", "customer_id"]].merge(
        orders, on="customer_id", how="left"
    )

    customer_orders = customer_orders_df[
        customer_orders_df["customer_unique_id"] == cust_row["customer_unique_id"]
    ].reset_index(drop=True)
    st.dataframe(customer_orders)


with tab_debug:
    st.header("Dữ liệu Customer360 (thô)")
    st.write(cust_row)
