# %%
import os
import pandas as pd

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
