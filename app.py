
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import io

st.set_page_config(page_title="App Bolsa", layout="wide")
st.title("App de Bolsa - 35 valores NYSE")

tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "WMT", "UNH",
    "KO", "PEP", "V", "BAC", "HD", "DIS", "MA", "PYPL", "INTC", "IBM",
    "CSCO", "ORCL", "NFLX", "T", "CVX", "PFE", "XOM", "C", "MCD", "BA",
    "ABT", "CRM", "MRK", "QCOM", "NKE"
]

@st.cache_data(ttl=3600)
def obtener_datos(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="90d")
            info = stock.info
            if len(hist) >= 7:
                hoy = (hist["Close"][-1] - hist["Open"][-1]) / hist["Open"][-1] * 100
                semana = (hist["Close"][-1] - hist["Close"][-6]) / hist["Close"][-6] * 100
                ytd = (hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0] * 100
                data.append({
                    "Ticker": ticker,
                    "Nombre": info.get("shortName", ""),
                    "Sector": info.get("sector", "N/A"),
                    "País": info.get("country", "N/A"),
                    "Precio actual": round(hist["Close"][-1], 2),
                    "Cambio Día (%)": round(hoy, 2),
                    "Cambio Semana (%)": round(semana, 2),
                    "Cambio YTD (%)": round(ytd, 2)
                })
        except:
            continue
    return pd.DataFrame(data)

df = obtener_datos(tickers)

# Mostrar datos si están disponibles
if not df.empty:
    for col, label in [
        ("Cambio Día (%)", "📅 Variación del Día"),
        ("Cambio Semana (%)", "📅 Variación de la Semana"),
        ("Cambio YTD (%)", "📅 Variación del Año (YTD)")
    ]:
        if col in df.columns:
            st.subheader(label)
            st.dataframe(df.sort_values(col, ascending=False), use_container_width=True)
        else:
            st.warning(f"No se pudo calcular la columna: {col}")
else:
    st.warning("No se pudieron obtener datos para los tickers seleccionados.")

# Filtro
st.subheader("🔍 Filtrar por nombre o ticker")
busqueda = st.text_input("Escribe parte del nombre o ticker para filtrar:")

if busqueda and "Ticker" in df.columns:
    df_filtrado = df[df["Ticker"].str.contains(busqueda.upper(), na=False)]
else:
    df_filtrado = df

if not df_filtrado.empty and "Cambio Día (%)" in df_filtrado.columns:
    st.subheader("📋 Resultados filtrados")
    st.dataframe(df_filtrado.sort_values("Cambio Día (%)", ascending=False), use_container_width=True)
else:
    st.warning("No hay resultados para mostrar con los filtros aplicados.")

# Exportar
st.subheader("📥 Exportar a Excel")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Datos Bolsa")
st.download_button(
    label="📤 Descargar Excel",
    data=buffer,
    file_name=f"datos_bolsa_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Gráfico por ticker
if not df.empty:
    st.subheader("📊 Evolución del precio con media 200 sesiones")
    seleccion = st.selectbox("Selecciona un ticker:", df["Ticker"])
    if seleccion:
        hist = yf.Ticker(seleccion).history(period="1y")
        hist["Media 50"] = hist["Close"].rolling(50).mean()
        hist["Media 200"] = hist["Close"].rolling(200).mean()
        st.line_chart(hist[["Close", "Media 50", "Media 200"]], use_container_width=True, height=300)
