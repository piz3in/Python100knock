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
