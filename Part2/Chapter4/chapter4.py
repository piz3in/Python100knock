# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# データの読み込み
# 1.利用履歴データの読み込み
use_log = pd.read_csv("input/use_log.csv")
use_log.isnull().sum()

# %%
# 2.顧客行動データの読み込み
customer = pd.read_csv("input/join_customer_data.csv")
customer.isnull().sum()

# %%
# クラスタリングで顧客をグループ化する
# 1.クラスタリングに用いるデータのみのデータフレームを作成する
customer_clustering = customer.loc[
    :, ["mean", "median", "max", "min", "membership_period"]
]
customer_clustering.head()

# %%
# 2.K-means法で4つのグループにクラスタリングする
# StandardScalarクラスのインスタンス作成
sc = StandardScaler()

# 2-1.標準化する
# 訓練データに対してfitメソッドを適用して、スケール変換器を作成する
# スケール変換器のtransformメソッドを用いて訓練データをスケール変換する
# ここでは、fit_transformメソッドでこれらを一気に実行する
customer_clustering_sc = sc.fit_transform(customer_clustering)

# 2-2.クラスタリングする
# KMeansクラスのインスタンスを作成する。同時に、パラメータを指定する
kmeans = KMeans(n_clusters=4, random_state=0)

# kmeansオブジェクトのfitメソッドを呼び出して訓練データからモデルを構築する
clusters = kmeans.fit(customer_clustering_sc)

# クラスタリング結果のデータ列を作成する
customer_clustering["cluster"] = clusters.labels_
# 各クラスにデータが割り振られていることを確認する
customer_clustering["cluster"].unique()

# %%
customer_clustering.head()

# %%
# クラスタリング結果を分析する
# 1.理解しやすいcolumn名に変更する
customer_clustering.columns = ["月内平均値", "月内中央値", "月内最大値", "月内最小値", "会員期間", "cluster"]
customer_clustering.head()

# %%
# 2.各クラスターに含まれる顧客の数をカウントする
customer_clustering.groupby("cluster").count()

# %%
# 3.グループ毎の平均値を集計する
customer_clustering.groupby("cluster").mean()

# クラスタリング結果を可視化する
# %%
X = customer_clustering_sc
# PCAオブジェクトを生成（ここでは次元削減を行うので、維持する主成分の数をパラメータとして指定）
pca = PCA(n_components=2)

# fitメソッドを呼び出し、主成分を見つける
# transformメソッドで回転と次元削減を行う
x_pca = pca.fit_transform(X)

pca_df = pd.DataFrame(x_pca)
pca_df["cluster"] = customer_clustering["cluster"]

for i in customer_clustering["cluster"].unique():
    tmp = pca_df.loc[pca_df["cluster"] == i]
    plt.scatter(tmp[0], tmp[1])

# %%
# 退会顧客の傾向を把握する
# 1.クラスタリング結果に顧客行動データから退会情報を追加する
customer_clustering = pd.concat(
    [
        customer_clustering,
        customer.loc[:, ["customer_id", "is_deleted", "routine_flg"]],
    ],
    axis=1,
)
customer_clustering.head()

# %%
# 2.クラスター毎の退会顧客数をカウントする
customer_clustering.groupby(["cluster", "is_deleted"]).count()["customer_id"]

# %%
# 3.クラスター毎の定期利用フラグをカウントする
customer_clustering.groupby(["cluster", "routine_flg"]).count()["customer_id"]

# %%
