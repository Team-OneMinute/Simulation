import random
from pathlib import Path
# シミュレーションの設定
import pandas as pd

import math
from scipy.optimize import fsolve
from scipy.integrate import quad

"""
ランキング変動型シミュレーション
ユニークユーザ数がふえる度にランキングが開放される。
また、ユニーク数が減る度にランキングが減っていく
"""

player_count = 1000  # プレイヤー数
max_attempts_per_player = 20  # ランキングを更新できないと諦める回数
min_score = 0  # 最小スコア
max_score = 65536  # 最大スコア
# 加熱度パラメータ bet金額がlimit_pool_size貯まったら全員参加させる。それ以外はlimit_numだけが参加
limit_num = 100
limit_pool_size = 100
# ランキング戦に参加する人数のレンジ
range_add_player = 10

# bet金額
bet_amount = 1  # $

# ランキングと報酬の設定
management_distribution = 0.1 # 運営Fee
management_pool = 0 # 運営の獲得プール
ranking_pools = [0, 0, 0, 0, 0]  # ランキングプール　初期はLength 1　ランキングが更新される度にaddされる

# ランキングの分配率
# ランキング１位が更新されるたびに次のランキングプールが開放される
ranking_distribution = []
current_ranking = [0, 0, 0, 0, 0]  # 現在のランキングスコア
total_player_earnings = 0

# ユニークユーザ数
active_user = 0

# 集計用データ
count_update_ranking = [0, 0, 0, 0, 0]
total_bet_amount = 0
update_ranking_user = []

def update_pool(ranking_pools, updated_rank):
    """
    ランキングプールの更新
    更新ロジック：上位スライド式
    1位のランキング更新があった場合、1位のランキングプールが空になるので
    2位以下のプールが上位のプールに移動する。よって、最下位プールが空になる
    空になったプールは、Betのロジックで別に補填ロジックを持つ
    """
    ranking_pools[updated_rank] = 0  # 更新されたランキングのプールをリセット
    if len(ranking_pools) != updated_rank + 1:
        for j in range(updated_rank, len(ranking_pools) - 1):
                ranking_pools[j] = ranking_pools[j + 1]
    ranking_pools[len(ranking_pools) - 1] = 0
    return ranking_pools

def distribute_bet_to_pools(management_pool, ranking_pools, bet_amount):
    """
    Betの分配
    運営プールとランキングプールに分配を行う
    """
    reward_distribution = getRewardDistribution(len(ranking_pools))
    # 運営プールの更新
    management_pool += bet_amount * management_distribution
    # 補填金額残金（補填金額が0.1のとき、過剰に補填してしまうため0.1を補填した後残りのBet金額を分配する）
    # 実質Bet金額
    # 運営プールを引いた額　かつ　補填が必要なプールに分配した残余金額
    # 初期値は、Betから運営費用を引いた額
    surplus_amount = bet_amount * (1 - management_distribution)

    #  補填金額チェック
    #  ranking プールが１つ（まだランキング1位が一度も更新されてない）
    if len(ranking_pools) != 1:
        for i in range(1, len(ranking_pools)):
            # 1位と現在のランキングの分配率から比率を計算
            ratio = reward_distribution[i] / reward_distribution[0]
            # 1位に溜まっているプールと比率を掛けて、現在のランキングに溜まっておくべき金額を算出
            expected_amount = ranking_pools[0] * ratio

            # 現在のプールと比較し、補填が必要な場合は補填金額を計算
            if ranking_pools[i] < expected_amount:
                # 補填金額が１回のBetで足りない
                if surplus_amount - expected_amount < 0:
                    ranking_pools[i] += surplus_amount
                    break
                # 補填金額が１回のBetで足りる
                else:
                    surplus_amount -= expected_amount
                    ranking_pools[i] += expected_amount

    # ランキングプールの分配
    if surplus_amount > 0:
        for i in range(len(ranking_pools)):
            ranking_pools[i] += surplus_amount * reward_distribution[i]

def update_ranking_score(current_ranking, score):
    """
    与えられたスコアに基づいてランキングを更新する。
    """
    updated_rank = -1  # ランキングが更新されなかった場合のデフォルト値
    for i in range(len(current_ranking)):
        if score > current_ranking[i]:
            updated_rank = i
            break

    if updated_rank >= 0:
        # ランキングが更新された場合、スコアを挿入し、古いスコアを下にずらす
        current_ranking.insert(updated_rank, score)
        current_ranking.pop()  # 最下位のスコアを削除
    return current_ranking

def format_decimal(value):
    """
    金額の表示を小数点以下2位でカットする。
    """
    if isinstance(value, float):
        return round(value, 2)
    return value

def result_factory(ranking, score, player_earning, player_id, total_bet_amount,previous_pools, current_ranking):
    return [
        ranking,
        format_decimal(player_earning),
        player_id,
        score,
        format_decimal(total_bet_amount),
        *[format_decimal(pool) for pool in previous_pools],
        *[format_decimal(score) for score in current_ranking[:i]],
        format_decimal(score),
        *[format_decimal(score) for score in current_ranking[i+1:]]
    ]

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

def results_factory(results, num_columns):
    """
    リスト形式のデータを受け取り、指定された数のランキングプールとスコアカラムを持つデータフレームを生成する。

    :param results: リスト形式のデータ
    :param num_columns: ランキングプールとスコアのカラム数
    :return: データフレーム
    """
    # ヘッダーを生成
    headers = ['更新順位', 'ユーザ獲得金額', 'ユーザNo', 'スコア', '合計Bet金額']
    headers += [f'p{i+1}' for i in range(num_columns)]
    headers += [f's{i+1}' for i in range(num_columns)]

    # [1, 0.9, 1, 29326, 1, 0.9, 0, 29326, 0]
    # [1, 0.63, 1, 57232, 2, 0.63, 0.27, 0, 57232, 29326, 0]
    # [3, 0.18, 1, 16045, 3, 0.59, 0.41, 0.18, 57232, 29326, 16045]
    # [1, 4.79, 3, 57401, 14, 4.79, 2.81, 1.31, 0, 57401, 57232, 51748, 51515]
    for i in range(len(results)):
        now_column_num = int((len(results[i]) - 5) / 2) # 0埋め前のカラム数
        expected_column_num = num_columns   # 全体で必要なカラム数
        padding_num = expected_column_num - now_column_num

        # 桁埋めが必要なとき
        padding_index = len(results[i]) - now_column_num
        while padding_num > 0:
            results[i].insert(padding_index, 0)
            results[i].append(0)
            padding_num -= 1
    df = pd.DataFrame(results, columns=headers)
    return df

def judge_player(ranking_pools, player_available, range_add_player):
    """
    先頭のlimit_num以下は無条件参加
    limit_numより大きい参加者はプールが閾値以上たまっている場合、range_add_playerずつ参加
    """
    true_count = sum(value for value in player_available.values())
    if any(pool >= limit_pool_size for pool in ranking_pools):
        index = find_first_false_index(player_available)

        # 全てのプレイヤーが参加状態
        if index is None:
            None
        elif true_count + range_add_player > player_count:
            for i in range(player_count - true_count):
                player_available[index + i] = True
            ranking_pools.append(0)
            current_ranking.append(0)
            count_update_ranking.append(0)
            ranking_distribution.append(0)
            previous_pools.append(0)
        else:
            for i in range(range_add_player):
                player_available[index + i] = True
            ranking_pools.append(0)
            current_ranking.append(0)
            count_update_ranking.append(0)
            ranking_distribution.append(0)
            previous_pools.append(0)

def find_first_false_index(my_dict):
    # 辞書の各要素（キーと値）を順番にチェック
    for index, (key, value) in enumerate(my_dict.items()):
        # 最初のFalseを見つけたら、そのインデックスを返す
        if value is False:
            return index
    # Falseが見つからなかった場合
    return None

def integrand(x, A, B):
    return A * math.exp(-B * x)

def equation(p, max_rank):
    A, B = p
    integral, _ = quad(integrand, 1, max_rank, args=(A, B))
    return (integral - 1, 0)

def calculateAB(max_rank):
    initial_guess = (1, 0.1)
    A, B = fsolve(equation, initial_guess, args=(max_rank))
    return A, B

def getRewardDistribution(max_rank):
    A, B = calculateAB(max_rank)
    rewards = [A * math.exp(-B * x) for x in range(1, max_rank + 1)]
    return rewards

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

# プレイヤーのプレイ回数を減算するためDict生成
play_counter = {}
for key in range(player_count):
    play_counter[key] = max_attempts_per_player

# プレイヤーが参加状態かどうか判定するためDict生成
player_available = {}
for key in range(player_count):
    player_available[key] = False

# 先頭のlimit_num人をゲームに参加させる
for i in range(limit_num):
    player_available[i] = True

# 分配率の初期値
ranking_distribution = getRewardDistribution(len(ranking_pools))
counter = 1
while sum(play_counter.values()) > 0:
    # playerの参加不参加を判定
    judge_player(ranking_pools, player_available, range_add_player)

    # ランキング更新がPodの金額が貯まらず終了したときに処理をとめる
    if chek_round() is False:
        break
    for player_id in range(len(player_available)):
        # 参加チェック
        if bet_check(player_id, play_counter, player_available):
            # アクティブユーザ加算
            active_user = get_active_user(player_available)
            # 運営プールとランキングプールへのBetの分配
            total_bet_amount += 1
            distribute_bet_to_pools(management_pool, ranking_pools, bet_amount)

            # play回数の減算
            play_counter[player_id] = play_counter[player_id] - 1
            # スコアの決定
            score = random.randint(min_score, max_score)

            # ランキング更新の確認と処理
            for i in range(len(current_ranking)):
                if score > current_ranking[i]:

                    # ランキング更新者のNoを登録
                    update_ranking_user.append(player_id)

                    # ランキング更新できたため、プレイ回数をリセット
                    play_counter[player_id] = max_attempts_per_player

                    previous_pools = ranking_pools.copy()

                    # ランキングプールの更新
                    ranking_pools = update_pool(ranking_pools, i)
                    # ランキングScore更新
                    current_ranking = update_ranking_score(current_ranking, score)

                    # プレイヤーの獲得金額
                    player_earning = previous_pools[i]

                    # 集計用データ: 合計獲得金額
                    total_player_earnings += player_earning

                    # 結果の記録
                    ranking = 1 + i
                    results.append(result_factory(
                        ranking, score, player_earning, player_id, total_bet_amount, previous_pools, current_ranking))
                    # sammary data
                    count_update_ranking[i] += 1

                    break
    counter += 1

# 集計
# ゲームに参加できなかった人数
not_available_num = sum(not value for value in player_available.values())
# ゲームの残回数が残った回数
residue_play_count = sum(play_counter.values())
# Resltのフォーマット修正
results = results_factory(results, len(ranking_pools))

# 表示テスト用サンプル出力
#sample_output = results[:10] if len(results) >= 10 else results

# 結果をTSVファイルに書き込む
#output_path = Path("/mnt/data/simulation_results.tsv")
output_path = Path("SimulationOutPut/playData_flexibleRanking_uu.csv")
results.to_csv(output_path, index=False)

output_path.resolve()
print("update count: " + str(count_update_ranking))
print("ranking num: " + str(len(count_update_ranking)))
print("not join num: " + str(not_available_num))
print("residue count: " + str(residue_play_count))
print("sum residue pools: " + str(sum(ranking_pools)))
print("update ranking count: " + str(sum(count_update_ranking)))
print("total_bet_amount: " + str(total_bet_amount))
print("total_management_amount: " + str(total_bet_amount * management_distribution) + "$")
print("ranking update unique user:" + str(len(set(update_ranking_user))))
