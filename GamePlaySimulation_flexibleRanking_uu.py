from pathlib import Path
# シミュレーションの設定
import pandas as pd

import config

from libs import calc_distribution
from libs import bet
from libs import output_factory
from libs import play_game
from libs import score_ranking

"""
ランキング変動型シミュレーション
ユニークユーザ数がふえる度にランキングが開放される。
また、ユニーク数が減る度にランキングが減っていく
"""

# グローバル変数
management_pool = 0 # 運営の獲得プール
ranking_pools = []  # ランキングプール　初期はLength 1　ランキングが更新される度にaddされる
ranking_distribution = []  # 総pot金額のうち、各potに積まれる金額の割合の分布
current_ranking = []  # スコアランキング
total_player_earnings = 0  # 全プレイヤーの総獲得金額

# 集計用データ
count_update_ranking = []
total_bet_amount = 0  # 全プレイヤーがbetした合計金額
update_ranking_user = []
player_result_win_lose = []
for i in range(config.total_player_count):
    # [bet金額, 合計獲得金額, ランキング更新回数]
    player_result_win_lose.append([0, 0, 0])
management_pay = 0  # 運営がpotに入れた合計金額

def update_pool(ranking_pools, updated_rank):
    """
    ランキングプールの更新
    更新ロジック：上位スライド式
    1位のランキング更新があった場合、1位のランキングプールが空になるので
    2位以下のプールが上位のプールに移動する。よって、最下位プールが空になる
    空になったプールは、Betのロジックで別に補填ロジックを持つ
    """
    global management_pay
    ranking_pools[updated_rank] = 0  # 更新されたランキングのプールをリセット
    if len(ranking_pools) != updated_rank + 1:
        for j in range(updated_rank, len(ranking_pools) - 1):
                ranking_pools[j] = ranking_pools[j + 1]
    ranking_pools[len(ranking_pools) - 1] = config.min_default_amount
    management_pay += config.min_default_amount
    return ranking_pools

def bet_check(player_id, play_counter, player_available):
    """
    参加チェック
    参加者のプレイ回数が残っているとき参加する
    """
    # プレイヤーが参加状態ではない
    if player_available[player_id] is False:
        return False
    elif play_counter[player_id] > 0:
        return True
    else:
        return False

def judge_player(ranking_pools, player_available, range_add_player):
    """
    先頭のlimit_num以下は無条件参加
    limit_numより大きい参加者はプールが閾値以上たまっている場合、range_add_playerずつ参加
    """
    # 現時点の参加している人数
    active_user_count = sum(value for value in player_available.values())

    # ランキングプールの中で１つでも閾値を超えている場合、参加ユーザを追加していく
    if any(pool >= config.motivation_pot_amount for pool in ranking_pools):
        index = find_first_false_index(player_available)

        # 全てのプレイヤーが参加状態
        if index is None:
            None
        # ユーザの追加 全体のプレイヤー数より、追加しようとしている人数か多い場合の考慮
        elif active_user_count + range_add_player > config.total_player_count:
            for i in range(config.total_player_count - active_user_count):
                player_available[index + i] = True
        # ユーザの追加
        else:
            for i in range(range_add_player):
                player_available[index + i] = True

        new_active_user_count = sum(value for value in player_available.values())
        resize_pool(new_active_user_count)

def resize_pool(new_active_user_count):
    """
    poolのサイズをプレイヤー人数に応じて増減させる
    :return:
    """
    # TODO poolの減算ロジック

    # 現在の参加人数で開放されておくべきランキング数
    expected_ranking_num = int(new_active_user_count * config.opening_ranking_per_active_player)
    # 追加が必要なランキングの個数
    compensation_ranking = expected_ranking_num - len(ranking_pools)

    while compensation_ranking > 0:
        add_pool_size()
        compensation_ranking -= 1

    update_distribution()

def add_pool_size():
    global management_pay
    ranking_pools.append(config.min_default_amount)
    management_pay += 1
    current_ranking.append(0)
    count_update_ranking.append(0)
    ranking_distribution.append(0)
    previous_pools.append(0)

def update_distribution():
    global ranking_distribution
    ranking_distribution = calc_distribution.getRecursiveDistribution(len(ranking_pools))


def find_first_false_index(my_dict):
    # 辞書の各要素（キーと値）を順番にチェック
    for index, (key, value) in enumerate(my_dict.items()):
        # 最初のFalseを見つけたら、そのインデックスを返す
        if value is False:
            return index
    # Falseが見つからなかった場合
    return None

def chek_round():
    # ゲーム参加人数
    true_count = sum(value for value in player_available.values())

    counter = 0
    for i in range(true_count - 1):
        counter += play_counter[i]

    return counter > 0

def get_active_user(player_available):
    true_count = sum(value for value in player_available.values())
    return true_count

# 結果格納用
results = []

### initialize ###
# プレイヤーのプレイ回数を減算するためDict生成
play_counter = {}
for key in range(config.total_player_count):
    play_counter[key] = config.player_motivation_count

# プレイヤーが参加状態かどうか判定するためDict生成
player_available = {}
for key in range(config.total_player_count):
    player_available[key] = False

# 先頭のlimit_num人をゲームに参加させる
for i in range(config.start_player_count):
    player_available[i] = True

# 開始人数に応じてプールの初期値を設定
for i in range(int(config.start_player_count * config.opening_ranking_per_active_player)):
    ranking_pools.append(config.min_default_amount)
    current_ranking.append(0)
    count_update_ranking.append(0)

# 分配率の初期値
ranking_distribution = calc_distribution.getRecursiveDistribution(len(ranking_pools))

### 実行 ###
while sum(play_counter.values()) > 0:
    # playerの参加不参加を判定
    judge_player(ranking_pools, player_available, config.join_player_count_per_sprint)

    # ランキング更新がPodの金額が貯まらず終了したときに処理をとめる
    if chek_round() is False:
        break
    for player_id in range(len(player_available)):
        # 参加チェック
        if bet_check(player_id, play_counter, player_available):
            # アクティブユーザ加算
            # active_user = get_active_user(player_available)
            # 運営プールとランキングプールへのBetの分配
            total_bet_amount += 1
            bet.bet_to_pools(management_pool, ranking_pools, config.bet_amount, config.management_fee_rate, ranking_distribution)
            player_result_win_lose[player_id][0] += 1

            # play回数の減算
            play_counter[player_id] = play_counter[player_id] - 1
            # スコアの決定
            score = play_game.getRandomScore()

            # ランキング更新の確認と処理
            for i in range(len(current_ranking)):
                if score > current_ranking[i]:

                    # ランキング更新者のNoを登録
                    update_ranking_user.append(player_id)

                    # ランキング更新できたため、プレイ回数をリセット
                    play_counter[player_id] = config.player_motivation_count

                    previous_pools = ranking_pools.copy()

                    # ランキングプールの更新
                    ranking_pools = update_pool(ranking_pools, i)
                    # ランキングScore更新
                    current_ranking = score_ranking.update_score_ranking(current_ranking, score)

                    # プレイヤーの獲得金額
                    player_earning = previous_pools[i]

                    # 集計用データ: 合計獲得金額
                    total_player_earnings += player_earning

                    # 結果の記録
                    ranking = 1 + i
                    results.append(output_factory.result_factory(
                        ranking, score, player_earning, player_id, total_bet_amount, previous_pools, current_ranking))
                    # sammary data
                    count_update_ranking[i] += 1
                    player_result_win_lose[player_id][1] += player_earning
                    player_result_win_lose[player_id][2] += 1

                    break

### 集計 ###
# ゲームに参加できなかった人数
not_available_num = sum(not value for value in player_available.values())
# ゲームの残回数が残った回数
residue_play_count = sum(play_counter.values())
# Resltのフォーマット修正
results = output_factory.results_factory(results, len(ranking_pools))

# 表示テスト用サンプル出力
#sample_output = results[:10] if len(results) >= 10 else results

# 結果をTSVファイルに書き込む
#output_path = Path("/mnt/data/simulation_results.tsv")
output_path = Path("SimulationOutPut/playData_flexibleRanking_uu.csv")
results.to_csv(output_path, index=False)
player_lose_win_output_path = Path("SimulationOutPut/player_lose_win_uu.csv")
player_result = output_factory.player_results_factory(player_result_win_lose)
player_result.to_csv(player_lose_win_output_path, index=True)

output_path.resolve()
player_lose_win_output_path.resolve()
print("ranking num: " + str(len(count_update_ranking)))
print("not join num: " + str(not_available_num))
print("residue count: " + str(residue_play_count))
print("sum residue pools: " + str(sum(ranking_pools)))
print("user earn:" + str(total_player_earnings))
print("update ranking count: " + str(sum(count_update_ranking)))
print("total_bet_amount: " + str(total_bet_amount))
print("total_bet_amount * 0.9: " + str(total_bet_amount* 0.9))
print("total_management_amount: " + str(total_bet_amount * config.management_fee_rate) + "$")
print("ranking update unique user:" + str(len(set(update_ranking_user))))
print("management_pay: " + str(management_pay))
print("win_player_count: " + str(player_result.query('勝ち==True').count()))
