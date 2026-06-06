import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

df = pd.read_excel(r"C:\Users\Naja\Documents\Market Research\UWScraper\Excel Output\6. merged_class.xlsx")

df = df.dropna(subset=["rating", "review_count"])

X = df[["review_count"]]  # count reviews is the independent variable (cause)
y = df["rating"]        # rating is the dependent variable (effect)

model = LinearRegression()
model.fit(X, y)

r2 = model.score(X, y)

plt.figure(figsize=(8, 5))

sns.scatterplot(
    data=df,
    x="review_count",
    y="rating",
    hue="tier",
    alpha=0.6
)

df_sorted = df.sort_values("review_count")
plt.plot(df_sorted["review_count"], model.predict(df_sorted[["review_count"]]), color="darkred")

plt.title("Price vs Rating — Do products with more reviews have better or worse ratings?")
plt.xlabel("Count Reviews")
plt.ylabel("Rating")

plt.text(
    0.05, 0.95,
    f"R² = {r2:.4f}",
    transform=plt.gca().transAxes,
    bbox=dict(facecolor="white", alpha=0.5)
)

plt.tight_layout()
plt.show()
