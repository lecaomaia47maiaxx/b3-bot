import yfinance as yf
import pandas as pd
import ta
import requests
import time
import os
from datetime import datetime

TOKEN = os.getenv("8430351852:AAF50usp88gBEQ9XAlS98pOCVs8aBNztAqc")
CHAT_ID = os.getenv("8352381582")

ATIVOS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
INTERVALO = "5m"

def enviar_alerta(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem
    }
    requests.post(url, data=payload)

def analisar_ativo(ticker):
    df = yf.download(ticker, period="2d", interval=INTERVALO)

    if df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = pd.Series(df["Close"].values.flatten(), index=df.index)

    df["EMA9"] = ta.trend.ema_indicator(close, window=9)
    df["EMA21"] = ta.trend.ema_indicator(close, window=21)
    df["EMA200"] = ta.trend.ema_indicator(close, window=200)
    df["RSI"] = ta.momentum.rsi(close, window=14)

    ultimo = df.iloc[-1]

    ema9 = float(ultimo["EMA9"])
    ema21 = float(ultimo["EMA21"])
    ema200 = float(ultimo["EMA200"])
    preco = float(ultimo["Close"])
    rsi = float(ultimo["RSI"])

    tendencia = "LATERAL"

    if ema9 > ema21 and preco > ema200 and rsi > 55:
        tendencia = "ALTISTA"
    elif ema9 < ema21 and preco < ema200 and rsi < 45:
        tendencia = "BAIXISTA"

    mensagem = f"""
🚨 {ticker.replace('.SA','')}
Preço: R$ {round(preco,2)}
Tendência: {tendencia}
RSI: {round(rsi,2)}
Horário: {datetime.now().strftime('%H:%M:%S')}
"""

    return mensagem

def monitorar():
    print("Robô iniciado...")

    while True:
        print("Analisando ativos...")
        for ativo in ATIVOS:
            alerta = analisar_ativo(ativo)
            if alerta:
                enviar_alerta(alerta)
        print("Aguardando próxima análise...")
        time.sleep(300)

if __name__ == "__main__":
    monitorar()
