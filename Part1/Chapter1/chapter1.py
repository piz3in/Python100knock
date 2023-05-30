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
