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
# 顧客データの基礎集計をする
# 1.会員区分毎の顧客数を確認する
join_customer_data.groupby("class_name")["customer_id"].count()

# %%
# 2.キャンペーン区分毎の顧客数を確認する
join_customer_data.groupby("campaign_name")["customer_id"].count()

# %%
# 3.性別毎の顧客数を確認する
join_customer_data.groupby("gender")["customer_id"].count()

# %%
# 4.退会済みの顧客数を確認する
join_customer_data.groupby("is_deleted")["customer_id"].count()

# %%
# 5.2018年度に入会した顧客数を確認する
# 5-1.start_dateをdatetime型に変換する
join_customer_data["start_date"] = pd.to_datetime(join_customer_data["start_date"])
join_customer_data.dtypes

# %%
# 5-2.2018年度に入会した顧客数をカウントする
join_customer_data.loc[
    ("2018-04-01" <= join_customer_data["start_date"])
    & (join_customer_data["start_date"] <= "2019-03-31"),
    "customer_id",
].count()

# %%
# 最新月に在籍している顧客データの基礎集計をする
# 1.最新月に月末まで在籍している（end_dateが2019-03-31以降またはend_dateのデータがない）顧客のデータを選択する
# 1-1.end_dateをdatetime型に変換する
join_customer_data["end_date"] = pd.to_datetime(join_customer_data["end_date"])
join_customer_data.head()

# %%
# 1-2.最新月に在籍している顧客のデータを選択する
customers_exist_latest_month = join_customer_data.loc[
    (join_customer_data["end_date"] >= "2019-03-31")
    | (join_customer_data["end_date"].isnull())
]
print(len(customers_exist_latest_month))
customers_exist_latest_month

# %%
# 1-3.絞り込みの検証を行う（end_dateが2019-03-31とNaTのみかを確認する）
customers_exist_latest_month["end_date"].unique()

# %%
# 2.基礎集計をする
# 2-1.会員区分毎の顧客数を確認する
customers_exist_latest_month.groupby("class_name")["customer_id"].count()

# %%
# 2-2.キャンペーン区分毎の顧客数を確認する
customers_exist_latest_month.groupby("campaign_name")["customer_id"].count()

# %%
# 2-3.性別毎の顧客数を確認する
customers_exist_latest_month.groupby("gender")["customer_id"].count()

# %%
