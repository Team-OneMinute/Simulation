def bet_to_pools(management_pool, ranking_pools, bet_amount, management_distribution, ranking_distribution):
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

            # 補填金額
            compensation_amount = expected_amount - ranking_pools[i]

            # 補填金額が必要な場合
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