import json

# JSONファイルのパス
file_path = './gameFi.json'

# ファイルからJSONデータを読み込む
with open(file_path, 'r') as file:
    parsed_data = json.load(file)

# avg_daily_activeとnameの値をリストに格納
avg_daily_active_and_name = [
    {
        "gamefi_rank": item["gamefi_rank"],
        "avg_daily_active": item["avg_daily_active"],
        "name": item["game"]["name"]
    }
    for item in parsed_data["data"]["items"]
]

print(avg_daily_active_and_name)