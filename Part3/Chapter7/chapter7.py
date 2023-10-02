# %%
import numpy as np
import os
import pandas as pd
from itertools import product
from pulp import LpProblem, LpVariable, lpSum, value, const
import networkx as nx

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# %%
# 1.データ読み込み
# 1-1.各倉庫から工場への輸送コストデータ
trans_cost = pd.read_csv("input/trans_cost.csv", index_col="工場")
trans_cost.head()

# %%
# 1-2.各工場の必要最低生産数データ
min_factory_demand = pd.read_csv("input/demand.csv")
min_factory_demand

# %%
# 1-3.各倉庫の最大供給可能部品数データ
max_warehouse_supply = pd.read_csv("input/supply.csv")
max_warehouse_supply

# %%
# 2.初期設定
np.random.seed(1)
factories = min_factory_demand.columns
warehouses = max_warehouse_supply.columns
# 各倉庫と各工場のデカルト積（itertools.product型）のリストを作成
pr = list(product(range(len(warehouses)), range(len(factories))))
pr
# %%

# 3.数理モデル作成
# LP problemクラスのオブジェクトを作成(最小化問題として定義する)
prob = LpProblem(sense=const.LpMinimize)

# 変数(各ルートの輸送量)をprをキーとしたディクショナリ型で定義
# 最小値は0,整数型に制約する
v1 = {(i, j): LpVariable(f"v{i}_{j}", lowBound=0, cat=const.LpInteger) for i, j in pr}

# 目的関数の定義(各ルートの輸送コストと各ルートの輸送量の積の総和)
prob += lpSum(trans_cost.iloc[i, j] * v1[i, j] for i, j in pr)

# 「制約条件1：各倉庫の部品供給数が最大部品供給数を超えない」を追加
for i in range(len(warehouses)):
    prob += (
        lpSum(v1[i, j] for j in range(len(factories)))
        <= max_warehouse_supply.iloc[0, i]
    )

# 「制約条件2:各工場が最低生産数以上を生産」を追加
for j in range(len(factories)):
    prob += (
        lpSum(v1[i, j] for i in range(len(warehouses))) >= min_factory_demand.iloc[0, j]
    )

# 最小化問題を解く
prob.solve()

# %%
# 4.総輸送コスト計算
# 各ルートの輸送量の最適解を代入するデータフレームを作成
data = np.zeros((len(warehouses), len(factories)), dtype=int)
trans_route_solved = pd.DataFrame(data, columns=factories, index=warehouses)

# 総輸送量コストの変数を定義（初期値0）
total_cost = 0

# 変数v1（最適解に更新されている）は辞書型。キーをk, 値をxに代入する
for k, x in v1.items():
    i, j = k[0], k[1]
    # 先に作成したデータフレームの各要素に対応するルートの輸送量の最適解を代入
    trans_route_solved.iloc[i, j] = value(x)
    # 総輸送量コストにそのルートの輸送コストを加算
    total_cost += trans_cost.iloc[i, j] * value(x)

print(trans_route_solved)
print(f"最適化ルートの総輸送コスト:{total_cost}")
# %%
# ノード座標の読み込み
trans_route_pos = pd.read_csv("input/trans_route_pos.csv")
trans_route_pos.head()
# %%
# グラフオブジェクトの作成
G = nx.Graph()

# ノードの設定
for i in range(len(trans_route_pos.columns)):
    G.add_node(trans_route_pos.columns[i])

# エッジの設定とエッジの重みのリスト化
edge_weights = []
size = 0.1

for i in range(len(trans_route_solved.index)):
    warehouse = trans_route_solved.index[i]

    for j in range(len(trans_route_solved.columns)):
        factory = trans_route_solved.columns[j]
        # エッジの追加
        G.add_edge(factory, warehouse)

        # エッジの重みのリスト化
        weight = trans_route_solved.loc[warehouse, factory] * size
        edge_weights.append(weight)

# ノードの座標の設定
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
# 制約条件を満たしているかを確認する
# 1.制約条件を確認する関数の作成
# 1-1.各工場の最小生産数を達成できるかを確認する関数の作成
def min_factory_demand_condition(trans_route, min_factory_demand):
    flag = np.zeros(len(min_factory_demand.columns))

    for i in range(len(min_factory_demand.columns)):
        factory = min_factory_demand.columns[i]
        min_demand = min_factory_demand.loc[0, factory]
        temp_sum = sum(trans_route.loc[:, factory])

        # 工場の最小生産数を達成できていればフラグを立てる
        if temp_sum >= min_demand:
            flag[i] = 1
    return flag


# 1-2.各倉庫の供給可能部品数以下に抑えられているかを確認する関数の作成
def max_warehouse_supply_condition(trans_route, max_warehouse_supply):
    flag = np.zeros(len(max_warehouse_supply.columns))

    for i in range(len(max_warehouse_supply.columns)):
        warehouse = max_warehouse_supply.columns[i]
        max_supply = max_warehouse_supply.loc[0, warehouse]
        temp_sum = sum(trans_route.loc[warehouse, :])

        # 倉庫の供給可能部品数以下に抑えられていればフラグを立てる
        if temp_sum <= max_supply:
            flag[i] = 1
    return flag


# %%
# 2.制約条件を満たしているかを確認する
print(
    f"各工場の最小生産数の達成確認結果(達成:1, 未達成:0): {min_factory_demand_condition(trans_route_solved,min_factory_demand)}"
)
print(
    f"各倉庫の供給可能部品数以下の達成確認結果(達成:1, 未達成:0): {max_warehouse_supply_condition(trans_route_solved,max_warehouse_supply)}"
)
