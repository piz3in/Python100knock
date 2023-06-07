# %%
import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# データの読み込み
use_log = pd.read_csv("input/use_log.csv")
print(len(use_log))
use_log.head()

# %%
customer_master = pd.read_csv("input/customer_master.csv")
print(len(customer_master))
customer_master.head()

# %%
class_master = pd.read_csv("input/class_master.csv")
print(len(class_master))
class_master.head()

# %%
campaign_master = pd.read_csv("input/campaign_master.csv")
print(len(campaign_master))
campaign_master.head()

# %%
# 顧客データにクラスマスターデータとキャンペーンマスターデータを結合する
# 1.クラスマスターデータを結合する
join_customer_data = pd.merge(customer_master, class_master, how="left", on="class")
print(len(join_customer_data))
join_customer_data.head()

# %%
# 2.キャンペーンマスターデータを結合する
join_customer_data = pd.merge(
    join_customer_data, campaign_master, how="left", on="campaign_id"
)
print(len(join_customer_data))
join_customer_data.head()

# %%
# 3.欠損値がないかを確認する
join_customer_data.isnull().sum()

# %%
