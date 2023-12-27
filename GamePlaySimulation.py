import pandas as pd
import numpy as np

NUM_PLAYERS = 1000
MAX_PLAYS_PER_PLAYER = 10
MAX_RANKING_UPDATES = 10
BET_AMOUNT = 1
MAX_SCORE = 65536

def simulate_game(num_players, max_plays_per_player, max_ranking_updates, bet_amount, max_score):
    total_bet = 0
    top_score = 1
    ranking_updates = []
    players_attempts = {player: 0 for player in range(num_players)}

    while len(ranking_updates) < max_ranking_updates and any(attempts < max_plays_per_player for attempts in players_attempts.values()):
        active_players = range(100) if total_bet < 100 else range(num_players)

        for player in active_players:
            if players_attempts[player] < max_plays_per_player:
                score = np.random.randint(0, max_score)
                total_bet += bet_amount
                players_attempts[player] += 1

                if score > top_score:
                    top_score = score
                    player_payout = total_bet * 0.90
                    operator_payout = total_bet * 0.10
                    ranking_updates.append({
                        "User Payout": player_payout,
                        "Operator Payout": operator_payout,
                        "Top Score": top_score,
                        "Total Bet": total_bet
                    })
                    break

    return ranking_updates

game_results = simulate_game(NUM_PLAYERS, MAX_PLAYS_PER_PLAYER, MAX_RANKING_UPDATES, BET_AMOUNT, MAX_SCORE)
df_game_results = pd.DataFrame(game_results)
df_game_results['Ranking Update Count'] = df_game_results.index + 1
df_game_results['Player Number'] = [np.nan] * len(df_game_results)

players_attempts = {player: 0 for player in range(NUM_PLAYERS)}
total_bet = 0
top_score = 1

for update in df_game_results.itertuples():
    active_players = range(100) if total_bet < 100 else range(NUM_PLAYERS)

    for player in active_players:
        if players_attempts[player] < MAX_PLAYS_PER_PLAYER:
            score = np.random.randint(0, MAX_SCORE)
            total_bet += BET_AMOUNT
            players_attempts[player] += 1

            if score > top_score:
                top_score = score
                df_game_results.at[update.Index, 'Player Number'] = player
                break

df_game_results = df_game_results[['Ranking Update Count', 'User Payout', 'Operator Payout', 'Top Score', 'Total Bet', 'Player Number']]
total_user_payout = df_game_results['User Payout'].sum()
total_operator_payout = df_game_results['Operator Payout'].sum()
total_bet_amount = df_game_results['Total Bet'].sum()

total_row_fixed = {
    "Ranking Update Count": "Total",
    "User Payout": total_user_payout,
    "Operator Payout": total_operator_payout,
    "Top Score": "-",
    "Total Bet": total_bet_amount,
    "Player Number": "-"
}

df_game_results_with_total_fixed = df_game_results.append(total_row_fixed, ignore_index=True)
