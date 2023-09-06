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
# 翌月の利用回数の予測を行う
# 2018年5-10月の6ヶ月間のデータを用いて2018年11月の利用回数を予測する
# 1.顧客毎に月毎の利用回数を集計する
# 1-1.usedateデータをdatetime型に変換する
use_log["usedate"] = pd.to_datetime(use_log["usedate"])
# 1-2.monthデータ列を追加する
use_log["usemonth"] = use_log["usedate"].dt.strftime("%Y-%m")
use_log.head()
# %%
# 1-3.顧客毎の月毎の利用データを作成する
monthly_use_log = use_log.groupby(["customer_id", "usemonth"], as_index=False).count()
monthly_use_log.drop("usedate", axis=1, inplace=True)
monthly_use_log.rename(columns={"log_id": "count"}, inplace=True)
monthly_use_log.head()

# %%
# 2.顧客毎に予測月の利用回数とその過去6ヶ月の利用回数のデータセットを作成する
# データ取得期間が2018年4月から2019年3月なので、予測月は過去6ヶ月のデータが取れる2018年10月から2019年3月までとなる
year_months = list(monthly_use_log["usemonth"].unique())

predict_data = pd.DataFrame()

for i in range(6, len(year_months)):  # 予測月は過去6ヶ月のデータが取れる2018年10月から
    # 予測月の利用回数データのデータフレーム（tmp）を作成する
    tmp = monthly_use_log[monthly_use_log["usemonth"] == year_months[i]].copy()
    tmp.rename(columns={"count": "count_pred", "usemonth": "pred_month"}, inplace=True)

    for j in range(1, 7):
        # 予測月の過去6ヶ月の利用回数データを各列に持つデータフレーム（tmp_before）を作成する
        tmp_before = monthly_use_log[
            monthly_use_log["usemonth"] == year_months[i - j]
        ].copy()

        # 当月（予測月の前の月）を0として、何ヶ月前の利用回数かを表すカラム名をつける
        tmp_before.rename(columns={"count": f"count_{j-1}"}, inplace=True)

        # カラム名でいつの月の利用回数か判別できるようになったので、不要になったusemonthデータ列を削除する
        tmp_before.drop("usemonth", axis=1, inplace=True)

        # 予測月の利用回数データに過去の利用回数データを結合する
        tmp = pd.merge(tmp, tmp_before, how="left", on="customer_id")

    # 各予測月について作成した予測月と過去の利用回数データのデータフレームを結合する
    predict_data = pd.concat([predict_data, tmp], ignore_index=True)

predict_data.head()

# %%
# 3.過去6ヶ月間のデータに欠損があるデータを削除する
predict_data = predict_data.dropna(ignore_index=True)
predict_data.head()

# %%
