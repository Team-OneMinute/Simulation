import hashlib
import hmac

# Telegramボットのトークンを入力してください
bot_token = ''

# クエリパラメータ（アルファベット順にソート）
params = {
    'auth_date': '1620000000',
    'first_name': 'John',
    'id': '123456789',
    'last_name': 'Doe',
    'photo_url': 'URL',
    'username': 'johndoe'
}

# パラメータをアルファベット順に並べ替え、改行で区切る
data_check_string = '\n'.join([f"{key}={value}" for key, value in sorted(params.items())])
print(data_check_string)

# ハッシュを計算
secret = hashlib.sha256(bot_token.encode()).digest()
hash_value = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

print(hash_value)
