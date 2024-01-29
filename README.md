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

ランキングを更新すると、報酬がもらえるゲームを考えています。
ユーザはゲームの参加時に１ドルのBetを行います。特定の分配率に応じて
各ランキングにBet金額が分配されていきいます。
このランキングへの分配率をあなたと考えていきたいです。
このランキングには、アクティブユーザ数に応じて増加する特徴があります。
4人参加すると１つ開放される特徴があります。例えば100人参加していると25人です。
このゲームの最も大事なコンセプトとして、成功体験をさせることです。
成功体験の定義は、そこそこの回数ランキングが更新できること、そこそこの獲得金額になることです。
つまり指数関数で分配率を計算してしまうと、ランキング開放数が大きい時下位のランキング更新時に
そこそこの獲得金額になりません。このことを考慮してどのような分配率を考えるべきか

段階的な分配率と参加者数に応じた調整を考えています。
最大ユーザは１０００人ほどと現在予想しています。
この時。参加人数100人、500人、800人、1000人のときの具体的な
報酬分配率のイメージをしてください

各ランキングにおいて
ランキング上位10%：50%の報酬
ランキングの次の40%（11位～50位）：30%の報酬
ランキングの残り50%（51位～100位）：20%の報酬
このような設定を行うときのPythonコードを実装してください。
関数名:getRankingDistribution()
引数：ranking_num（）現在のランキング解放数
戻り値:各ランキングの分配率のList
例：２５個ランキングが開放されているとき、戻り値は1~25位までの分配率がListになってreturnされる