import math
import random
import csv
from pathlib import Path

# シミュレーションの設定
from scipy.integrate import quad
from scipy.optimize import fsolve

player_count = 1000  # プレイヤー数
max_attempts_per_player = 20  # プレイヤーごとの最大試行回数
min_score = 0  # 最小スコア
max_score = 65536  # 最大スコア
limit_num = 100  # 加熱度パラメータ
limit_pool_size = 100
bet_amount = 1  # $

# 運営関連の設定
management_distribution = 0.1
management_pool = 0

# ランキング設定
ranking_num = 250  # ランキング解放数
ranking_pools = []  # ランキングプール
ranking_distribution = []  # ランキングの分配率
current_ranking = []  # 現在のランキングスコア
total_player_earnings = 0

# 集計用データ
count_update_ranking = []
bet_judge = [0, 0, 0]  # bet/unbetの集計　参加人数の下限値,上限かつlimit以上のプールサイズ、サイズが小さくBetしなかった
total_bet_amount = 0
update_ranking_user = []

def getReward(rank):
    """
    Calculate the reward based on the ranking position.

    Parameters:
    rank (int): The ranking position.

    Returns:
    float: The reward for the given rank.
    """
    A = 0.40496
    B = 0.3
    reward = A * math.exp(-B * rank)
    return reward

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
    # 運営プールの更新
    management_pool += bet_amount * management_distribution
    # 補填金額残金（補填金額が0.1のとき、過剰に補填してしまうため0.1を補填した後残りのBet金額を分配する）
    # 実質Bet金額
    # 運営プールを引いた額　かつ　補填が必要なプールに分配した残余金額
    # 初期値は、Betから運営費用を引いた額
    surplus_amount = bet_amount * (1 - management_distribution)

    # 補填金額チェック
    for i in range(1, len(ranking_pools)):
        # 1位と現在のランキングの分配率から比率を計算
        ratio = ranking_distribution[i] / ranking_distribution[0]
        # 1位に溜まっているプールと比率を掛けて、現在のランキングに溜まっておくべき金額を算出
        expected_amount = ranking_pools[0] * ratio

        # 補填金額
        compensation_amount = expected_amount - ranking_pools[i]
        # 補填が必要な場合
        if compensation_amount > 0:
            # 補填金額が１回のBetで足りない
            # surplus_amount(ユーザの残りBet金額):0.9 expected_amount（貯まっておくべき金額）:100
            if surplus_amount < compensation_amount:
                ranking_pools[i] += surplus_amount
                surplus_amount = 0
                break
            # 補填金額が１回のBetで足りる
            # surplus_amount(ユーザの残りBet金額):0.2 expected_amount（貯まっておくべき金額）:0.1
            else:
                ranking_pools[i] += compensation_amount
                # bet金額から補填した金額を減らす
                surplus_amount -= compensation_amount

    # ランキングプールの分配
    if surplus_amount > 0:
        for i in range(len(ranking_pools)):
            ranking_pools[i] += surplus_amount * ranking_distribution[i]

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

def bet_check(player_id, ranking_pools, bet_judge):
    if player_id < limit_num:
        bet_judge[0] += 1
        return True
    elif any(pool >= limit_pool_size for pool in ranking_pools):
        bet_judge[1] += 1
        return True
    else:
        bet_judge[2] += 1
        return False

def integrand(x, A, B):
    return A * math.exp(-B * x)

def equation(p, max_rank):
    A, B = p
    integral, _ = quad(integrand, 1, max_rank, args=(A, B))
    rank1_reward = A * math.exp(-B * 1) - 0.30  # 最高ランクの報酬率を30%に設定
    return (integral - 1, rank1_reward)

def calculateAB(max_rank):
    initial_guess = (1, 0.1)
    A, B = fsolve(equation, initial_guess, args=(max_rank))
    return A, B

def getRewardDistribution(max_rank):
    A, B = calculateAB(max_rank)
    rewards = [A * math.exp(-B * x) for x in range(1, max_rank + 1)]
    return rewards

def normalizeRewards(rewards):
    total = sum(rewards)
    normalized_rewards = [r / total for r in rewards]
    return normalized_rewards

# シミュレーションのプログラムにこれらの関数を組み込む
results = []

# ランキング開放数に合わせてpool等を生成
for i in range(ranking_num):
    ranking_pools.append(0)
    current_ranking.append(0)
    count_update_ranking.append(0)

# ランキングが1位から6位までの場合の報酬分配率を計算
reward_distribution = getRewardDistribution(len(ranking_pools))
ranking_distribution = normalizeRewards(reward_distribution)

# プレイヤーのプレイ回数を減算するためDict生成
play_counter = {}
for key in range(player_count):
    play_counter[key] = max_attempts_per_player

while_counter = 0
ifconter = 0
while sum(play_counter.values()) > 0:
    for player_id in range(player_count):
        before_pools = ranking_pools.copy()
        before_total_player_earnings = total_player_earnings
        # どこかのpoolが100超えていない場合、先頭100人のみ参加
        if bet_check(player_id, ranking_pools, bet_judge):
            # 運営プールとランキングプールへのBetの分配
            total_bet_amount += 1
            distribute_bet_to_pools(management_pool, ranking_pools, bet_amount)
            play_counter[player_id] -= 1
            # スコアの決定
            score = random.randint(min_score, max_score)

            # ランキング更新の確認と処理
            for i in range(len(current_ranking)):
                if score > current_ranking[i]:

                    previous_pools = ranking_pools.copy()

                    # ランキング更新者のNoを登録
                    update_ranking_user.append(player_id)

                    # ランキングプールの更新
                    ranking_pools = update_pool(ranking_pools, i)
                    # ランキングScore更新
                    current_ranking = update_ranking_score(current_ranking, score)

                    # プレイヤーの獲得金額
                    player_earning = previous_pools[i]

                    play_counter[player_id] = max_attempts_per_player

                    # 集計用データ: 合計獲得金額
                    total_player_earnings += player_earning

                    # 結果の記録
                    ranking = 1 + i
                    results.append(result_factory(
                        ranking, score, player_earning, player_id, total_bet_amount,previous_pools, current_ranking))
                    # sammary data
                    count_update_ranking[i] += 1

                    break
        # if sum(ranking_pools) + total_player_earnings - total_bet_amount * 0.9 and ifconter ==0:
        #     ifconter +=1
        #     print("before pool" + str(before_pools))
        #     print("before pool sum" + str(sum(before_pools)))
        #     print("user earn before:" + str(before_total_player_earnings))
        #     print("after pool" + str(ranking_pools))
        #     print("after pool sum" + str(sum(ranking_pools)))
        #     print("user earn after:" + str(total_player_earnings))


# 表示テスト用サンプル出力
#sample_output = results[:10] if len(results) >= 10 else results

# 結果をTSVファイルに書き込む
#output_path = Path("/mnt/data/simulation_results.tsv")
output_path = Path("SimulationOutPut/playData_fixed_longpool.csv")
with output_path.open("w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',')
    headers = [
        "更新順位", "ユーザ獲得金額", "ユーザNo", "スコア", "合計Bet金額",
        "1位ランキングプール", "2位ランキングプール", "3位ランキングプール",
        "4位ランキングプール", "5位ランキングプール", "6位ランキングプール",
        "1位スコア", "2位スコア", "3位スコア", "4位スコア", "5位スコア", "6位スコア"
    ]
    writer.writerow(headers)
    for row in results:
        writer.writerow(row)

output_path.resolve()
print("update ranking count: " + str(sum(count_update_ranking)))
print("total_bet_amount: " + str(total_bet_amount))
print("total_management_amount: " + str(total_bet_amount * (1 - management_distribution)) + "$")
print("residue pool:" + str(sum(ranking_pools)))
print("total user earn:" + str(total_player_earnings))
print("ranking update unique user:" + str(len(set(update_ranking_user))))


