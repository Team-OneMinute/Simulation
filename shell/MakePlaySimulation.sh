# 固定ランキング
#python3 ./GamePlaySimulation_fixed.py
# 変動ランキング 1位更新時ランキング解放
python3 ./GamePlaySimulation_flexibleRanking.py
# 変動ランキング ユニークユーザ増加時ランキング解放
#python3 ./GamePlaySimulation_flexibleRanking.py

python3 ./PlayDataSummary.py
slee 5
SimulationOutPut/playData_fixed.csv

# 固定ランキング
#open -a Numbers /Users/iwasakitakashidai/IdeaProjects/yearn/Simulation/SimulationOutPut/playDataSummary_fixed.csv
# 変動ランキング 1位更新時ランキング解放
open -a Numbers /Users/iwasakitakashidai/IdeaProjects/yearn/Simulation/SimulationOutPut/playDataSummary_flexibleRanking_top_score.csv
# 変動ランキング ユニークユーザ増加時ランキング解放
#open -a Numbers /Users/iwasakitakashidai/IdeaProjects/yearn/Simulation/SimulationOutPut/playDataSummary_flexibleRanking_uu.csv


