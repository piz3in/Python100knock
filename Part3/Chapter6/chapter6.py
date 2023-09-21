# %%
import os
import pandas as pd
import networkx as nx
import numpy as np

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
# 1.関東支社（倉庫が関東にある）データ
kanto = join_data[join_data["WHRegion"] == "関東"].copy()
kanto.head()
# %%
# 2.東北支社(倉庫が東北にある)データ
tohoku = join_data[join_data["WHRegion"] == "東北"].copy()
tohoku.head()

# %%
# 現状の輸送量・コストの確認
# 1.総コスト実績
print(f'関東支社の総コスト:{kanto["Cost"].sum()}万円')
print(f'東北支社の総コスト:{tohoku["Cost"].sum()}万円')
# %%
# 2.総部品輸送個数実績
print(f'関東支社の総部品輸送個数:{kanto["Quantity"].sum()}個')
print(f'東北支社の総部品輸送個数:{tohoku["Quantity"].sum()}個')

# %%
# 3.輸送部品１つあたりの輸送コスト実績
print(f'関東支社の部品１つあたりの輸送コスト:{int(kanto["Cost"].sum()/kanto["Quantity"].sum()*10000)}円')
print(f'東北支社の部品１つあたりの輸送コスト:{int(tohoku["Cost"].sum()/tohoku["Quantity"].sum()*10000)}円')

# %%
# 4.各支社の倉庫→工場間の平均輸送コスト
cost_check = pd.merge(cost, factories, how="left", on="FCID")
print(f'関東支社の平均輸送コスト:{cost_check.loc[cost_check["FCRegion"]=="関東","Cost"].mean()}万円')
print(f'東北支社の平均輸送コスト:{cost_check.loc[cost_check["FCRegion"]=="東北","Cost"].mean()}万円')

# %%
# 各倉庫から工場への輸送ルートデータ読み込み
trans_route = pd.read_csv("input/trans_route.csv", index_col="工場")
trans_route.head()
# %%
# 各輸送ルートの輸送量データを可視化する
# ノード座標の読み込み
trans_route_pos = pd.read_csv("input/trans_route_pos.csv")
trans_route_pos.head()

# %%
# グラフオブジェクトの作成
G = nx.Graph()

# ノード（頂点）の設定
for i in range(len(trans_route_pos.columns)):
    G.add_node(trans_route_pos.columns[i])

# エッジ（辺）の設定とエッジの重みのリスト化
edge_weights = []
size = 0.1

for i in range(len(trans_route.index)):
    warehouse = trans_route.index[i]

    for j in range(len(trans_route.columns)):
        # エッジの設定
        factory = trans_route.columns[j]
        G.add_edge(factory, warehouse)

        # エッジの重みのリスト化
        weight = trans_route.loc[warehouse, factory] * size
        edge_weights.append(weight)

# 座標の設定
pos = {}
for i in range(len(trans_route_pos.columns)):
    node = trans_route_pos.columns[i]
    pos[node] = (trans_route_pos.loc[0, node], trans_route_pos.loc[1, node])

# 描画
nx.draw(
    G,
    pos,
    with_labels=True,
    font_size=16,
    node_size=1000,
    node_color="k",
    font_color="w",
    width=edge_weights,
)
# %%
# 輸送コストを計算する関数を作成する
# 各倉庫から工場への輸送コストデータ読み込み
trans_cost = pd.read_csv("input/trans_cost.csv", index_col="工場")
trans_cost.head()


# %%
# 輸送コストを計算する関数
def calc_trans_cost(trans_route, trance_cost):
    cost = 0
    for i in range(len(trans_route.index)):
        for j in range(len(trans_route.columns)):
            warehouse = trans_route.index[i]
            factory = trans_route.columns[j]
            cost += (
                trance_cost.loc[warehouse, factory]
                * trans_route.loc[warehouse, factory]
            )
    return cost


print(f"総輸送コスト:{calc_trans_cost(trans_route, trans_cost)}")

# %%
# 制約条件を作る
# 1.データの読み込み
# 1-1.各工場の最小生産数
factory_min_demand = pd.read_csv("input/demand.csv")
factory_min_demand

# %%
# 1-2.各倉庫が供給可能な最大部品数
warehouse_max_supply = pd.read_csv("input/supply.csv")
warehouse_max_supply

# %%
# 2.工場側の制約条件(最小生産数を達成する)の作成
for i in range(len(factory_min_demand.columns)):
    factory = factory_min_demand.columns[i]
    min_demand = factory_min_demand.loc[0, factory]
    temp_sum = sum(trans_route.loc[:, factory])
    print(f"{factory}への輸送量:{temp_sum}, 最低生産数:{min_demand}")

    if temp_sum >= min_demand:
        print("最低生産数を満たしています。")
    else:
        print("最低生産数を満たしていません。輸送ルートの再計算が必要です。")


# %%
# 3.倉庫側の制約条件（供給可能部品数以下に抑える）の作成
for i in range(len(warehouse_max_supply.columns)):
    warehouse = warehouse_max_supply.columns[i]
    max_supply = warehouse_max_supply.loc[0, warehouse]
    temp_sum = sum(trans_route.loc[warehouse, :])
    print(f"{warehouse}の供給量:{temp_sum}, 上限供給可能部品数:{max_supply}")

    if temp_sum <= max_supply:
        print("上限供給可能部品数以下です。")
    else:
        print("上限供給可能部品数を超えています。輸送ルートの再計算が必要です。")
# %%
# 輸送ルートを変更して総輸送コストの変化を確認する
# 変更後ルートデータの読み込み
new_trans_route = pd.read_csv("input/trans_route_new.csv", index_col="工場")
new_trans_route

# %%
# 変更後ルートの総輸送コスト計算
print(f"総輸送コスト（変更後）:{calc_trans_cost(new_trans_route, trans_cost)}")


# %%
# 制約条件を満たしているかの確認
# 1.制約条件を確認する関数の作成
# 1-1.各工場の最小生産数を達成できるかを確認する関数の作成
def factory_min_demand_condition(trans_route, factory_min_demand):
    flag = np.zeros(len(factory_min_demand.columns))

    for i in range(len(factory_min_demand.columns)):
        factory = factory_min_demand.columns[i]
        min_demand = factory_min_demand.loc[0, factory]
        temp_sum = sum(trans_route.loc[:, factory])

        # 工場の最小生産数を達成できていればフラグを立てる
        if temp_sum >= min_demand:
            flag[i] = 1
    return flag


# 1-2.各倉庫の供給可能部品数以下に抑えられているかを確認する関数の作成
def warehouse_max_supply_condition(trans_route, warehouse_max_supply):
    flag = np.zeros(len(warehouse_max_supply.columns))

    for i in range(len(warehouse_max_supply.columns)):
        warehouse = warehouse_max_supply.columns[i]
        max_supply = warehouse_max_supply.loc[0, warehouse]
        temp_sum = sum(trans_route.loc[warehouse, :])

        # 倉庫の供給可能部品数以下に抑えられていればフラグを立てる
        if temp_sum <= max_supply:
            flag[i] = 1
    return flag


# %%
# 2.制約条件を満たしているかを確認する
print(
    f"各工場の最小生産数の達成確認結果(達成:1, 未達成:0): {factory_min_demand_condition(new_trans_route,factory_min_demand)}"
)
print(
    f"各倉庫の供給可能部品数以下の達成確認結果(達成:1, 未達成:0): {warehouse_max_supply_condition(new_trans_route,warehouse_max_supply)}"
)

# %%
