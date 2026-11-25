import streamlit as st
import pandas as pd
from engine import get_market_data, generate_signal, load_portfolio, save_portfolio, execute_paper_order, portfolio_metrics

st.set_page_config(page_title="AGENT INVEST", page_icon="📈", layout="wide")
st.title("📈 AGENT INVEST")
st.caption("Versão 0.1 • Simulador de ações • Sem conexão com corretora")

st.warning("MODO SIMULAÇÃO: nenhuma ordem real é enviada. Cotações podem ter atraso ou indisponibilidade. Não use este painel como recomendação de investimento.")

portfolio = load_portfolio()
metrics = portfolio_metrics(portfolio)

c1, c2, c3 = st.columns(3)
c1.metric("Patrimônio simulado", f"R$ {metrics['equity']:.2f}")
c2.metric("Dinheiro disponível", f"R$ {portfolio['cash']:.2f}")
c3.metric("Resultado aberto", f"R$ {metrics['unrealized']:+.2f}")

st.divider()
st.subheader("Radar de mercado")
default_tickers = "ITUB4.SA, PETR4.SA, VALE3.SA, BBAS3.SA, BBDC4.SA"
tickers_text = st.text_input("Ações para acompanhar (Yahoo Finance)", default_tickers)
tickers = [x.strip().upper() for x in tickers_text.split(",") if x.strip()]

if st.button("Atualizar análise", type="primary"):
    st.session_state["refresh"] = True

if tickers:
    with st.spinner("Consultando cotações..."):
        data = get_market_data(tickers)
    if data.empty:
        st.error("Não foi possível obter cotações. Tente novamente mais tarde.")
    else:
        rows = []
        for ticker in tickers:
            if ticker in data.index:
                r = data.loc[ticker]
                signal = generate_signal(ticker)
                rows.append({
                    "Ativo": ticker,
                    "Preço": r.get("price"),
                    "Variação diária (%)": r.get("change_pct"),
                    "Sinal experimental": signal["signal"],
                    "Motivo": signal["reason"]
                })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption("Sinais baseados em médias móveis e momentum simples. Não são previsões nem recomendações.")

st.divider()
st.subheader("Carteira simulada")
positions = portfolio.get("positions", {})
if positions:
    st.dataframe(pd.DataFrame([
        {"Ativo": t, "Quantidade": p["qty"], "Preço médio": p["avg_price"]}
        for t, p in positions.items()
    ]), use_container_width=True, hide_index=True)
else:
    st.info("Ainda não há posições simuladas.")

with st.expander("Simular uma ordem"):
    with st.form("paper_order"):
        ticker = st.text_input("Ticker", "ITUB4.SA").upper().strip()
        side = st.selectbox("Operação", ["COMPRA", "VENDA"])
        qty = st.number_input("Quantidade", min_value=1, max_value=10000, value=1, step=1)
        submitted = st.form_submit_button("Executar ordem simulada")
        if submitted:
            result = execute_paper_order(ticker, side, int(qty))
            if result["ok"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])

st.caption("Próximas versões: alertas, backtesting, regras de risco configuráveis, persistência robusta e avaliação de integração oficial.")
