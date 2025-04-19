import vdf
import os

#你的 本地文件路径，自行修改那串数字

LOCALCONFIG_PATH = r"C:\Program Files (x86)\Steam\userdata\76561198426747673\config\localconfig.vdf"

with open(LOCALCONFIG_PATH, "r", encoding="utf-8") as f:
    data = vdf.load(f)


apps = data["UserLocalConfigStore"]["Software"]["Valve"]["Steam"]["Apps"]   
shared_games = []

for appid, app_data in apps.items():   ## 提取所有家庭共享游戏
    if "LastOwner" in app_data and app_data["LastOwner"] != STEAM_ID:
        shared_games.append({
            "AppID": appid,
            "GameName": f"Unknown (AppID: {appid})",  # 默认名称（可后续补充）
            "OwnerSteamID": app_data["LastOwner"],
            "PlaytimeMinutes": app_data.get("Playtime", 0)
        })

print(f"找到 {len(shared_games)} 个家庭共享游戏：")
for game in shared_games:
    print(f"- AppID: {game['AppID']}, 原主: {game['OwnerSteamID']}, 游玩: {game['PlaytimeMinutes']} 分钟")


import csv # 不是必要的
with open("steam_family_shared.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["AppID", "GameName", "OwnerSteamID", "PlaytimeMinutes"])
    writer.writeheader()
    writer.writerows(shared_games)
print("已导出到 steam_family_shared.csv")
