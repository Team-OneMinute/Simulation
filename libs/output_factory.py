### 集計結果のファイル出力関連の処理を行う

import pandas as pd
from libs import utils

def result_factory(ranking, score, player_earning, player_id, total_bet_amount,previous_pools, current_ranking):
    return [
        ranking,
        utils.format_decimal(player_earning),
        player_id,
        score,
        utils.format_decimal(total_bet_amount),
        *[utils.format_decimal(pool) for pool in previous_pools],
        *[utils.format_decimal(score) for score in current_ranking]
    ]

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

def player_results_factory(results):
    """
    リスト形式のデータを受け取り、プレイヤーのbet金額と獲得金額を持つデータフレームを生成する。

    :param results: リスト形式のデータ
    :return: データフレーム
    """
    # ヘッダーを生成
    headers = ['bet金額', '合計獲得金額', 'ランキング更新回数']

    df = pd.DataFrame(results, columns=headers)
    df['勝ち'] = df['bet金額'] < df['合計獲得金額']
    return df