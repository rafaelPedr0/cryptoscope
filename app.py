import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import subprocess
import sys

st.set_page_config(
    page_title="CryptoScope Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=900)
def load_market_data() -> pd.DataFrame:
    path = Path("data/processed/market_snapshot.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

@st.cache_data(ttl=900)
def load_history_data() -> pd.DataFrame:
    path = Path("data/processed/price_history.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=["date"])

with st.sidebar:
    st.title("📊 CryptoScope")
    st.caption("Dashboard de Inteligência de Mercado")
    st.divider()

    if st.button("🔄 Atualizar Dados Agora", use_container_width=True):
        with st.spinner("Executando pipeline ETL..."):
            subprocess.run([sys.executable, "src/etl_pipeline.py"], capture_output=True)
        st.cache_data.clear()
        st.success("✅ Dados atualizados!")
        st.rerun()

    top_n = st.slider("Top N criptos para exibir", 5, 50, 20)
    change_filter = st.selectbox(
        "Filtrar por Momentum",
        ["Todos", "🚀 Alta Forte", "📈 Alta", "➡️ Lateral", "🔻 Queda", "📉 Queda Forte"]
    )

df = load_market_data()
df_hist = load_history_data()

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado. Clique em 'Atualizar Dados' no menu lateral.")
    st.stop()

if change_filter != "Todos":
    df = df[df["momentum"] == change_filter]
df = df.head(top_n)

st.title("📊 CryptoScope — Inteligência de Mercado")
st.caption(f"Última atualização: {df['extracted_at'].iloc[0][:19]}")
st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📈 Em Alta (24h)", f"{(df['change_24h_pct'] > 0).sum()} / {len(df)}")
with col2:
    avg = df["change_24h_pct"].mean()
    st.metric("📊 Variação Média 24h", f"{avg:.2f}%", delta=f"{avg:.2f}%")
with col3:
    st.metric("💰 Volume Total 24h", f"${df['volume_24h'].sum()/1e9:.1f}B")
with col4:
    st.metric("⚡ Alta Volatilidade", f"{(df['change_24h_pct'].abs() > 5).sum()} ativos")

st.divider()

st.subheader("🏆 Ranking de Criptomoedas")
display_df = df[["name","symbol","price_usd","change_1h_pct","change_24h_pct","change_7d_pct","market_cap","momentum"]].copy()
display_df["price_usd"] = display_df["price_usd"].apply(lambda x: f"${x:,.2f}")
display_df["market_cap"] = display_df["market_cap"].apply(lambda x: f"${x/1e9:.1f}B")
for col in ["change_1h_pct","change_24h_pct","change_7d_pct"]:
    display_df[col] = display_df[col].apply(lambda x: f"+{x:.2f}%" if x > 0 else f"{x:.2f}%")
st.dataframe(display_df, use_container_width=True, hide_index=True)

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("📊 Variação 24h por Ativo")
    fig_bar = px.bar(
        df.head(15), x="symbol", y="change_24h_pct",
        color="change_24h_pct",
        color_continuous_scale=["#e53935","#b0bec5","#43a047"],
        title="Top 15 — Variação em 24 horas"
    )
    fig_bar.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🌡️ Market Cap vs Volume")
    fig_scatter = px.scatter(
        df, x="market_cap", y="volume_24h",
        size="market_cap", color="change_24h_pct",
        hover_name="name",
        color_continuous_scale="RdYlGn",
        log_x=True, log_y=True,
        title="Market Cap vs Volume (escala log)"
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

if not df_hist.empty:
    st.subheader("📈 Histórico de Preços — Top 5 Criptos")
    coins = df_hist["coin"].unique().tolist()
    selected = st.multiselect("Selecione os ativos:", coins, default=coins[:3])
    if selected:
        fig_line = px.line(
            df_hist[df_hist["coin"].isin(selected)],
            x="date", y="price", color="coin",
            title="Evolução de Preço (últimos 90 dias)"
        )
        fig_line.update_layout(height=450)
        st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.caption("Desenvolvido com Python · Pandas · Streamlit · CoinGecko API | Projeto de Portfólio")