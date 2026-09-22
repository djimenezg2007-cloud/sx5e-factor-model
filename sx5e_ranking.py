import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


sx5e_fundamentals = pd.read_csv("C:/Users/djime/Forecasts/Python/sx5e Factor Model/fundamentales_EUROSTOXX50_PIT.csv")
sx5e_prices = pd.read_csv("C:/Users/djime/Forecasts/Python/sx5e Factor Model/sx5e_prices.csv",
                  index_col="date", parse_dates=True)

AS_OF = pd.Timestamp("2025-09-08")
sx5e_prices = sx5e_prices.loc[AS_OF:]

# valuation - lower is better
sx5e_fundamentals["trailing_PE_percent"] = sx5e_fundamentals["trailingPE"].rank(
    pct=True, ascending=False)
sx5e_fundamentals["forward_PE_percent"] = sx5e_fundamentals["forwardPE"].rank(
    pct=True, ascending=False)
sx5e_fundamentals["fpe_tpe"] = sx5e_fundamentals["trailingPE"] / \
    sx5e_fundamentals["forwardPE"]
sx5e_fundamentals["priceToBook_percent"] = sx5e_fundamentals["priceToBook"].rank(
    pct=True, ascending=False)
sx5e_fundamentals["priceToSalesTrailing12Months_percent"] = sx5e_fundamentals["priceToSalesTrailing12Months"].rank(
    pct=True, ascending=False)
sx5e_fundamentals["enterpriseToEbitda_percent"] = sx5e_fundamentals["enterpriseToEbitda"].rank(
    pct=True, ascending=False)

valuation_wheight = {"priceToBook_percent": 0.1725,
                     "priceToSalesTrailing12Months_percent": 0.2425,
                     "forward_PE_percent": 0.2225,
                     "trailing_PE_percent": 0.2225,
                     "enterpriseToEbitda_percent": 0.15
                     }

num = 0
den = 0
for col, w in valuation_wheight.items():
    num = num + sx5e_fundamentals[col].fillna(0) * w
    den = den + sx5e_fundamentals[col].notna() * w

eurostoxx_valuation_score = (num / den)


# Dividend - higher is better
sx5e_fundamentals["dividendYield_percent"] = sx5e_fundamentals["dividendYield"].fillna(0).rank(
    pct=True, ascending=True)
eurostoxx_dividend_score = sx5e_fundamentals["dividendYield_percent"]

# Quality - higher is better


sx5e_fundamentals["returnOnEquity_percent"] = sx5e_fundamentals["returnOnEquity"].rank(
    pct=True, ascending=True)
sx5e_fundamentals["returnOnAssets_percent"] = sx5e_fundamentals["returnOnAssets"].rank(
    pct=True, ascending=True)
sx5e_fundamentals["profitMargins_percent"] = sx5e_fundamentals["profitMargins"].rank(
    pct=True, ascending=True)
sx5e_fundamentals["operatingMargins_percent"] = sx5e_fundamentals["operatingMargins"].rank(
    pct=True, ascending=True)


quality_weights = {"returnOnEquity_percent": 0.25,
                   "returnOnAssets_percent": 0.3,
                   "profitMargins_percent": 0.25,
                   "operatingMargins_percent": 0.2
                   }

num = 0
den = 0
for col, w in quality_weights.items():
    num = num + sx5e_fundamentals[col].fillna(0) * w
    den = den + sx5e_fundamentals[col].notna() * w


eurostoxx_quality_score = (num/den)


# Balance sheet
sx5e_fundamentals["debtToEquity_percent"] = sx5e_fundamentals["debtToEquity"].rank(
    pct=True, ascending=False)
sx5e_fundamentals["currentRatio_percent"] = sx5e_fundamentals["currentRatio"].rank(
    pct=True, ascending=True)

sx5e_fundamentals["debtToAssets_percent"] = ((sx5e_fundamentals["debtToEquity"] / (100)) * (sx5e_fundamentals["returnOnAssets"] / sx5e_fundamentals["returnOnEquity"])).rank(pct=True, ascending=False)
sx5e_fundamentals["netDebtToEbitda_percent"] = (sx5e_fundamentals["enterpriseToEbitda"] * (
    1 - sx5e_fundamentals["marketCap"] / sx5e_fundamentals["enterpriseValue"])).rank(pct=True, ascending=False)


BS_wheights = {"debtToAssets_percent": 0.25,
               "netDebtToEbitda_percent": 0.15,
               "debtToEquity_percent": 0.35,
               "currentRatio_percent": 0.25}

num = 0
den = 0
for col, w in BS_wheights.items():
    num = num + sx5e_fundamentals[col].fillna(0) * w
    den = den + sx5e_fundamentals[col].notna() * w

eurostoxx_BS_score = num / den

# Growth - higher is better
sx5e_fundamentals["earningsGrowth_percent"] = sx5e_fundamentals["earningsGrowth"].rank(
    pct=True, ascending=True)
sx5e_fundamentals["fpe_tpe_percent"] = sx5e_fundamentals["fpe_tpe"].rank(
    pct=True, ascending=True)
sx5e_fundamentals["salesGrowth_percent"] = sx5e_fundamentals["salesGrowth"].rank(
    pct=True, ascending=True)

weights = {
    "fpe_tpe_percent": 0.35,
    "earningsGrowth_percent": 0.30,
    "salesGrowth_percent": 0.35,
}

num = 0
den = 0
for col, w in weights.items():
    num = num + sx5e_fundamentals[col].fillna(0) * w
    den = den + sx5e_fundamentals[col].notna() * w

eurostoxx_growth_score = num / den

sx5e_fundamentals["score"] = np.where(sx5e_fundamentals["sector"] == "Financial Services", eurostoxx_growth_score * 0.35 + eurostoxx_quality_score *
                                 0.3 + eurostoxx_valuation_score * 0.25 + eurostoxx_dividend_score * 0.1, eurostoxx_growth_score * 0.28 + eurostoxx_quality_score *
                                 0.24 + eurostoxx_valuation_score * 0.2 + eurostoxx_dividend_score * 0.08 + eurostoxx_BS_score * 0.2)

eurostoxx = sx5e_fundamentals.sort_values("score", ascending=False)
print(eurostoxx[["ticker", "score"]])


# Split into octiles (all 48 stocks)

# Split into deciles (all 48 stocks)

Q1 = eurostoxx[0:5]
Q2 = eurostoxx[5:10]
Q3 = eurostoxx[10:15]
Q4 = eurostoxx[15:20]
Q5 = eurostoxx[20:25]
Q6 = eurostoxx[25:30]
Q7 = eurostoxx[30:35]
Q8 = eurostoxx[35:40]
Q9 = eurostoxx[40:45]
Q10 = eurostoxx[45:]

# Get performance of each decile

Index_1 = Q1["ticker"]
Q1_prices = sx5e_prices[Index_1]
Q1_performance = Q1_prices.pct_change()
Q1_norm = (Q1_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_2 = Q2["ticker"]
Q2_prices = sx5e_prices[Index_2]
Q2_performance = Q2_prices.pct_change()
Q2_norm = (Q2_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_3 = Q3["ticker"]
Q3_prices = sx5e_prices[Index_3]
Q3_performance = Q3_prices.pct_change()
Q3_norm = (Q3_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_4 = Q4["ticker"]
Q4_prices = sx5e_prices[Index_4]
Q4_performance = Q4_prices.pct_change()
Q4_norm = (Q4_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_5 = Q5["ticker"]
Q5_prices = sx5e_prices[Index_5]
Q5_performance = Q5_prices.pct_change()
Q5_norm = (Q5_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_6 = Q6["ticker"]
Q6_prices = sx5e_prices[Index_6]
Q6_performance = Q6_prices.pct_change()
Q6_norm = (Q6_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_7 = Q7["ticker"]
Q7_prices = sx5e_prices[Index_7]
Q7_performance = Q7_prices.pct_change()
Q7_norm = (Q7_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_8 = Q8["ticker"]
Q8_prices = sx5e_prices[Index_8]
Q8_performance = Q8_prices.pct_change()
Q8_norm = (Q8_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_9 = Q9["ticker"]
Q9_prices = sx5e_prices[Index_9]
Q9_performance = Q9_prices.pct_change()
Q9_norm = (Q9_performance.mean(axis=1).fillna(0) + 1).cumprod()

Index_10 = Q10["ticker"]
Q10_prices = sx5e_prices[Index_10]
Q10_performance = Q10_prices.pct_change()
Q10_norm = (Q10_performance.mean(axis=1).fillna(0) + 1).cumprod()


# Perform spearman rank correlation (deciles)

curves = pd.DataFrame({
    "Q1": Q1_norm,
    "Q2": Q2_norm,
    "Q3": Q3_norm,
    "Q4": Q4_norm,
    "Q5": Q5_norm,
    "Q6": Q6_norm,
    "Q7": Q7_norm,
    "Q8": Q8_norm,
    "Q9": Q9_norm,
    "Q10": Q10_norm,
})
predicted_returns = pd.Series({"Q1": 10,
                               "Q2": 9,
                               "Q3": 8,
                               "Q4": 7,
                               "Q5": 6,
                               "Q6": 5,
                               "Q7": 4,
                               "Q8": 3,
                               "Q9": 2,
                               "Q10": 1
                               })
final_return = curves.iloc[-1]
realized_return = final_return.sort_values()
spearman = realized_return.corr(predicted_returns, method="spearman")

print("Decile Spearman Correlation:", spearman)


# Checking performance of each stock

indv_performance = ((((sx5e_prices.pct_change().fillna(0) + 1).cumprod()).iloc[-1]).drop("^STOXX50E")).sort_values()
predicted_indv_returns = eurostoxx.set_index("ticker")["score"]
indv_spearman = predicted_indv_returns.corr(indv_performance, method="spearman")
print("Individual Spearman Correlation:", indv_spearman)


# Plotting performance of each decile

fig, ax = plt.subplots(figsize=(10, 6))
Q1_norm.plot(ax=ax, label="Q1 (highest score)")
Q2_norm.plot(ax=ax, label="Q2")
Q3_norm.plot(ax=ax, label="Q3")
Q4_norm.plot(ax=ax, label="Q4")
Q5_norm.plot(ax=ax, label="Q5")
Q6_norm.plot(ax=ax, label="Q6")
Q7_norm.plot(ax=ax, label="Q7")
Q8_norm.plot(ax=ax, label="Q8")
Q9_norm.plot(ax=ax, label="Q9")
Q10_norm.plot(ax=ax, label="Q10 (lowest score)")

ax.set_title("Cumulative return by decile")
ax.set_ylabel("Growth since 8 Sep 2025")
ax.axhline(1.0, color="grey", linewidth=0.8)
ax.legend()
plt.savefig("decile_performance.png", dpi=150, bbox_inches="tight")
plt.show()