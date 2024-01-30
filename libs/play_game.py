import random

def getRandomScore():
    """
    ランダムなスコア（min(0)〜max(65536)の間の数値）を返す
    """
    min_score = 0  # 最小スコア
    max_score = 65536  # 最大スコア

    return random.randint(min_score, max_score)