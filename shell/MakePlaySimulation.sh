# 固定ランキング
#python3 ./GamePlaySimulation_fixed.py
# 固定ランキング
#python3 ./GamePlaySimulation_fixed_long_pool.py
# 変動ランキング 1位更新時ランキング解放
# python3 ./GamePlaySimulation_flexibleRanking.py
# 変動ランキング ユニークユーザ増加時ランキング解放
python3 ./GamePlaySimulation_flexibleRanking_uu.py

python3 ./PlayDataSummary.py

# 固定ランキング
#open -a Numbers ./SimulationOutPut/playDataSummary_fixed.csv
# 固定ランキング long pool
#open -a Numbers ./SimulationOutPut/playDataSummary_fixed_longpool.csv
# 変動ランキング 1位更新時ランキング解放
#open -a Numbers ./SimulationOutPut/playDataSummary_flexibleRanking_top_score.csv
# 変動ランキング ユニークユーザ増加時ランキング解放
open -a Numbers ./SimulationOutPut/playDataSummary_flexibleRanking_uu.csv
