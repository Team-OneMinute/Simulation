## TODO: 未移行なので移行する
def adjust_active_player(ranking_pools, player_available, range_add_player, limit_pool_size, player_count):
    """
    先頭のlimit_num以下は無条件参加
    limit_numより大きい参加者はプールが閾値以上たまっている場合、range_add_playerずつ参加
    """

    def find_first_false_index(my_dict):
        # 辞書の各要素（キーと値）を順番にチェック
        for index, (key, value) in enumerate(my_dict.items()):
            # 最初のFalseを見つけたら、そのインデックスを返す
            if value is False:
                return index
        # Falseが見つからなかった場合
        return None

    def resize_pool(new_active_user_count):
        """
        poolのサイズをプレイヤー人数に応じて増減させる
        :return:
        """
        # TODO poolの減算ロジック

        # 現在の参加人数で開放されておくべきランキング数
        expected_ranking_num = int(new_active_user_count * default_ranking_rate)
        # 追加が必要なランキングの個数
        compensation_ranking = expected_ranking_num - len(ranking_pools)

        while compensation_ranking > 0:
            add_pool_size()
            compensation_ranking -= 1

        update_distribution()
    def add_pool_size():
        global management_pay
        ranking_pools.append(min_default_amount)
        management_pay += 1
        current_ranking.append(0)
        count_update_ranking.append(0)
        ranking_distribution.append(0)
        previous_pools.append(0)

    # 現時点の参加している人数
    active_user_count = sum(value for value in player_available.values())

    # ランキングプールの中で１つでも閾値を超えている場合、参加ユーザを追加していく
    if any(pool >= limit_pool_size for pool in ranking_pools):
        index = find_first_false_index(player_available)

        # 全てのプレイヤーが参加状態
        if index is None:
            None
        # ユーザの追加 全体のプレイヤー数より、追加しようとしている人数か多い場合の考慮
        elif active_user_count + range_add_player > player_count:
            for i in range(player_count - active_user_count):
                player_available[index + i] = True
        # ユーザの追加
        else:
            for i in range(range_add_player):
                player_available[index + i] = True

        new_active_user_count = sum(value for value in player_available.values())
        resize_pool(new_active_user_count)