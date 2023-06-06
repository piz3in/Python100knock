# %%
import os
import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# データの読みこみ
uriage_data = pd.read_csv("input/uriage.csv")
uriage_data.head()

# %%
kokyaku_data = pd.read_excel("input/kokyaku_daicho.xlsx")
print(kokyaku_data.head())
print(len(kokyaku_data))

# %%
# データの揺れがあるまま商品毎の月売上合計を集計する
# 1.purchase_dateの型確認
uriage_data.dtypes

# %%
# 2.purchase_dateをdatetime型に変換
uriage_data["purchase_date"] = pd.to_datetime(uriage_data["purchase_date"])

# 3.年月のみ抽出したデータ列(purchase_month)を作成する
uriage_data["purchase_month"] = uriage_data["purchase_date"].dt.strftime("%Y-%m")
uriage_data[["purchase_date", "purchase_month"]].head()

# %%
# 4.商品毎の月別販売数を集計する
pd.pivot_table(
    uriage_data,
    index="purchase_month",
    columns="item_name",
    aggfunc="size",
    fill_value=0,
)
# %%
# 5.商品毎の月別売上を集計する
pd.pivot_table(
    uriage_data,
    index="purchase_month",
    columns="item_name",
    values="item_price",
    aggfunc="sum",
    fill_value=0,
)

# %%
# 商品名の表記揺れを補正する
# 1.商品名のユニーク数を確認する(実際は26種類)
len(pd.unique(uriage_data["item_name"]))

# %%
# 2.データの揺れを解消する
# 2-1.半角を全角に統一する
uriage_data["item_name"] = uriage_data["item_name"].str.upper()

# 2-2.スペース（全角、半角両方）を消す
uriage_data["item_name"] = uriage_data["item_name"].str.replace("　", "")
uriage_data["item_name"] = uriage_data["item_name"].str.replace(" ", "")

# 2-3.商品名順にソートする
uriage_data.sort_values("item_name", ascending=True)

# %%
# 3.補正結果の検証をする
# 3-1.ユニークな商品名の確認
np.sort(pd.unique(uriage_data["item_name"]))

# %%
# 3-2.ユニークな商品名の数の確認
len(pd.unique(uriage_data["item_name"]))

# %%
# 金額の欠損値を補完する
# 1.どのデータに欠損値があるかを確認する
uriage_data.isnull().any()

# %%
# 2.欠損値を補完する
# 2-1.item_priceが欠損している時に1となるフラグを立てる
item_price_is_null = uriage_data["item_price"].isnull()
item_price_is_null

# %%
# 2-2.item_priceに欠損がある商品名のリストを作成する
price_is_null_item_name_list = list(
    np.sort(uriage_data.loc[item_price_is_null, "item_name"].unique())
)
price_is_null_item_name_list

# %%
# 2-3.item_priceに欠損があるの商品の価格を欠損していない行から取得し欠損値を補完する
for item_name in price_is_null_item_name_list:
    # 対象となるitem_nameのitem_priceを欠損していない行から取得する
    item_price = uriage_data.loc[
        (~item_price_is_null) & (uriage_data["item_name"] == item_name), "item_price"
    ].max()
    # 対象となるitem_nameのitem_price列の全ての欠損値を取得したitem_priceで補完する
    uriage_data.loc[
        (item_price_is_null) & (uriage_data["item_name"] == item_name), "item_price"
    ] = item_price
uriage_data.head()

# %%
# 3.補完の検証を行う
# 3-1.欠損値の有無を確認する
uriage_data.isnull().any()

# %%
# 3-2.補完した金額の値が正しいかを確認する
for item_name in price_is_null_item_name_list:
    item_price_max = uriage_data.loc[
        uriage_data["item_name"] == item_name, "item_price"
    ].max()

    item_price_min = uriage_data.loc[
        uriage_data["item_name"] == item_name, "item_price"
    ].min()

    print(f"{item_name}の最大額:{item_price_max}、最小額:{item_price_min}")

# %%
# 顧客データの揺れを補正する
kokyaku_data.head()

# %%
# 1.顧客名の揺れを補正する
# 1-1.顧客名の顧客データと売上データ間の表記揺れの確認
print(kokyaku_data["顧客名"].head())
print(uriage_data["customer_name"].head())

# %%
# 1-2.空白を削除する
kokyaku_data["顧客名"] = kokyaku_data["顧客名"].str.replace("　", "")
kokyaku_data["顧客名"] = kokyaku_data["顧客名"].str.replace(" ", "")
kokyaku_data["顧客名"].head()

# %%
# 2.日付の揺れを補正する
kokyaku_data["登録日"].head()

# %%
# 2-1.数値として取り込まれている行を特定する
register_date_is_digit = kokyaku_data["登録日"].astype("str").str.isdigit()
# 該当する行数を確認する
register_date_is_digit.sum()

# %%
# 2-2.数値として取り込まれている行をdatetime型に変換する
correct_register_date_from_serial = pd.to_datetime("1900-01-01") + pd.to_timedelta(
    kokyaku_data.loc[register_date_is_digit, "登録日"].astype("float"), unit="D"
)
correct_register_date_from_serial

# %%
# 2-3.文字列として取り込まれている行をdatetime型に変換する
correct_register_date_from_string = pd.to_datetime(
    kokyaku_data.loc[~register_date_is_digit, "登録日"]
)
correct_register_date_from_string

# %%
# 2-4.数値列から変換した行と文字列から変換した行を結合して顧客データの登録日データを更新する
kokyaku_data["登録日"] = pd.concat(
    [correct_register_date_from_serial, correct_register_date_from_string]
)
kokyaku_data["登録日"].head()

# %%
# 3.月毎の顧客登録数をカウントする
# 3-1.登録日データから登録月データを作成する
kokyaku_data["登録月"] = kokyaku_data["登録日"].dt.strftime("%Y-%m")

# 3-2.月毎の登録顧客数をカウントする
print(kokyaku_data[["登録月", "顧客名"]].groupby("登録月").count())

# 3-3.顧客データ数に変化がないかを検証する
print(len(kokyaku_data))

# 3-4.登録日データに数値列が残っていないかを確認する
register_date_is_digit = kokyaku_data["登録日"].astype("str").str.isdigit()
register_date_is_digit.sum()

# %%
# 売上履歴に顧客データを結合する
join_data = pd.merge(
    uriage_data, kokyaku_data, how="left", left_on="customer_name", right_on="顧客名"
)
# 重複するデータ列(customer_nameと顧客名)の一方（customer_name）を削除する
join_data = join_data.drop("customer_name", axis=1)
join_data.head()

# %%
