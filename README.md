# Simulation
GameSystems's simulation tool 

## Simulation tool
- 固定ランキング
```
GamePlaySimulation_fixed.py
```
- 変動ランキング 1位更新時にランキング開放
```
GamePlaySimulation_flexibleRanking_top_score.py
```
- 変動ランキング ユニークユーザ増加でランキング開放
```
GamePlaySimulation_flexibleRanking_uu.py
```

## How to
- シミュレーションしたいツールごとにコメントを入れ替える
  - 編集対象ファイル
  ```
  MakePlaySimulation.sh
  PlayDataSummary.py
  ```
- sh
  - MakePlaySimulation.sh
```shell
cd /Users/iwasakitakashidai/IdeaProjects/yearn/Simulation
sh ./MakePlaySimulation.sh
```