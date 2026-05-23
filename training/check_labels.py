import pandas as pd

df = pd.read_csv(r"D:\sneha\smartshield_new\datasets\processed\url_dataset.csv")

print(df.head())

print("\nUnique labels:")
print(df["label"].unique())