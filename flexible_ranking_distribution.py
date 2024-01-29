# Define global variables for the reward distribution percentages and the corresponding ranking percentages

def getRecursiveDistribution(ranking_num, top_percentage=0.1, middle_percentage=0.4, bottom_percentage=0.5,
                             top_reward=0.5, middle_reward=0.3, bottom_reward=0.2):

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

# Example: Calculate the recursive distribution for 25 available rankings
recursive_distribution_example = getRecursiveDistribution(100)


