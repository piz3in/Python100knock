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
kokyaku_data.head()

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
