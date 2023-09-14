# %%
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
from sklearn.tree import DecisionTreeClassifier
import sklearn.model_selection

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
# 継続顧客のデータを作成する
# 1.継続中の顧客のみの顧客行動データを作成
continue_customer = customer[customer["is_deleted"] == 0].copy()

# 2.全ての顧客（退会済みと継続中）の月別利用回数データと継続中の顧客行動データを結合
continue_use_log = pd.merge(use_log, continue_customer, on="customer_id", how="left")
print(len(continue_use_log))

# 3.退会済みの顧客行動データを削除
continue_use_log = continue_use_log.dropna(subset=["name"])
print(len(continue_use_log))

# %%
# 退会顧客と継続顧客のデータ数を揃えるため、継続顧客データをアンダーサンプリングする
# 1.データをシャッフルする
continue_use_log = continue_use_log.sample(frac=1, ignore_index=True)

# 2.customer_idが重複しているデータは最初のデータのみを残す
continue_use_log.drop_duplicates(subset="customer_id", inplace=True)

print(len(continue_use_log))
continue_use_log.head()

# %%
# 継続顧客データと退会顧客データを結合する
predict_data = pd.concat([continue_use_log, exit_use_log], ignore_index=True)
print(len(predict_data))
predict_data.head()

# %%
# 予測月の初日時点での会員期間を計算する
# 1.予測月の初日データ(now_date)列を作成する
predict_data["now_date"] = pd.to_datetime(predict_data["usemonth"], format="%Y-%m")

# 2.start_date列をdatetime型に変換する
predict_data["start_date"] = pd.to_datetime(predict_data["start_date"])

# 3.予測月までの会員期間（membership_period: now_dateとstart_dateの差分）を計算する)
predict_data["membership_period"] = 0

for i in range(len(predict_data)):
    delta = relativedelta(
        predict_data.loc[i, "now_date"], predict_data.loc[i, "start_date"]
    )
    predict_data.loc[i, "membership_period"] = int(delta.years * 12 + delta.months)

predict_data.head()

# %%
# 欠損値を除去する
# 1.欠損値の数を確認する
predict_data.isnull().sum()

# %%
# 2.count_1のデータが欠損している行を除外する
predict_data.dropna(subset=["count_1"], inplace=True)

# 3.除外できたことを確認する
predict_data.isnull().sum()

# %%
# 文字列型の変数を処理できるように整形する
# 1.予測に用いるデータ列のみ残す
target_columns = [
    "campaign_name",
    "class_name",
    "gender",
    "count_1",
    "routine_flg",
    "membership_period",
    "is_deleted",
]
predict_data = predict_data[target_columns]
predict_data.head()

# %%
# 2.カテゴリー変数をダミー変数化する
predict_data = pd.get_dummies(predict_data, dtype=int)
predict_data.head()
# %%
# 3.不要なダミー変数を削除する
predict_data.drop(
    columns=["campaign_name_通常", "class_name_ナイト", "gender_M"], inplace=True
)
predict_data.head()

# %%
# 決定木を用いて退会予測モデルを作成する
# 1.退会顧客と継続顧客が同数含まれるデータを作成する
exit_predict_data = predict_data[predict_data["is_deleted"] == 1].copy()
continue_predict_data = (
    predict_data[predict_data["is_deleted"] == 0]
    .copy()
    .sample(n=len(exit_predict_data))
)

X = pd.concat([exit_predict_data, continue_predict_data], ignore_index=True)
y = X["is_deleted"].copy()
X.drop(columns=["is_deleted"], inplace=True)

# 2.学習用データと評価用データに分割する
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y)

# 3.モデルを作成する
model = DecisionTreeClassifier(random_state=0)
# 3-1.訓練データからモデルを構築する
model.fit(X_train, y_train)
# 3-2.与えられた入力に対する予測結果を返す
y_test_pred = model.predict(X_test)
print(y_test_pred)

# %%
# 4.予測結果と正解結果の比較を行う
results_test = pd.DataFrame({"y_test": y_test, "y_pred": y_test_pred})
results_test.head()

# %%
# 予測モデルの評価
correct = len(results_test[results_test["y_test"] == results_test["y_pred"]])
data_count = len(results_test)
score_test = correct / data_count
print(score_test)

# %%
print(f"test score: {model.score(X_test, y_test)}")
print(f"train score: {model.score(X_train, y_train)}")

# %%
# モデルパラメータの調整
# max_depthを5にする
model = DecisionTreeClassifier(random_state=0, max_depth=5)
model.fit(X_train, y_train)

print(f"test score: {model.score(X_test, y_test)}")
print(f"train score: {model.score(X_train, y_train)}")

# %%
