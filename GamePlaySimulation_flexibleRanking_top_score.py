import random
from pathlib import Path
# シミュレーションの設定
import pandas as pd

"""
ランキング変動型シミュレーション
ランキング1位が変更される度に、次のランキングが開放される
"""

player_count = 1000  # プレイヤー数
max_attempts_per_player = 70  # プレイヤーごとの最大試行回数 ランキングを更新できないと諦める
min_score = 0  # 最小スコア
max_score = 65536  # 最大スコア
# 加熱度パラメータ bet金額がlimit_pool_size貯まったら全員参加させる。それ以外はlimit_numだけが参加
limit_num = 100
limit_pool_size = 100

bet_amount = 1  # $

# ランキングと報酬の設定
management_distribution = 0.1 # 運営Fee
management_pool = 0 # 運営の獲得プール
ranking_pools = [0]  # ランキングプール　初期はLength 1　ランキングが更新される度にaddされる

# ランキングの分配率
# ランキング１位が更新されるたびに次のランキングプールが開放される
ranking_distribution = [1]
current_ranking = [0]  # 現在のランキングスコア
total_player_earnings = 0

# 集計用データ
count_update_ranking = [0]
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

    #  補填金額チェック
    #  ranking プールが１つ（まだランキング1位が一度も更新されてない）
    if len(ranking_pools) != 1:
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

def add_ranking_pool(ranking_pools, rank):
    # 1位更新のときだけ
    if rank == 0:
        ranking_pools.append(0)
        return ranking_pools
    else:
        return ranking_pools

def add_current_ranking(current_ranking, rank):
    if rank == 0:
        current_ranking.append(0)
        return current_ranking
    else:
        return current_ranking

def add_counter(count_update_ranking, rank):
    if rank == 0:
        count_update_ranking.append(0)
        return count_update_ranking
    else:
        return count_update_ranking

def add_previous_pools(previous_pools, rank):
    if rank == 0:
        previous_pools.append(0)
        return previous_pools
    else:
        return previous_pools

def add_ranking_distribution(ranking_distribution, rank):
    #  分配率の追加ロジック
    #  基本的には1位50％ 2位25%...
    #  足して100％にする必要があるので最後の２要素のみ残り金額を7：3で分配する
    last_distribution1 = 0.7
    last_distribution2 = 0.3

    #  初めての1位ランキング更新
    if len(ranking_distribution) == 1:
        ranking_distribution = [0.7, 0.3]
        return ranking_distribution
    elif len(ranking_distribution) == 2:
        ranking_distribution = [0.5, 0.35, 0.15]
        return ranking_distribution
    else:
        #  [0.5, 0.35, 0.15, 0]
        #  [0.5, 0.25, 0.175, 0.075]
        #  [0.5, 0.25, 0.175, 0.075, 0]
        #  [0.5, 0.25, 0.125, 0.0875, 0.0375]
        ranking_distribution.append(0)
        tmp = ranking_distribution[len(ranking_distribution) - 4]
        ranking_distribution[len(ranking_distribution) - 3] = tmp / 2
        ranking_distribution[len(ranking_distribution) - 2] = \
            ranking_distribution[len(ranking_distribution) - 3] * last_distribution1
        ranking_distribution[len(ranking_distribution)-1] = \
            ranking_distribution[len(ranking_distribution) - 2] * last_distribution2
        return ranking_distribution

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

# 結果格納用
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

                    # ranking 1位のときプールの開放を行う
                    ranking_pools = add_ranking_pool(ranking_pools, i)
                    current_ranking = add_current_ranking(current_ranking, i)
                    count_update_ranking = add_counter(count_update_ranking, i)
                    ranking_distribution = add_ranking_distribution(ranking_distribution, i)
                    previous_pools = add_previous_pools(previous_pools, i)

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

                    # print("player_id:" + str(player_id) + "  score:" + str(score))
                    break

# 最終集計
results = results_factory(results, len(ranking_pools))

# 表示テスト用サンプル出力
#sample_output = results[:10] if len(results) >= 10 else results

# 結果をTSVファイルに書き込む
#output_path = Path("/mnt/data/simulation_results.tsv")
output_path = Path("SimulationOutPut/playData_flexibleRanking_top_score.csv")
results.to_csv(output_path, index=False)

output_path.resolve()
print("update count: " + str(count_update_ranking))
print("update ranking count: " + str(sum(count_update_ranking)))
print("total_bet_amount: " + str(total_bet_amount))
print("total_management_amount: " + str(total_bet_amount * management_distribution) + "$")
print("lowBet/highBet/unbet: " + str(bet_judge))