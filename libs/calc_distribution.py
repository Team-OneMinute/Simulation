import math
from scipy.optimize import fsolve
from scipy.integrate import quad

"""
段階的な分配率の計算
Args:
    ranking_num: ランキングの個数
    top_percentage: ランキング中の上位層の割合
    middle_percentage: ランキング中の中位層の割合
    bottom_percentage: ランキング中の下位層の割合
    top_reward: 全体に占める上位層への報酬の割合
    middle_reward: 全体に占める中位層への報酬の割合
    bottom_reward: 全体に占める下位層への報酬の割合
"""
def getRecursiveDistribution(ranking_num, top_percentage=0.1, middle_percentage=0.4, bottom_percentage=0.5,
                             top_reward=0.5, middle_reward=0.3, bottom_reward=0.2):

    """
    分配率の計算（再帰関数）
    """
    def calculate_distribution(num_ranks, reward, current_top_percentage, current_middle_percentage):
        """
        Helper function to calculate the distribution for a given segment of ranks.
        """
        segment_distribution = []
        for rank in range(1, num_ranks + 1):
            if rank <= num_ranks * current_top_percentage:  # Top percentage ranks in the segment
                segment_distribution.append(reward / (num_ranks * current_top_percentage))
            elif rank <= num_ranks * (current_top_percentage + current_middle_percentage):  # Middle percentage ranks in the segment
                segment_distribution.append(reward / (num_ranks * current_middle_percentage))
            else:  # Bottom percentage ranks in the segment
                segment_distribution.append(reward / (num_ranks * (1 - current_top_percentage - current_middle_percentage)))

        return segment_distribution

    # Calculate the raw distribution for the entire set of rankings
    raw_distribution = []
    top_ranks_num = int(ranking_num * top_percentage)
    middle_ranks_num = int(ranking_num * middle_percentage)

    # Apply the distribution recursively within the top and middle ranks
    raw_distribution.extend(calculate_distribution(top_ranks_num, top_reward, top_percentage, middle_percentage))
    raw_distribution.extend(calculate_distribution(middle_ranks_num, middle_reward, top_percentage, middle_percentage))

    # Calculate distribution for the bottom ranks
    bottom_ranks_num = ranking_num - top_ranks_num - middle_ranks_num
    raw_distribution.extend([bottom_reward / bottom_ranks_num] * bottom_ranks_num)

    # Normalize the distribution to sum up to 1
    total = sum(raw_distribution)
    normalized_distribution = [value / total for value in raw_distribution]

    return normalized_distribution

"""
指数関数をもとにした分配率の計算
Args:
    size: ランキングのサイズ
"""
def getExponentialDistribution(size):
    def getRewardDistribution(max_rank):
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

        A, B = calculateAB(max_rank)
        rewards = [A * math.exp(-B * x) for x in range(1, max_rank + 1)]
        return rewards

    def normalizeRewards(rewards):
        total = sum(rewards)
        normalized_rewards = [r / total for r in rewards]
        return normalized_rewards

    reward_distribution = getRewardDistribution(size)
    return normalizeRewards(reward_distribution)
