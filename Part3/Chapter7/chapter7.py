# %%
import numpy as np
import os
import pandas as pd
from itertools import product
from pulp import LpProblem, LpVariable, lpSum, value, const

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
