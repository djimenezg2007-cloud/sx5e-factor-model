"""
Download Euro Stoxx 50 constituent prices and compute performance stats.

Usage:
    pip install yfinance pandas
    python sx5e_constituents.py

Outputs (written next to this script):
    sx5e_prices.csv       wide: Date x ticker, adjusted close
    sx5e_returns.csv      wide: Date x ticker, daily simple returns
    sx5e_summary.csv      one row per stock: start, end, total return, vol, max DD
"""

import pandas as pd
import yfinance as yf

# antes de tu fecha AS_OF (2025-09-08) para el ranking point-in-time
START = "2025-01-01"
# yfinance end is exclusive; hasta hoy para medir el rendimiento posterior
END = "2026-09-17"
OUT_PREFIX = "sx5e"

# Alphabetical by ticker, so positional index matches the 0-47 ordering you
# already have. The benchmark is kept separate so it doesn't shift those indices.
TICKERS = {
    "ABI.BR": "AB InBev",            # 0
    "AD.AS": "Ahold Delhaize",       # 1
    "ADS.DE": "Adidas",              # 2
    "ADYEN.AS": "Adyen",             # 3
    "AI.PA": "Air Liquide",          # 4
    "AIR.PA": "Airbus",              # 5
    "ALV.DE": "Allianz",             # 6
    "ASML.AS": "ASML",               # 7
    "BAS.DE": "BASF",                # 8
    "BAYN.DE": "Bayer",              # 9
    "BBVA.MC": "BBVA",               # 10
    "BMW.DE": "BMW",                 # 11
    "BN.PA": "Danone",               # 12
    "BNP.PA": "BNP Paribas",         # 13
    "CS.PA": "AXA",                  # 14

    "DB1.DE": "Deutsche Boerse",     # 15
    "DG.PA": "Vinci",                # 16
    "DHL.DE": "DHL Group",           # 17
    "DTE.DE": "Deutsche Telekom",    # 18
    "EL.PA": "EssilorLuxottica",     # 19
    "ENEL.MI": "Enel",               # 20
    "ENI.MI": "Eni",                 # 21
    "IBE.MC": "Iberdrola",           # 22
    "IFX.DE": "Infineon",            # 23
    "INGA.AS": "ING Groep",          # 24
    "ISP.MI": "Intesa Sanpaolo",     # 25
    "ITX.MC": "Inditex",             # 26
    "KER.PA": "Kering",              # 27
    "MBG.DE": "Mercedes-Benz",       # 28
    "MUV2.DE": "Munich Re",          # 29
    "NDA-FI.HE": "Nordea",           # 30
    "NOKIA.HE": "Nokia",             # 31
    "OR.PA": "L'Oreal",              # 32
    "PRX.AS": "Prosus",              # 33
    "RACE.MI": "Ferrari",            # 34
    "RI.PA": "Pernod Ricard",        # 35
    "RMS.PA": "Hermes",              # 36
    "SAF.PA": "Safran",              # 37
    "SAN.MC": "Banco Santander",     # 38
    "SAN.PA": "Sanofi",              # 39
    "SAP.DE": "SAP",                 # 40
    "SGO.PA": "Saint-Gobain",        # 41
    "SIE.DE": "Siemens",             # 42
    "STLAM.MI": "Stellantis",        # 43
    "SU.PA": "Schneider Electric",   # 44
    "TTE.PA": "TotalEnergies",       # 45
    "UCG.MI": "UniCredit",           # 46
    "VOW3.DE": "Volkswagen",         # 47
}

BENCHMARK = {"^STOXX50E": "EURO STOXX 50"}   # price index, no dividends


def download(tickers, start, end):
    raw = yf.download(
        list(tickers),
        start=start,
        end=end,
        auto_adjust=True,      # adjusted for splits/dividends
        progress=False,
        group_by="column",
    )
    px = raw["Close"].copy()

    # Drop anything that came back empty (bad ticker, delisted, wrong suffix)
    empty = [c for c in px.columns if px[c].isna().all()]
    if empty:
        print("No data, dropped:", empty)
        px = px.drop(columns=empty)

    # Different exchanges have different holidays; forward-fill gaps, then drop
    # rows where the whole market was shut.
    px = px.dropna(how="all").ffill()

    # Keep the Yahoo tickers as column headers so they join against your
    # fundamentals file. Column order follows the dict, not yfinance's.
    px = px[[t for t in tickers if t in px.columns]]
    px.index.name = "date"
    return px


def summarize(px):
    rets = px.pct_change()
    cum = px / px.iloc[0]
    dd = cum / cum.cummax() - 1

    out = pd.DataFrame({
        "start_price": px.iloc[0],
        "end_price": px.iloc[-1],
        "total_return_pct": (px.iloc[-1] / px.iloc[0] - 1) * 100,
        "ann_vol_pct": rets.std() * (252 ** 0.5) * 100,
        "max_drawdown_pct": dd.min() * 100,
        "n_obs": px.notna().sum(),
    })
    return rets, out.sort_values("total_return_pct", ascending=False)


if __name__ == "__main__":
    prices = download({**TICKERS, **BENCHMARK}, START, END)
    returns, summary = summarize(prices)

    prices.to_csv(f"{OUT_PREFIX}_prices.csv", float_format="%.4f")
    
    returns.to_csv(f"{OUT_PREFIX}_returns.csv", float_format="%.6f")
    summary.to_csv(f"{OUT_PREFIX}_summary.csv", float_format="%.4f")

    print(f"\n{len(prices.columns)} series, {len(prices)} trading days "
          f"({prices.index[0].date()} to {prices.index[-1].date()})\n")
    print(summary.round(2).to_string())
