import pandas as pd


def main():
    df = pd.read_csv("./orders.csv")
    result = df[
        (df["Category"] == "Electronics")
        & (df["Price"] > 300)
        & (df["PaymentMethod"] == "PayPal")
    ]

    result.to_csv("results.csv", index=False)


if __name__ == "__main__":
    main()
