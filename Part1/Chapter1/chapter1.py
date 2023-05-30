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
