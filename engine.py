import os, json
from pathlib import Path
import pandas as pd
import yfinance as yf

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
INITIAL_CASH = 200.00

def load_portfolio():
    if not PORTFOLIO_FILE.exists():
        p = {"cash": INITIAL_CASH, "positions": {}, "history": []}
        save_portfolio(p)
        return p
    with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_portfolio(p):
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

def get_market_data(tickers):
    rows = []
    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(period="5d", interval="1d", auto_adjust=True)
            if len(hist) < 2:
                continue
            price = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            rows.append({
                "ticker": ticker,
                "price": price,
                "change_pct": ((price / previous) - 1) * 100 if previous else 0
            })
        except Exception:
            continue
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).set_index("ticker")

def generate_signal(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="6mo", interval="1d", auto_adjust=True)
        close = hist["Close"].dropna()
        if len(close) < 50:
            return {"signal": "SEM DADOS", "reason": "Histórico insuficiente"}
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        last = close.iloc[-1]
        prior = close.iloc[-6]
        momentum = (last / prior) - 1 if prior else 0

        if last > sma20 > sma50 and momentum > 0:
            return {"signal": "TENDÊNCIA POSITIVA", "reason": "Preço acima das médias de 20 e 50 dias; momentum positivo"}
        if last < sma20 < sma50 and momentum < 0:
            return {"signal": "TENDÊNCIA NEGATIVA", "reason": "Preço abaixo das médias; momentum negativo"}
        return {"signal": "NEUTRO", "reason": "Critérios de tendência não alinhados"}
    except Exception:
        return {"signal": "INDISPONÍVEL", "reason": "Falha ao consultar dados"}

def current_price(ticker):
    hist = yf.Ticker(ticker).history(period="5d", interval="1d", auto_adjust=True)
    if hist.empty:
        raise ValueError("Cotação indisponível")
    return float(hist["Close"].dropna().iloc[-1])

def execute_paper_order(ticker, side, qty):
    p = load_portfolio()
    try:
        price = current_price(ticker)
    except Exception:
        return {"ok": False, "message": "Não foi possível obter o preço do ativo."}

    value = price * qty
    positions = p["positions"]

    if side == "COMPRA":
        if value > p["cash"]:
            return {"ok": False, "message": f"Saldo insuficiente. Ordem: R$ {value:.2f}; disponível: R$ {p['cash']:.2f}."}
        old = positions.get(ticker, {"qty": 0, "avg_price": 0.0})
        new_qty = old["qty"] + qty
        avg = ((old["qty"] * old["avg_price"]) + value) / new_qty
        positions[ticker] = {"qty": new_qty, "avg_price": avg}
        p["cash"] -= value
    else:
        old = positions.get(ticker)
        if not old or old["qty"] < qty:
            return {"ok": False, "message": "Quantidade insuficiente para vender na carteira simulada."}
        old["qty"] -= qty
        p["cash"] += value
        if old["qty"] == 0:
            del positions[ticker]

    p["history"].append({"ticker": ticker, "side": side, "qty": qty, "price": price, "value": value})
    save_portfolio(p)
    return {"ok": True, "message": f"{side} simulada: {qty} {ticker} a R$ {price:.2f} (total R$ {value:.2f})."}

def portfolio_metrics(p):
    market_value = 0.0
    cost_value = 0.0
    for ticker, pos in p.get("positions", {}).items():
        try:
            price = current_price(ticker)
            market_value += price * pos["qty"]
            cost_value += pos["avg_price"] * pos["qty"]
        except Exception:
            market_value += pos["avg_price"] * pos["qty"]
            cost_value += pos["avg_price"] * pos["qty"]
    return {
        "equity": p["cash"] + market_value,
        "unrealized": market_value - cost_value
    }
