# %%
import os
import pandas as pd
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
