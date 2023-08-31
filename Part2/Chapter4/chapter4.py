# %%
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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
kmeans = KMeans(n_clusters=4, n_init=1, random_state=0)

# kmeansオブジェクトのfitメソッドを呼び出して訓練データからモデルを構築する
clusters = kmeans.fit(customer_clustering_sc)

# クラスタリング結果のデータ列を作成する
customer_clustering["cluster"] = clusters.labels_
# 各クラスにデータが割り振られていることを確認する
customer_clustering["cluster"].unique()

# %%
customer_clustering.head()

# %%
