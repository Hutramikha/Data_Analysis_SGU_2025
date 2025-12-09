import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Load dữ liệu
# -----------------------------------------------------------
@st.cache_data
def load_featured():
    df = pd.read_csv("featured_data.csv", parse_dates=["first_purchase", "last_purchase"])
    return df

customer360 = load_featured()

# Hàm phụ trợ an toàn
# -----------------------------------------------------------
def fmt_money(x):
    return f"{x:,.0f}"

def fmt_date(x):
    if pd.isna(x):
        return "N/A"
    return x.strftime("%d/%m/%Y")

# UI
# -----------------------------------------------------------
st.set_page_config(page_title="Customer360", layout="wide")

st.title("Customer360 — (featured)")

st.sidebar.header("Tùy chọn")
selected_customer = st.sidebar.selectbox(
    "Chọn khách",
    customer360["customer_unique_id"].tolist()
)

cust_row = customer360[customer360["customer_unique_id"] == selected_customer].iloc[0]

# Tabs
tab_profile, tab_behavior, tab_debug = st.tabs(
    ["Hồ sơ & KPI", "Biểu đồ hành vi", "Dữ liệu thô"]
)


# TAB 1 — Hồ sơ & KPI
# -----------------------------------------------------------
with tab_profile:
    k1, k2, k3, k4, k5 = st.columns([1.4, 1, 1, 1, 1])

    # cột trái
    k1.markdown(
        f"### 👤 {selected_customer}\n"
        f"**ID:** {cust_row.get('customer_id', 'N/A')}  \n"
        f"{cust_row['customer_city']} / {cust_row['customer_state']}"
    )

    k2.metric("💰 Tổng chi tiêu", fmt_money(cust_row["monetary"]))
    k3.metric("🛒 Tổng đơn", int(cust_row["total_orders"]))
    k4.metric("📅 Đơn / tháng", f"{cust_row['orders_per_month']:.2f}")

    # churn risk tự dựng từ RFM (đơn giản)
    churn_risk = (1 - cust_row["r_score"] / 5) * 0.5 + (1 - cust_row["f_score"] / 5) * 0.3 + (1 - cust_row["m_score"] / 5) * 0.2
    churn_pct = f"{churn_risk*100:.0f}%"

    if churn_risk > 0.6:
        k5.markdown(f"### 🔴 Mất khách\n**{churn_pct}**")
        st.error("⚠️ Nguy cơ churn cao — đề xuất chiến dịch win-back.")
    elif churn_risk > 0.3:
        k5.markdown(f"### 🟠 Cảnh báo\n**{churn_pct}**")
        st.warning("🟠 Khách có dấu hiệu giảm tương tác.")
    else:
        k5.markdown(f"### 🟢 Ổn định\n**{churn_pct}**")
        st.success("Khách hoạt động ổn định.")

    st.markdown("---")

    # ---------------- Thông tin chi tiết ----------------
    st.subheader("Hồ sơ khách hàng")
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.write(f"**Mã khách:** {cust_row['customer_unique_id']}")
        st.write(f"**Lần mua đầu:** {fmt_date(cust_row['first_purchase'])}")
        st.write(f"**Lần mua gần nhất:** {fmt_date(cust_row['last_purchase'])}")
        st.write(f"**Tuổi khách:** {cust_row['customer_age_days']} ngày")
        st.write(f"**Thời gian hoạt động:** {cust_row['customer_lifetime_days']} ngày")
        st.write(f"**Danh mục Top3:** {cust_row['top_3_categories']}")
        st.write(
            f"**RFM:** R{cust_row['r_score']} F{cust_row['f_score']} M{cust_row['m_score']} "
            f"(Tổng: {cust_row['rfm_score']})"
        )

    with col_b:
        st.write(f"**AOV:** {fmt_money(cust_row['avg_order_value'])}")
        st.write(f"**Tần suất mua / tháng:** {cust_row['orders_per_month']:.2f}")
        st.write(f"**Loại thanh toán ưa dùng:** {cust_row['preferred_payment_type']}")
        st.write(f"**Đánh giá TB:** {cust_row['avg_review_score']:.2f}")
        st.write(f"**Tỷ lệ giao hàng trễ:** {cust_row['late_rate']*100:.1f}%")
        st.write(f"**Thời gian giao TB:** {cust_row['avg_delivery_days']:.1f} ngày")

    st.markdown("---")
    st.subheader("Gợi ý nhanh (Insights)")
    insights = []

    if cust_row["recency_days"] > customer360["recency_days"].median():
        insights.append("⚠️ Khách lâu chưa quay lại — nên gửi chiến dịch tái tương tác.")

    if cust_row["total_orders"] < customer360["total_orders"].mean():
        insights.append("📉 Tần suất mua thấp — nên gợi ý ưu đãi khuyến khích mua lại.")

    if cust_row["monetary"] >= customer360["monetary"].quantile(0.75):
        insights.append("💎 Khách giá trị cao — nên ưu tiên chăm sóc.")

    if len(insights) == 0:
        insights.append("✅ Không có hành động cấp bách. Khách ổn định.")

    for it in insights:
        st.markdown(f"- {it}")

    # Nút tải CSV (Customer360 row)
    st.markdown("---")
    if st.button("⬇️ Tải Customer (CSV)"):
        one = pd.DataFrame([cust_row])
        st.download_button("Tải CSV", data=one.to_csv(index=False), file_name=f"{cust_row['customer_unique_id']}_customer.csv", mime="text/csv")



# TAB 2 — BIỂU ĐỒ HÀNH VI
# -----------------------------------------------------------
with tab_behavior:
    st.header("Biểu đồ hành vi khách hàng")

    # =============================================
    # 1) Lifecycle (Age, Lifetime, Recency)
    # =============================================
    st.subheader("🕒 Vòng đời khách hàng (Lifecycle)")

    lifecycle_df = pd.DataFrame({
        "Chỉ số": ["Tuổi khách (days)", "Lifetime (days)", "Recency (days)"],
        "Giá trị": [
            cust_row["customer_age_days"],
            cust_row["customer_lifetime_days"],
            cust_row["recency_days"],
        ],
    })

    fig_life = px.bar(
        lifecycle_df,
        x="Chỉ số",
        y="Giá trị",
        title="Các chỉ số vòng đời khách hàng",
        text="Giá trị",
    )
    fig_life.update_traces(textposition="outside")
    st.plotly_chart(fig_life, use_container_width=True)

    st.markdown("---")

    # 2) Spending & Frequency
    # =============================================
    st.subheader("💰 Chi tiêu & Tần suất mua")

    spend_df = pd.DataFrame({
        "Chỉ số": ["Tổng chi tiêu", "Tổng đơn", "AOV"],
        "Giá trị": [
            cust_row["monetary"],
            cust_row["delivered_orders"],
            cust_row["avg_order_value"],
        ],
    })

    fig_spend = px.bar(
        spend_df,
        x="Chỉ số",
        y="Giá trị",
        title="Chi tiêu & tần suất mua hàng",
        text="Giá trị",
    )
    fig_spend.update_traces(textposition="outside")
    st.plotly_chart(fig_spend, use_container_width=True)

    st.markdown("---")

    # 3) Delivery Performance
    # =============================================
    st.subheader("🚚 Giao hàng đúng hạn / trễ")

    delivery_df = pd.DataFrame({
        "Loại": ["Đúng hạn", "Trễ"],
        "Số lượng": [
            cust_row["num_of_on_time_delivery"],
            cust_row["num_of_late_delivery"],
        ],
    })

    fig_del = px.pie(
        delivery_df,
        names="Loại",
        values="Số lượng",
        hole=0.35,
        title="Phân bố giao hàng đúng hạn / trễ",
    )
    st.plotly_chart(fig_del, use_container_width=True)

    st.markdown("---")

    # 4) RFM Radar
    # =============================================
    st.subheader("📊 Biểu đồ Radar — RFM Score")

    rfm_vals = [
        cust_row["r_score"],
        cust_row["f_score"],
        cust_row["m_score"],
    ]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=rfm_vals + [rfm_vals[0]],
        theta=["Recency", "Frequency", "Monetary", "Recency"],
        fill="toself",
        name="RFM",
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# TAB 3 — RAW DATA
# -----------------------------------------------------------
with tab_debug:
    st.header("Dữ liệu thô — Customer360 Row")
    st.dataframe(pd.DataFrame([cust_row]))
