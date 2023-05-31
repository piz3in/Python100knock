# %%
import os
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
