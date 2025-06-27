# CC98 API配置示例
# 请复制此文件为 cc98_config.py 并填入您的认证信息

CC98_CONFIG = {
    "username": "your_cc98_username",  # 请填入您的CC98用户名
    "password": "your_cc98_password",  # 请填入您的CC98密码
    "client_id": "9a1fd200-8687-44b1-4c20-08d50a96e5cd",
    "client_secret": "8b53f727-08e2-4509-8857-e34bf92b27f2",
    "api_base_url": "https://api.cc98.org",
    "auth_url": "https://openid.cc98.org/connect/token"
}

# 使用说明：
# 1. 复制此文件为 cc98_config.py
# 2. 将 your_cc98_username 替换为您的CC98用户名
# 3. 将 your_cc98_password 替换为您的CC98密码
# 4. 保存文件
# 5. 重启后端服务

# 注意：请确保您的CC98账号有效且有API访问权限 