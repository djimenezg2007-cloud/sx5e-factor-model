import numpy as np
import pandas as pd

# ===== RUTAS (todos los archivos en la carpeta del proyecto) =====
RECON = "statements_FY2024_FY2023_ALL.csv"
OLD = "fundamentales_EUROSTOXX50.csv"
PRICES = "sx5e_prices.csv"
AS_OF = pd.Timestamp("2025-09-08")
CUR, PREV = "FY2024", "FY2023"

# ===== 1. largo -> ancho, una tabla por año fiscal =====
long = pd.read_csv(RECON)


def wide(fy):
    return long[long["fiscal_year"] == fy].pivot_table(
        index="ticker", columns="line_item", values="value", aggfunc="first")


cur, prev = wide(CUR), wide(PREV)


def c(w, name):   # si falta la partida (p.ej. financieros) -> NaN, y tu num/den la descarta
    return w[name] if name in w.columns else pd.Series(index=w.index, dtype=float)


# ===== 2. reconstruir con TUS nombres de columna exactos =====
f = pd.DataFrame(index=cur.index)

# --- ratios estado/estado: neutrales a divisa (financieros NaN por diseño) ---
f["returnOnEquity"] = c(cur, "Net Income") / c(cur, "Stockholders Equity")
f["returnOnAssets"] = c(cur, "Net Income") / c(cur, "Total Assets")
f["profitMargins"] = c(cur, "Net Income") / c(cur, "Total Revenue")
f["operatingMargins"] = c(cur, "Operating Income") / c(cur, "Total Revenue")
f["grossMargins"] = c(cur, "Gross Profit") / c(cur, "Total Revenue")
f["currentRatio"] = c(cur, "Current Assets") / c(cur, "Current Liabilities")
f["debtToEquity"] = c(cur, "Total Debt") / c(cur, "Stockholders Equity") * 100
f["earningsGrowth"] = c(cur, "Net Income") / c(prev, "Net Income") - 1
f["salesGrowth"] = c(cur, "Total Revenue") / c(prev, "Total Revenue") - 1

# --- ratios con precio: precio A FECHA AS_OF ---
px = pd.read_csv(PRICES, index_col="date", parse_dates=True).sort_index()
# último cierre en/antes de AS_OF
price = px.loc[:AS_OF].iloc[-1].reindex(f.index)
shares = c(cur, "Diluted Average Shares")
mktcap = price * shares
f["marketCap"] = mktcap
f["trailingPE"] = price / c(cur, "Diluted EPS")
f["priceToBook"] = price / (c(cur, "Stockholders Equity") / shares)
f["priceToSalesTrailing12Months"] = mktcap / c(cur, "Total Revenue")
f["enterpriseValue"] = mktcap + \
    c(cur, "Total Debt") - c(cur, "Cash And Cash Equivalents")
f["enterpriseToEbitda"] = f["enterpriseValue"] / c(cur, "EBITDA")
f["dividendYield"] = c(cur, "Cash Dividends Paid").abs() / mktcap

# --- no reconstruibles point-in-time -> NaN, tu num/den renormaliza ---
f["forwardPE"] = np.nan
f["beta"] = np.nan

# ===== 3. sector desde tu archivo viejo (el sector no cambia) =====
f["sector"] = pd.read_csv(OLD).set_index("ticker")["sector"].reindex(f.index)

# ===== 4. guardar =====
f.reset_index().to_csv("fundamentales_EUROSTOXX50_PIT.csv", index=False)
print("escrito:", f.shape[0], "tickers")
