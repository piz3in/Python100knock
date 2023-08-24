# %%
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

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
# 顧客毎の月利用回数の集計データを作成する
# 1.集計に必要なデータを作成する
# 1-1.usedateをdatetime型に変換する
use_log["usedate"] = pd.to_datetime(use_log["usedate"])

# 1-2.use_month列を作成する
use_log["use_month"] = use_log["usedate"].dt.strftime("%Y-%m")

# 1-3.各顧客の月毎の利用回数を集計したデータフレームを作成する
monthly_use_log = use_log.groupby(["use_month", "customer_id"], as_index=False).count()
monthly_use_log

# %%
# 1-4.不要なusedate列を削除する（usedate列とlog_id列のカウント結果は等しいため）
monthly_use_log.drop("usedate", axis=1, inplace=True)
monthly_use_log

# %%
# 1-5.列名log_idをcountに変更する
monthly_use_log.rename(columns={"log_id": "count"}, inplace=True)
monthly_use_log

# %%
# 2.顧客毎の月利用回数の平均値、中央値、最大値、最小値を集計する
customer_monthly_use_log = (
    monthly_use_log[["customer_id", "count"]]
    .groupby("customer_id")
    .agg(["mean", "median", "max", "min"])
)["count"]
customer_monthly_use_log.reset_index(drop=False, inplace=True)
customer_monthly_use_log

# %%
# 各顧客が定期的（今回は、毎週同じ曜日に利用していることと定義する）に利用しているかどうかのフラグを作成する
# 1.顧客毎に月毎の曜日別の利用回数をカウントする
# 1-1.曜日データを作成する
use_log["weekday"] = use_log["usedate"].dt.weekday
# 1-2.各月の各曜日の利用回数をカウントする
weekday_use_log = use_log.groupby(
    ["customer_id", "use_month", "weekday"], as_index=False
).count()[["customer_id", "use_month", "weekday", "log_id"]]
weekday_use_log.rename(columns={"log_id": "count"}, inplace=True)
weekday_use_log.head()
# %%
# 2.定期利用フラグを作成する
# 2-1.顧客毎に各月の同一曜日の利用回数の最大値を取得する
weekday_use_log = weekday_use_log.groupby("customer_id", as_index=False).max("count")[
    ["customer_id", "count"]
]
weekday_use_log.head()
# %%
# 2-2.最大値が4以上の時にフラグを立てる
weekday_use_log["routine_flg"] = 0
weekday_use_log.loc[weekday_use_log["count"] >= 4, "routine_flg"] = 1
weekday_use_log.head()
# %%
# 顧客データと利用履歴データ(月利用回数の集計データと定期利用フラグ)を結合する
# 1.顧客データと月利用回数の集計データを結合する
join_customer_data = pd.merge(
    join_customer_data, customer_monthly_use_log, how="left", on="customer_id"
)
# 2.顧客データと定期利用フラグを結合する
join_customer_data = pd.merge(
    join_customer_data,
    weekday_use_log[["customer_id", "routine_flg"]],
    how="left",
    on="customer_id",
)
join_customer_data.head()
# %%
# 3.欠損値の確認をする
join_customer_data.isnull().sum()

# %%
# 会員期間を計算する
# 1.会員期間計算用の終了日データ列を作成する
join_customer_data["calc_end_date"] = join_customer_data["end_date"]
join_customer_data["calc_end_date"] = join_customer_data["calc_end_date"].fillna(
    pd.to_datetime("20190430")
)
# 2.会員期間を月単位で算出する
join_customer_data["membership_period"] = 0
for i in range(len(join_customer_data)):
    delta = relativedelta(
        join_customer_data.loc[i, "calc_end_date"],
        join_customer_data.loc[i, "start_date"],
    )
    join_customer_data.loc[i, "membership_period"] = delta.years * 12 + delta.months
join_customer_data.head()
# %%
# 顧客行動の各種統計量を計算する
# 1.顧客毎の月利用回数の平均値、中央値、最大値、最小値の統計量を計算する
join_customer_data[["mean", "median", "max", "min"]].describe()

# %%
# 2.定期利用している(各月の同一曜日の利用回数の最大値が4以上)ユーザーとそうでないユーザーの数の確認
join_customer_data.groupby("routine_flg").count()["customer_id"]

# %%
# 3.会員期間の分布を可視化する
fig = plt.figure()
ax = fig.add_subplot()

ax.hist(join_customer_data["membership_period"])

# %%
