# %%
import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# データの読みこみ
customer_master = pd.read_csv("01_input/customer_master.csv")
print("customer_master:")
customer_master.head()

# %%
item_master = pd.read_csv("01_input/item_master.csv")
print("item_master:")
item_master.head()

# %%
transaction_1 = pd.read_csv("01_input/transaction_1.csv")
transaction_2 = pd.read_csv("01_input/transaction_2.csv")

print("transaction:")
transaction_1.head()

# %%
transaction_detail_1 = pd.read_csv("01_input/transaction_detail_1.csv")
transaction_detail_2 = pd.read_csv("01_input/transaction_detail_2.csv")

print("transaction_detail:")
transaction_detail_1.head()

# %%
# 複数ファイルにわたっているデータ（transaction, transaction_detail）の結合(縦の結合）
transaction = pd.concat([transaction_1, transaction_2], ignore_index=True)
print(len(transaction_1))
print(len(transaction_2))
print(len(transaction))

# %%
transaction_detail = pd.concat(
    [transaction_detail_1, transaction_detail_2], ignore_index=True
)
print(len(transaction_detail_1))
print(len(transaction_detail_2))
print(len(transaction_detail))

# %%
# dataframe同士の結合（横の結合）
# 最もデータ粒度が細かいtransaction_detailを主軸とする
# 1.transaction_detailにtransactionを結合する
# （1.追加するデータ列：[payment_date, customer_id], 2.共通するデータ列：transaction_id）
join_transaction = pd.merge(
    transaction_detail,
    transaction[["transaction_id", "payment_date", "customer_id"]],
    how="left",
    on="transaction_id",
)
print("join_transaction:")
join_transaction.head()

# %%
print(f"transaction_detail len:{len(transaction_detail)}")
print(f"transaction len:{len(transaction)}")
print(f"join_transaction len: {len(join_transaction)}")

# %%
# 2.join_transactionにマスターデータ（customer_master, item_master）を結合する
# customer_masterデータの結合
# (1.追加するデータ列：すべて, 2.共通するデータ列：customer_id)
join_data = pd.merge(join_transaction, customer_master, how="left", on="customer_id")
print("join_data:")
join_data.head()

# %%
print(f"join_transaction len:{len(join_transaction)}")
print(f"customer_master len:{len(customer_master)}")
print(f"join_data len:{len(join_data)}")

# %%
# item_masterデータの結合
# (1.追加するデータ列：すべて, 2.共通するデータ列:item_id)
join_data = pd.merge(join_data, item_master, how="left", on="item_id")
join_data.head()

# %%
print(f"item_master len:{len(item_master)}")
print(f"join_data len:{len(join_data)}")

# %%
# 売上のデータ列を作成する
join_data["price"] = join_data["item_price"] * join_data["quantity"]
join_data[["item_price", "quantity", "price"]].head()

# %%
# 売上のデータ列の検算
print(transaction["price"].sum())
print(join_data["price"].sum())

# %%
# データ欠損数の確認
join_data.isnull().sum()

# %%
# データ集計の出力
join_data.describe()

# %%
# データ取得期間の把握
print("first date: " + join_data["payment_date"].min())
print("last  date: " + join_data["payment_date"].max())

# %%
# 月別で売上データを集計する
# 1.payment_dateのデータ型を確認する
join_data.dtypes

# %%
# 2.payment_dateのデータ型をdatetime型に変換する
join_data["payment_date"] = pd.to_datetime(join_data["payment_date"])

# 3.payment_dateから年月のみを抽出したデータ列(payment_month)を作成する
join_data["payment_month"] = join_data["payment_date"].dt.strftime("%Y-%m")
join_data[["payment_date", "payment_month"]].head()

# %%
# 4.月毎に売上データを集計する
join_data[["payment_month", "price"]].groupby("payment_month").sum()

# %%
# 月別、商品別で売上データを集計する
join_data[["payment_month", "item_name", "price", "quantity"]].groupby(
    ["payment_month", "item_name"]
).sum()

# %%
# pivot_table関数を使って集計結果を見やすく表示する
pd.pivot_table(
    join_data,
    index="item_name",
    columns="payment_month",
    values=["price", "quantity"],
    aggfunc="sum",
)

# %%
