# %%
import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# データの読み込み
# 1.利用履歴データの読み込み
use_log = pd.read_csv("input/use_log.csv")
use_log.isnull().sum()

# %%
# 2.顧客行動データの読み込み
customer = pd.read_csv("input/join_customer_data.csv")
customer.isnull().sum()

# %%
