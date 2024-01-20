import pandas as pd

# ファイルの読み込み
file_path = './SimulationOutPut/playData.csv'
data = pd.read_csv(file_path)

# 獲得金額閾値
bet_amount = 10

# ユーザ獲得金額が1以下の件数を集計するカラムを追加
summary = data.groupby('更新順位').agg({
    'ユーザ獲得金額': ['count', 'max', 'min', lambda x: sum(x < bet_amount), 'mean', 'median']
}).reset_index()

# 列名を再設定
summary.columns = ['ランキング', '更新回数', '最大獲得金額', '最小獲得金額', '閾値未満件数', '平均獲得金額', '獲得金額中央値']

# 集計結果をCSVファイルとして出力
output_file_path = './SimulationOutPut/playDataSummary.csv'
summary.to_csv(output_file_path, index=False)


