# %%
import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# %%
# データの読み込み
# %%
# 1.工場データ
factories = pd.read_csv("input/tbl_factory.csv", index_col=0)
factories.head()

# %%
# 2.倉庫データ
warehouses = pd.read_csv("input/tbl_warehouse.csv", index_col=0)
warehouses.head()

# %%
# 3.コストデータ
cost = pd.read_csv("input/rel_cost.csv", index_col=0)
cost.head()

# %%
# 4.輸送実績
transactions = pd.read_csv("input/tbl_transaction.csv", index_col=0)
transactions.head()

# %%
# 輸送実績に各データを結合する
# %%
# 1.コストデータを付与する
join_data = pd.merge(
    transactions,
    cost,
    how="left",
    left_on=["ToFC", "FromWH"],
    right_on=["FCID", "WHID"],
)
join_data.head()

# %%
# 2.工場データを付与する
join_data = pd.merge(join_data, factories, how="left", on="FCID")
join_data.head()

# %%
# 3.倉庫データを付与する
join_data = pd.merge(join_data, warehouses, how="left", on="WHID")
join_data.head()

# %%
# 重複カラムを削除する
join_data.drop(columns=["FCID", "WHID"], inplace=True)
join_data.columns

# %%
# 直感的にわかりやすい順にカラムを並び替える
join_data[
    [
        "TransactionDate",
        "Quantity",
        "Cost",
        "ToFC",
        "FCName",
        "FCDemand",
        "FCRegion",
        "FromWH",
        "WHName",
        "WHSupply",
        "WHRegion",
    ]
]
join_data.head()

# %%
# 関東支社と東北支社のデータのみのデータフレームを作成する
# %%
# 1.関東支社データ
kanto = join_data[join_data["WHRegion"] == "関東"].copy()
kanto.head()
# %%
# 2.東北支社データ
tohoku = join_data[join_data["WHRegion"] == "東北"].copy()
tohoku.head()

# %%
