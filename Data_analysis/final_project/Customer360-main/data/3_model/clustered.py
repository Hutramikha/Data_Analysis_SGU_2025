import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Config
# ---------------------------
st.set_page_config(page_title="Customer360", layout="wide")

# Hàm phụ trợ an toàn
# ---------------------------
@st.cache_data
def load_data(path="clustered_data.csv"):
    df = pd.read_csv(path)
    # normalize columns
    df.columns = [c.strip() for c in df.columns]
    # ensure numeric
    for c in ["recency", "frequency", "monetary", "Cluster"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    # cluster label exist?
    if "ClusterLabel" not in df.columns:
        df["ClusterLabel"] = df["Cluster"].astype(str)
    return df

def rank_to_1_5(series, invert=False):
    """Map numeric series to 1..5. If invert=True smaller values -> higher rank (useful for recency)."""
    s = series.copy().fillna(series.median())
    if invert:
        s = -s
    if s.nunique() <= 1:
        return pd.Series([3]*len(s), index=s.index)
    ranks = s.rank(method="average")
    minr, maxr = ranks.min(), ranks.max()
    scaled = (ranks - minr) / (maxr - minr) * 4 + 1
    return scaled.round().astype(int)

def fmt_num(x):
    try:
        if abs(x) >= 1000:
            return f"{x:,.0f}"
        return f"{x:.2f}"
    except:
        return str(x)

# Load dataset
# ---------------------------
try:
    df = load_data("clustered_data.csv")
except Exception as e:
    st.error("Không thể load file 'clustered_data.csv'. Đặt file vào cùng thư mục và thử lại.")
    st.stop()

# Compute R/F/M scores (1..5) based on dataset percentiles
# ---------------------------
# recency: lower is better -> invert=True
df["r_score"] = rank_to_1_5(df["recency"], invert=True)
df["f_score"] = rank_to_1_5(df["frequency"], invert=False)
df["m_score"] = rank_to_1_5(df["monetary"], invert=False)
df["rfm_score"] = df["r_score"] * 100 + df["f_score"] * 10 + df["m_score"]

# cluster centroids (for radar comparison)
cluster_centroids = (
    df.groupby("Cluster")[["recency", "frequency", "monetary"]]
    .mean()
    .reset_index()
)

# Sidebar / selection
# ---------------------------
st.title("Customer360 — (Clustered)")

st.sidebar.header("Tùy chọn")
cust_list = df["customer_unique_id"].astype(str).tolist()
selected_customer = st.sidebar.selectbox("Chọn khách", cust_list)

# filter row
cust_row = df[df["customer_unique_id"].astype(str) == str(selected_customer)]
if cust_row.empty:
    st.error("Không tìm thấy khách đã chọn trong dataset.")
    st.stop()
cust_row = cust_row.iloc[0]

# Tabs
# ---------------------------
tab_profile, tab_behavior, tab_raw = st.tabs(
    ["Hồ sơ & KPI", "Biểu đồ hành vi", "Dữ liệu thô"]
)

# TAB1: Hồ sơ & KPI
# ---------------------------
with tab_profile:
    st.header("Hồ sơ & KPI")

    # Top KPI row
    k1, k2, k3, k4, k5 = st.columns([1.3, 1, 1, 1, 1])

    k1.markdown(f"### 👤 {selected_customer}\n**Cluster:** {cust_row['ClusterLabel']} (#{int(cust_row['Cluster'])})")
    k2.metric("📅 Recency (days)", int(cust_row["recency"]))
    k3.metric("🛒 Frequency", int(cust_row["frequency"]))
    k4.metric("💰 Monetary", fmt_num(cust_row["monetary"]))

    # churn heuristic from RFM percentile (simple)
    # compute percentiles relative to dataset
    r_pct = (df["recency"] <= cust_row["recency"]).mean()
    f_pct = (df["frequency"] <= cust_row["frequency"]).mean()
    m_pct = (df["monetary"] <= cust_row["monetary"]).mean()
    # churn: higher when recency high (not purchased recently), low frequency/monetary
    churn_score = 0.5 * (1 - r_pct) + 0.25 * (1 - f_pct) + 0.25 * (1 - m_pct)
    churn_pct = f"{churn_score*100:.0f}%"

    if churn_score > 0.6:
        k5.markdown(f"### 🔴 Nguy cơ churn\n**{churn_pct}**")
        st.error("Khách có nguy cơ mất — cân nhắc chiến dịch win-back.")
    elif churn_score > 0.3:
        k5.markdown(f"### 🟠 Nguy cơ churn\n**{churn_pct}**")
        st.warning("Khách cần chú ý — cân nhắc ưu đãi nhắc mua.")
    else:
        k5.markdown(f"### 🟢 Khách ổn định\n**{churn_pct}**")
        st.success("Khách ổn định.")

    st.markdown("---")

    # Details
    st.subheader("Chi tiết khách")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write(f"- **Mã Khách:** {cust_row['customer_unique_id']}")
        st.write(f"- **Cluster:** {cust_row['ClusterLabel']} (#{int(cust_row['Cluster'])})")
        st.write(f"- **Recency (days):** {int(cust_row['recency'])}")
        st.write(f"- **Frequency:** {int(cust_row['frequency'])}")
        st.write(f"- **Monetary:** {fmt_num(cust_row['monetary'])}")
    with c2:
        st.write(f"- **R score (1-5):** {int(cust_row['r_score'])}")
        st.write(f"- **F score (1-5):** {int(cust_row['f_score'])}")
        st.write(f"- **M score (1-5):** {int(cust_row['m_score'])}")
        st.write(f"- **RFM composite:** {int(cust_row['rfm_score'])}")

    st.markdown("---")
    st.subheader("Gợi ý nhanh (Insights)")
    insights = []
    if cust_row["recency"] > df["recency"].median():
        insights.append("⚠️ Lần mua gần nhất khá lâu — gửi chiến dịch tái tương tác.")
    if cust_row["frequency"] < df["frequency"].mean():
        insights.append("📉 Frequency thấp — cân nhắc ưu đãi tăng tần suất.")
    if cust_row["monetary"] >= df["monetary"].quantile(0.75):
        insights.append("💎 Khách thuộc nhóm giá trị cao (top 25%) — ưu tiên chăm sóc.")
    # cluster-based hint
    clust_size = (df["Cluster"] == cust_row["Cluster"]).sum()
    insights.append(f"📦 Cluster {cust_row['ClusterLabel']} có {clust_size} khách.")
    for it in insights:
        st.markdown(f"- {it}")

    # download single customer row
    st.markdown("---")
    if st.button("⬇️ Tải Customer (CSV)"):
        one = pd.DataFrame([cust_row])
        st.download_button("Tải CSV", data=one.to_csv(index=False), file_name=f"{cust_row['customer_unique_id']}_customer.csv", mime="text/csv")


# TAB2: Biểu đồ hành vi
# ---------------------------
with tab_behavior:
    st.header("Biểu đồ hành vi")

    # 1) Small KPI row of R/F/M (dataset percentile context)
    a1, a2, a3 = st.columns(3)
    a1.metric("Recency (days)", int(cust_row["recency"]))
    a2.metric("Frequency", int(cust_row["frequency"]))
    a3.metric("Monetary", fmt_num(cust_row["monetary"]))

    st.markdown("---")

    # 2) Distribution plots (dataset) with marker for selected customer
    c1, c2 = st.columns(2)
    with c1:
        fig_rec = px.histogram(df, x="recency", nbins=30, title="Phân bố Recency (toàn bộ khách)")
        fig_rec.add_vline(x=cust_row["recency"], line_dash="dash", line_color="red")
        st.plotly_chart(fig_rec, use_container_width=True)
    with c2:
        fig_freq = px.histogram(df, x="frequency", nbins=30, title="Phân bố Frequency (toàn bộ khách)")
        fig_freq.add_vline(x=cust_row["frequency"], line_dash="dash", line_color="red")
        st.plotly_chart(fig_freq, use_container_width=True)

    st.markdown("---")

    # 3) Monetary distribution
    fig_mon = px.histogram(df, x="monetary", nbins=30, title="Phân bố Monetary (toàn bộ khách)")
    fig_mon.add_vline(x=cust_row["monetary"], line_dash="dash", line_color="red")
    st.plotly_chart(fig_mon, use_container_width=True)

    st.markdown("---")

    # 4) RFM radar: use mapped 1..5 scores
    st.subheader("RFM Radar (mapped 1..5)")

    rfm_vals = [cust_row["r_score"], cust_row["f_score"], cust_row["m_score"]]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=rfm_vals + [rfm_vals[0]],
        theta=["Recency","Frequency","Monetary","Recency"],
        fill="toself",
        name="Customer RFM"
    ))
    # add cluster centroid on same scale (map centroid -> 1..5)
    centroid = cluster_centroids[cluster_centroids["Cluster"] == cust_row["Cluster"]]
    if not centroid.empty:
        cen = centroid.iloc[0]
        # compute centroid r/f/m scores relative to dataset
        cen_r = rank_to_1_5(df["recency"], invert=True).loc[df["Cluster"]==cust_row["Cluster"]].mean()
        cen_f = rank_to_1_5(df["frequency"]).loc[df["Cluster"]==cust_row["Cluster"]].mean()
        cen_m = rank_to_1_5(df["monetary"]).loc[df["Cluster"]==cust_row["Cluster"]].mean()
        cen_vals = [float(cen_r), float(cen_f), float(cen_m)]
        fig_radar.add_trace(go.Scatterpolar(
            r=cen_vals + [cen_vals[0]],
            theta=["Recency","Frequency","Monetary","Recency"],
            fill="toself",
            name="Cluster centroid"
        ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,5])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # 5) Cluster scatter: frequency vs monetary (colored by cluster)
    st.subheader("Cluster scatter (Frequency vs Monetary)")
    fig_cluster = px.scatter(
        df,
        x="frequency",
        y="monetary",
        color="ClusterLabel",
        hover_data=["customer_unique_id"],
        title="Frequency vs Monetary (size=recency)",
        size="recency",
        size_max=25,
    )
    # highlight selected
    fig_cluster.add_scatter(x=[cust_row["frequency"]], y=[cust_row["monetary"]],
                            mode="markers+text", text=["Bạn"], textposition="top center",
                            marker=dict(size=18, symbol="star", color="black"), name="Selected")
    st.plotly_chart(fig_cluster, use_container_width=True)

    st.markdown("---")

    # 6) Quick cluster summary: counts & avg RFM
    st.subheader("Tóm tắt cluster")
    cluster_summary = df.groupby(["Cluster","ClusterLabel"]).agg(
        n_customers=("customer_unique_id","count"),
        avg_recency=("recency","mean"),
        avg_frequency=("frequency","mean"),
        avg_monetary=("monetary","mean")
    ).reset_index().sort_values("n_customers", ascending=False)
    st.dataframe(cluster_summary)


# TAB4: RAW data
# ---------------------------
with tab_raw:
    st.header("Dữ liệu thô - Customer 360 Row")
    st.dataframe(pd.DataFrame([cust_row]))
