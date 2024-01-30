# プレイヤー数
total_player_count = 1000  # 総プレイヤー数
start_player_count = 100  # 開始時のアクティブプレイヤー数
join_player_count_per_sprint = 50  # アクティブプレイヤーを何人ずつ追加するか

# プレイヤーのモチベーションパラメータ
player_motivation_count = 20  # プレイヤーがランキングを更新できないと諦める回数
motivation_pot_amount = 100  # 途中参加する動機となるポット金額

# 金額
bet_amount = 1  # bet金額($)
management_fee_rate = 0.1 # bet金額に対する運営の取り分割合
min_default_amount = 2  # 最低獲得金額

# ランキングの設定
opening_ranking_per_active_player = 0.4  # アクティブプレイヤー数に対して開放するランキングの割合(0.25の場合、100人のアクティブプレイヤーがいたら25位まで開放)
