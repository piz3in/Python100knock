# %%
import os
import pandas as pd
from dateutil.relativedelta import relativedelta

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# データの読み込み
# 顧客行動データ
customer = pd.read_csv("input/join_customer_data.csv")
customer.head()

# %%
# 顧客毎の月別の利用回数データ
monthly_use_log = pd.read_csv("input/use_log_months.csv")
monthly_use_log.head()

# %%
# 当月と過去1ヶ月の利用回数を集計したデータの作成
# 6ヶ月未満で退会する顧客もいるため、予測に用いる過去の利用履歴データの期間を第４章より短くする
year_months = list(monthly_use_log["usemonth"].unique())

use_log = pd.DataFrame()

# 過去1ヶ月のデータがある2018年5月以降のデータで作成する
for i in range(1, len(year_months)):
    tmp = monthly_use_log[monthly_use_log["usemonth"] == year_months[i]].copy()
    tmp.rename(columns={"count": "count_0"}, inplace=True)

    tmp_before = monthly_use_log[
        monthly_use_log["usemonth"] == year_months[i - 1]
    ].copy()
    tmp_before.drop("usemonth", axis=1, inplace=True)
    tmp_before.rename(columns={"count": "count_1"}, inplace=True)

    tmp = pd.merge(tmp, tmp_before, how="left", on="customer_id")

    use_log = pd.concat([use_log, tmp], ignore_index=True)

use_log.head()

# %%
# 退会前月の退会顧客データを作成する
# 前提： 退会前月に退会を申し込み、翌月に退会する規則がある

# 1.退会済みの顧客のみのデータを作成する
exit_customer = customer[customer["is_deleted"] == 1].copy()

# 2.退会日（end_date）の1ヶ月前の年月データ（exit_month）列を作成する
# 2-1.退会日（end_date）の1ヶ月前の日付データ（exit_date）列を作成する
exit_customer["exit_date"] = None
exit_customer["end_date"] = pd.to_datetime(exit_customer["end_date"])
exit_customer.reset_index(drop=True, inplace=True)

for i in range(len(exit_customer)):
    exit_customer.loc[i, "exit_date"] = exit_customer.loc[
        i, "end_date"
    ] - relativedelta(months=1)

# 2-2.exit_dateをdatetime型に変換する
exit_customer["exit_date"] = pd.to_datetime(exit_customer["exit_date"])

# 2-3.exit_dateの日付を年月に変換したデータ列（exit_month）を作成する
exit_customer["exit_month"] = exit_customer["exit_date"].dt.strftime("%Y-%m")

# 3.顧客行動データ（use_log）と作成した退会済みの顧客の行動データ（exit_customer）を結合する
exit_use_log = pd.merge(
    use_log,
    exit_customer,
    how="left",
    left_on=["customer_id", "usemonth"],
    right_on=["customer_id", "exit_month"],
)

exit_use_log.drop("exit_month", axis=1, inplace=True)
print(len(use_log))

exit_use_log.head()
# %%
# 3.退会済みかつ退会前月の顧客の行動データのみを残す
# 3-1.nameデータに欠損値がある行を削除する
#   exit_customerの元になっているcustomerデータはend_date以外に欠損はないので、
#   end_date以外のデータ（ここではnameを指定した）が欠損している行は退会済みの顧客の退会前月以外のデータである
exit_use_log = exit_use_log.dropna(subset=["name"])

# 3-2.結合結果の確認
#  退会済みの1顧客につき退会前月データは1つのみなので、作成したデータでcustomer_idの重複がないことを確かめる
print(len(exit_use_log))
print(len(exit_use_log["customer_id"].unique()))
exit_use_log.head()

# %%
