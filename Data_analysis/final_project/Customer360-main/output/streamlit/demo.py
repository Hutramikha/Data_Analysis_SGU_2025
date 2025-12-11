import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="Customer360 — Demo PRO v3 (VN)", layout="wide")

# -------------------------- Dữ liệu demo (2 khách) --------------------------
now = pd.Timestamp("2018-09-01")

customers = [
    {
        "customer_unique_id": "CUST_AAAA",
        "customer_id": "CA_001",
        "city": "Sao Paulo",
        "state": "SP",
    },
    {
        "customer_unique_id": "CUST_CCCC",
        "customer_id": "CC_003",
        "city": "Belo Horizonte",
        "state": "MG",
    },
]

orders = [
    # Customer A
    {
        "order_id": "ORD_00001",
        "customer_unique_id": "CUST_AAAA",
        "customer_id": "CA_001",
        "order_status": "delivered",
        "order_purchase_timestamp": now - timedelta(days=10),
        "order_delivered_customer_date": now - timedelta(days=5),
        "order_estimated_delivery_date": now - timedelta(days=6),
        "payment_type": "credit_card",
        "payment_installments": 3,
        "payment_value": 120.0,
        "price": 100.0,
        "freight_value": 20.0,
        "product_category": "electronics",
        "review_score": 5,
    },
    {
        "order_id": "ORD_00002",
        "customer_unique_id": "CUST_AAAA",
        "customer_id": "CA_001",
        "order_status": "delivered",
        "order_purchase_timestamp": now - timedelta(days=60),
        "order_delivered_customer_date": now - timedelta(days=55),
        "order_estimated_delivery_date": now - timedelta(days=56),
        "payment_type": "credit_card",
        "payment_installments": 1,
        "payment_value": 45.5,
        "price": 40.0,
        "freight_value": 5.5,
        "product_category": "books",
        "review_score": 4,
    },
    {
        "order_id": "ORD_00003",
        "customer_unique_id": "CUST_AAAA",
        "customer_id": "CA_001",
        "order_status": "canceled",
        "order_purchase_timestamp": now - timedelta(days=20),
        "order_delivered_customer_date": pd.NaT,
        "order_estimated_delivery_date": now - timedelta(days=14),
        "payment_type": "boleto",
        "payment_installments": 1,
        "payment_value": 0.0,
        "price": 60.0,
        "freight_value": 10.0,
        "product_category": "toys",
        "review_score": None,
    },
    # Customer C
    {
        "order_id": "ORD_00006",
        "customer_unique_id": "CUST_CCCC",
        "customer_id": "CC_003",
        "order_status": "shipped",
        "order_purchase_timestamp": now - timedelta(days=3),
        "order_delivered_customer_date": pd.NaT,
        "order_estimated_delivery_date": now + timedelta(days=4),
        "payment_type": "debit_card",
        "payment_installments": 1,
        "payment_value": 78.9,
        "price": 68.9,
        "freight_value": 10.0,
        "product_category": "beauty",
        "review_score": None,
    },
    {
        "order_id": "ORD_00007",
        "customer_unique_id": "CUST_CCCC",
        "customer_id": "CC_003",
        "order_status": "delivered",
        "order_purchase_timestamp": now - timedelta(days=400),
        "order_delivered_customer_date": now - timedelta(days=395),
        "order_estimated_delivery_date": now - timedelta(days=390),
        "payment_type": "credit_card",
        "payment_installments": 2,
        "payment_value": 250.0,
        "price": 230.0,
        "freight_value": 20.0,
        "product_category": "electronics",
        "review_score": 5,
    },
]

orders_df = pd.DataFrame(orders)
orders_df["order_purchase_timestamp"] = pd.to_datetime(
    orders_df["order_purchase_timestamp"]
)
orders_df["order_delivered_customer_date"] = pd.to_datetime(
    orders_df["order_delivered_customer_date"]
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


def fmt_date(ts):
    if pd.isna(ts):
        return "N/A"
    try:
        return pd.to_datetime(ts).strftime("%Y-%m-%d")
    except:
        return str(ts)


# -------------------------- Xây customer360 --------------------------
def build_customer360(orders_df):
    df = orders_df.copy()
    delivered = df[df["order_status"] == "delivered"]

    monetary = (
        delivered.groupby("customer_unique_id")["payment_value"]
        .sum()
        .rename("monetary")
    )
    total_orders = (
        df.groupby("customer_unique_id")["order_id"].nunique().rename("total_orders")
    )
    delivered_orders = (
        delivered.groupby("customer_unique_id")["order_id"]
        .nunique()
        .rename("delivered_orders")
    )
    last_purchase = (
        delivered.groupby("customer_unique_id")["order_purchase_timestamp"]
        .max()
        .rename("last_purchase")
    )
    first_purchase = (
        df.groupby("customer_unique_id")["order_purchase_timestamp"]
        .min()
        .rename("first_purchase")
    )
    payment_types = (
        df.groupby("customer_unique_id")["payment_type"]
        .agg(lambda x: ",".join(sorted(set(x))))
        .rename("payment_types")
    )
    avg_installments = (
        df.groupby("customer_unique_id")["payment_installments"]
        .mean()
        .rename("avg_installments")
    )

    top_cat = (
        df.groupby(["customer_unique_id", "product_category"])["order_id"]
        .count()
        .reset_index()
    )
    top_cat = (
        top_cat.sort_values(["customer_unique_id", "order_id"], ascending=[True, False])
        .drop_duplicates("customer_unique_id")
        .set_index("customer_unique_id")["product_category"]
        .rename("top_category")
    )

    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days
    avg_delivery = (
        df.groupby("customer_unique_id")["delivery_days"]
        .mean()
        .rename("avg_delivery_days")
    )
    late_rate = (
        df.assign(
            late=df["order_delivered_customer_date"]
            > df["order_estimated_delivery_date"]
        )
        .groupby("customer_unique_id")["late"]
        .mean()
        .rename("late_rate")
    )
    avg_review = (
        df.groupby("customer_unique_id")["review_score"].mean().rename("avg_review")
    )

    cust = pd.concat(
        [
            monetary,
            total_orders,
            delivered_orders,
            last_purchase,
            first_purchase,
            payment_types,
            avg_installments,
            top_cat,
            avg_delivery,
            late_rate,
            avg_review,
        ],
        axis=1,
    )

    cust = cust.reset_index()

    # map thông tin địa lý/id
    cust["customer_id"] = cust["customer_unique_id"].map(
        {c["customer_unique_id"]: c["customer_id"] for c in customers}
    )
    cust["city"] = cust["customer_unique_id"].map(
        {c["customer_unique_id"]: c["city"] for c in customers}
    )
    cust["state"] = cust["customer_unique_id"].map(
        {c["customer_unique_id"]: c["state"] for c in customers}
    )

    # recency & age
    cust["recency_days"] = (now - cust["last_purchase"]).dt.days
    cust["customer_age_days"] = (now - cust["first_purchase"]).dt.days
    cust["months_active"] = (cust["customer_age_days"] / 30).clip(lower=1)

    cust["avg_order_value"] = (
        (cust["monetary"] / cust["delivered_orders"])
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )
    cust["orders_per_month"] = cust["total_orders"] / cust["months_active"]

    # RFM safe
    cust["r_score"] = rank_to_1_5((-cust["recency_days"]).fillna(-9999))
    cust["f_score"] = rank_to_1_5(cust["delivered_orders"].fillna(0))
    cust["m_score"] = rank_to_1_5(cust["monetary"].fillna(0))
    cust["rfm_score"] = cust["r_score"] * 100 + cust["f_score"] * 10 + cust["m_score"]

    cust["r_percentile"] = (cust["r_score"] - 1) / 4
    cust["f_percentile"] = (cust["f_score"] - 1) / 4
    cust["m_percentile"] = (cust["m_score"] - 1) / 4

    cust["cltv_estimate"] = cust["avg_order_value"] * cust["delivered_orders"] * 1.2

    # top3 categories
    top3 = (
        df.groupby(["customer_unique_id", "product_category"])["order_id"]
        .count()
        .reset_index()
        .sort_values(["customer_unique_id", "order_id"], ascending=[True, False])
    )
    top3 = (
        top3.groupby("customer_unique_id")
        .head(3)
        .groupby("customer_unique_id")["product_category"]
        .apply(lambda x: ", ".join(x))
        .rename("top3_categories")
    )
    cust = cust.merge(top3, how="left", left_on="customer_unique_id", right_index=True)

    # churn heuristic 0..1
    max_recency = cust["recency_days"].replace({np.nan: 0}).max() or 1
    recency_score = cust["recency_days"].fillna(max_recency) / max_recency
    freq_score = 1 - cust["f_percentile"].fillna(0)
    m_ = 1 - cust["m_percentile"].fillna(0)
    cust["churn_risk"] = (0.5 * recency_score + 0.25 * freq_score + 0.25 * m_).clip(
        0, 1
    )

    # segment
    def segment(row):
        if row["rfm_score"] >= 445:
            return "Champion"
        if row["rfm_score"] >= 333:
            return "Loyal"
        if row["rfm_score"] >= 222:
            return "Potential"
        if row["rfm_score"] >= 111:
            return "At Risk"
        return "Lost"

    cust["segment"] = cust.apply(segment, axis=1)

    return cust


customer360 = build_customer360(orders_df)

# -------------------------- Giao diện Streamlit (Tiếng Việt) --------------------------
st.title("Customer360 — Demo PRO v3 (mẫu)")

st.sidebar.header("Tùy chọn")
selected_customer = st.sidebar.selectbox(
    "Chọn khách", customer360["customer_unique_id"].tolist()
)
show_orders = st.sidebar.checkbox("Hiển thị Lịch sử đơn", True)
download_row = st.sidebar.checkbox("Hiển thị nút Tải Customer360 (CSV)", True)

cust_row = customer360[customer360["customer_unique_id"] == selected_customer].iloc[0]
cust_orders = orders_df[
    orders_df["customer_unique_id"] == selected_customer
].sort_values("order_purchase_timestamp", ascending=False)

# -------------------------- Tabs chính --------------------------
tab_profile, tab_behavior, tab_orders, tab_debug = st.tabs(
    ["Hồ sơ & KPI", "Biểu đồ hành vi", "Lịch sử đơn", "Dữ liệu thô"]
)

with tab_profile:
    # KPI hàng đầu
    k1, k2, k3, k4, k5 = st.columns([1.2, 1, 1, 1, 1])
    k1.markdown(
        f"### 👤 {selected_customer}\n**{cust_row['customer_id']}**\n{cust_row['city']} / {cust_row['state']}"
    )
    k2.metric("💰 Tổng chi tiêu (đã giao)", fmt_money(cust_row["monetary"]))
    k3.metric("🛒 Đơn đã giao", int(cust_row["delivered_orders"]))
    k4.metric("📅 Đơn / Tháng", f"{cust_row['orders_per_month']:.2f}")
    churn_pct = f"{cust_row['churn_risk']*100:.0f}%"
    if cust_row["churn_risk"] > 0.6:
        k5.markdown(f"### 🔴 Nguy cơ mất khách\n**{churn_pct}**")
        st.error("⚠️ Khách có nguy cơ churn cao — cân nhắc chiến dịch win-back.")
    elif cust_row["churn_risk"] > 0.3:
        k5.markdown(f"### 🟠 Nguy cơ mất khách\n**{churn_pct}**")
        st.warning("🟠 Khách cần chú ý — xem xét ưu đãi nhắc mua.")
    else:
        k5.markdown(f"### 🟢 Nguy cơ mất khách\n**{churn_pct}**")
        st.success("✅ Khách ổn định.")

    st.markdown("---")

    # Thông tin chi tiết hồ sơ
    st.subheader("Hồ sơ khách")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.write(f"**Mã khách:** {cust_row['customer_id']}")
        st.write(f"**Lần mua đầu:** {fmt_date(cust_row['first_purchase'])}")
        st.write(f"**Lần mua gần nhất (giao):** {fmt_date(cust_row['last_purchase'])}")
        st.write(
            f"**Tuổi khách (ngày):** {int(cust_row['customer_age_days'])} ngày ({cust_row['months_active']:.1f} tháng)"
        )
        st.write(f"**Danh mục hàng Top3:** {cust_row.get('top3_categories','N/A')}")
        st.write(
            f"**Phân khúc:** {cust_row['segment']} — (R{cust_row['r_score']} F{cust_row['f_score']} M{cust_row['m_score']})"
        )
    with col_b:
        st.write(
            f"**Giá trị trung bình/đơn:** {fmt_money(cust_row['avg_order_value'])}"
        )
        st.write(f"**Ước tính CLTV:** {fmt_money(cust_row['cltv_estimate'])}")
        st.write(f"**Loại thanh toán:** {cust_row['payment_types']}")
        st.write(
            f"**Độ đa dạng danh mục:** {cust_orders['product_category'].nunique()}"
        )
        st.write(
            f"**Đánh giá trung bình:** {cust_row['avg_review']:.2f}"
            if not pd.isna(cust_row["avg_review"])
            else "Đánh giá: N/A"
        )

    st.markdown("---")
    st.subheader("Gợi ý nhanh (Insights)")
    insights = []
    if cust_row["cltv_estimate"] > 200:
        insights.append("💎 Khách có giá trị cao — cân nhắc ưu đãi VIP.")
    if cust_row["orders_per_month"] < 0.05:
        insights.append("⚠️ Hoạt động thấp — đề xuất chiến dịch tái tương tác.")
    if cust_row["churn_risk"] > 0.6:
        insights.append("🔥 Nguy cơ churn cao — gửi chương trình win-back.")
    if len(insights) == 0:
        insights.append("✅ Không có hành động cấp bách. Khách ổn định.")
    for it in insights:
        st.markdown(f"- {it}")

    # Nút tải CSV (Customer360 row)
    if download_row:
        row_df = pd.DataFrame([cust_row.to_dict()])
        csv = row_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Tải Customer360 (CSV)",
            csv,
            file_name=f"{selected_customer}_customer360.csv",
            mime="text/csv",
        )

with tab_behavior:
    st.header("Biểu đồ hành vi")

    # Lịch sử chi tiêu 6 tháng gần nhất (demo)
    tmp = cust_orders.copy()
    tmp["month"] = tmp["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    monthly = tmp.groupby("month")["payment_value"].sum().reset_index()
    if monthly.empty:
        st.info("Không có dữ liệu chi tiêu để vẽ biểu đồ.")
    else:
        cutoff = (now - pd.DateOffset(months=6)).normalize()
        monthly6 = monthly[monthly["month"] >= cutoff]
        if monthly6.empty:
            st.info("Không có đơn trong 6 tháng gần nhất.")
        else:
            fig = px.bar(
                monthly6,
                x="month",
                y="payment_value",
                title="Chi tiêu 6 tháng gần nhất",
                labels={"payment_value": "BRL", "month": "Tháng"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # Phân bố danh mục
    cat = cust_orders["product_category"].value_counts().reset_index()
    if not cat.empty:
        cat.columns = ["category", "count"]
        fig2 = px.pie(cat, names="category", values="count", title="Phân bố danh mục")
        st.plotly_chart(fig2, use_container_width=True)

    # Phân bố đánh giá
    rev = cust_orders.dropna(subset=["review_score"])
    if not rev.empty:
        fig3 = px.histogram(
            rev, x="review_score", nbins=5, title="Phân bố điểm đánh giá"
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.header("RFM Radar")
    rfm_vals = [cust_row["r_score"], cust_row["f_score"], cust_row["m_score"]]
    fig_radar = go.Figure()
    fig_radar.add_trace(
        go.Scatterpolar(
            r=rfm_vals + [rfm_vals[0]],
            theta=["Recency", "Frequency", "Monetary", "Recency"],
            fill="toself",
            name=selected_customer,
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab_orders:
    st.header("Lịch sử đơn hàng")
    if show_orders:
        display_cols = [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "payment_type",
            "payment_installments",
            "payment_value",
            "product_category",
            "review_score",
        ]
        st.dataframe(cust_orders[display_cols].reset_index(drop=True))
    else:
        st.info("Đã tắt hiển thị lịch sử đơn (bật trong sidebar).")

with tab_debug:
    st.header("Dữ liệu Customer360 (thô)")
    st.write(cust_row)

# Footer
st.markdown("---")
st.caption(
    "Ghi chú: Dữ liệu mẫu cứng (hardcoded) mô phỏng cấu trúc Olist. Dùng làm prototype UI."
)
