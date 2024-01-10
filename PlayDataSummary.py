import pandas as pd

# ファイルの読み込み
file_path = './SimulationOutPut/playData.csv'
data = pd.read_csv(file_path)

# 各ランキングごとの集計を行う
summary = data.groupby('更新順位')['ユーザ獲得金額'].agg(['count', 'max', 'min', 'mean', 'median'])
summary.reset_index(inplace=True)
summary.columns = ['ランキング', '更新回数', '最大獲得金額', '最小獲得金額', '平均獲得金額', '獲得金額中央値']

# 集計結果をCSVファイルとして出力
output_file_path = './SimulationOutPut/playDataSummary.csv'
summary.to_csv(output_file_path, index=False)
