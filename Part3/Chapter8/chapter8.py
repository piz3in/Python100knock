# %%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# %%
# 人間関係のネットワークを可視化する
# データ読み込み
df_links = pd.read_csv("input/links.csv")
df_links
# %%
# グラフオブジェクトの作成
G = nx.Graph()

# ノード（頂点）の設定
n_repeaters = len(df_links)

G.add_nodes_from([str(n) for n in range(n_repeaters)])

# エッジ（辺）の設定
G.add_edges_from(
    [
        (str(i), str(j))
        for i in range(n_repeaters)
        for j in range(n_repeaters)
        if df_links.iloc[:, 1:].iloc[i, j] == 1
    ]
)

# 描画
nx.draw_networkx(G, node_color="k", edge_color="k", font_color="w")


# %%
# 口コミによる情報伝播の様子を可視化する
def determine_link(percent: float) -> float:
    """
    口コミを伝播させるかどうかを決定する

    Args:
        percent (float): 口コミが起こる確率
    """
    random_value = np.random.rand()
    if random_value <= percent:
        return 1
    else:
        return 0


def simulate_percolation(
    n_repeaters: int, list_active: list, percent_percolation: float
) -> list:
    """
    口コミの伝播をシミュレートする

    Args:
        n_repeaters (int): リピーターの人数
        list_active (list): 各リピーター（ノード）に口コミが伝わったかどうかを0,1で表現するリスト
        percent_percolation (float): 口コミが起こる確率

    Returns:
        list_active(list): 更新した各リピーター（ノード）に口コミが伝わったかどうかを0,1で表現するリスト
    """
    for i in range(n_repeaters):
        if list_active[i] == 1:  # 引数で受け取ったlist_activeで対象ユーザーがactiveのとき
            for j in range(n_repeaters):
                if (
                    df_links.iloc[:, 1:].iloc[i, j] == 1
                ):  # 対象ユーザーと繋がっているユーザー（対応ユーザーと呼ぶ）毎に口コミを伝播させるかどうかを決定する関数を実行する
                    if determine_link(percent_percolation) == 1:  # 伝播する場合
                        list_active[j] = 1  # 更新するlist_activeの対応ユーザーをactiveにする
    return list_active


percent_percolation = 0.1
n_t = 100

# アクティブユーザーリストを初期化（ユーザー0のみactiveにする）
list_active = np.zeros(n_repeaters)
list_active[0] = 1

# アクティブユーザーリストの履歴リスト（シミュレートの試行毎にアクティブユーザーリストを残す）
list_timeseries = []
list_timeseries.append(list_active.copy())

for t in range(1, n_t + 1):
    list_active = simulate_percolation(n_repeaters, list_active, percent_percolation)
    list_timeseries.append(list_active.copy())


# %%
# 伝播した口コミの様子を可視化する
def active_node_coloring(list_active: list) -> list:
    """口コミが伝わったユーザーのノード色を赤にする関数

    Args:
        list_active (list): アクティブユーザーのリスト（アクティブなら1、そうでないなら0）

    Returns:
        list: アクティブユーザーのノード色のリスト（アクティブなら"r"、そうでないなら"k"）
    """
    list_color = []
    for i in range(n_repeaters):
        if (
            list_timeseries[t][i] == 1
        ):  # 試行回数tのときのアクティブユーザーリストのi番目のユーザーがactiveならノード色のリストに赤を追加する
            list_color.append("r")
        else:
            list_color.append("k")  # 非アクティブなら黒を追加する
    return list_color


# %%
# 初期のアクティブユーザー可視化
t = 0
nx.draw_networkx(G, font_color="w", node_color=active_node_coloring(list_timeseries[t]))
# %%
# 試行回数10のときのアクティブユーザー可視化
t = 10
nx.draw_networkx(G, font_color="w", node_color=active_node_coloring(list_timeseries[t]))
# %%
# 試行回数100のときのアクティブユーザー可視化
t = 100
nx.draw_networkx(G, font_color="w", node_color=active_node_coloring(list_timeseries[t]))
# %%
# 口コミの時系列変化のグラフを作成する
list_timeseries_active_num = [sum(lst) for lst in list_timeseries]

plt.plot(list_timeseries_active_num)
# %%
