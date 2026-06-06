import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

df = pd.read_excel(r"C:\Users\Naja\Documents\Market Research\UWScraper\Excel Output\amazon_bestbuy_tokopedia.xlsx")

df = df.dropna(subset=["rating", "price_idr"])
df = df[df["price_idr"] <= 40_000_000]  # remove outliers
df = df[df["rating"] <= 5]  # remove outliers

X = df[["price_idr"]]  # price is the independent variable (cause)
y = df["rating"]        # rating is the dependent variable (effect)

model = LinearRegression()
model.fit(X, y)

r2 = model.score(X, y)

plt.figure(figsize=(8, 5))

sns.scatterplot(
    data=df,
    x="price_idr",
    y="rating",
    hue="source",
    alpha=0.6
)

df_sorted = df.sort_values("price_idr")
plt.plot(df_sorted["price_idr"], model.predict(df_sorted[["price_idr"]]), color="darkred")

plt.title("Price vs Rating — Does paying more mean better rated?")
plt.xlabel("Price (IDR)")
plt.ylabel("Rating")

plt.text(
    0.05, 0.95,
    f"R² = {r2:.4f}",
    transform=plt.gca().transAxes,
    bbox=dict(facecolor="white", alpha=0.5)
)

plt.tight_layout()
plt.show()