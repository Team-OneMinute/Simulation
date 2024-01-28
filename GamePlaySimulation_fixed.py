import random
import csv
from pathlib import Path

# シミュレーションの設定
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
ranking_pools = [0, 0, 0, 0, 0, 0]  # ランキングプール
ranking_distribution = [
    0.3,
    0.15,
    0.1125,
    0.05625,
    0.028125,
    0.028125]  # ランキングの分配率
current_ranking = [0, 0, 0, 0, 0, 0]  # 現在のランキングスコア
total_player_earnings = 0

# 集計用データ
count_update_ranking = [0, 0, 0, 0, 0, 0]
bet_judge = [0, 0, 0]  # bet/unbetの集計　参加人数の下限値,上限かつlimit以上のプールサイズ、サイズが小さくBetしなかった
total_bet_amount = 0

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

def distribute_bet_to_pools(management_pool, ranking_pools, bet_amount, distribution):
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
    compensation_flg = False

    # 補填金額チェック
    for i in range(1, len(ranking_pools)):
        # 1位と現在のランキングの分配率から比率を計算
        ratio = ranking_distribution[i] / ranking_distribution[0]
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
            ranking_pools[i] += surplus_amount * distribution[i]

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

# シミュレーションのプログラムにこれらの関数を組み込む
results = []

for player_id in range(1, player_count + 1):
    for attempt in range(max_attempts_per_player):
        # 加熱性チェック
        # どこかのpoolが100超えていない場合、先頭100人のみ参加
        if bet_check(player_id, ranking_pools, bet_judge):
            # 運営プールとランキングプールへのBetの分配
            total_bet_amount += 1
            distribute_bet_to_pools(management_pool, ranking_pools, bet_amount, ranking_distribution)

            # スコアの決定
            score = random.randint(min_score, max_score)

            # ランキング更新の確認と処理
            for i in range(len(current_ranking)):
                if score > current_ranking[i]:

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
                        ranking, score, player_earning, player_id, total_bet_amount,previous_pools, current_ranking))
                    # sammary data
                    count_update_ranking[i] += 1

                    # print("player_id:" + str(player_id) + "  score:" + str(score))
                    break

# 表示テスト用サンプル出力
#sample_output = results[:10] if len(results) >= 10 else results

# 結果をTSVファイルに書き込む
#output_path = Path("/mnt/data/simulation_results.tsv")
output_path = Path("SimulationOutPut/playData_fixed.csv")
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
print("update count: " + str(count_update_ranking))
print("update ranking count: " + str(sum(count_update_ranking)))
print("total_bet_amount: " + str(total_bet_amount))
print("total_management_amount: " + str(total_bet_amount * management_distribution) + "$")
print("lowBet/highBet/unbet: " + str(bet_judge))