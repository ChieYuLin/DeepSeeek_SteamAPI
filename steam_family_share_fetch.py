import requests
import csv
import time
from typing import List, Dict, Optional

# 配置你的 Steam API 密钥和 Steam ID
STEAM_API_KEY = "7264BAD197ECAA7F81F18C55917782FE"
STEAM_ID = "76561198426747673"  # 应该是17位数字的SteamID64

# Steam API 基础URL
STEAM_API_URL = "https://api.steampowered.com"

def get_family_group_id(steam_id: str, api_key: str) -> Optional[str]:
    """获取用户的家庭组ID"""
    url = f"{STEAM_API_URL}/IFamilyGroupsService/GetFamilyGroupForUser/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "response" in data and "family_groupid" in data["response"]:
            return str(data["response"]["family_groupid"])
        else:
            print("未找到家庭组ID，你可能不在任何家庭组中")
            return None
    except requests.exceptions.RequestException as e:
        print(f"获取家庭组ID时出错: {e}")
        return None

def get_family_members(family_group_id: str, api_key: str) -> List[Dict]:
    """获取家庭组成员列表"""
    url = f"{STEAM_API_URL}/IFamilyGroupsService/GetFamilyMembers/v1/"
    params = {
        "key": api_key,
        "family_groupid": family_group_id
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "response" in data and "members" in data["response"]:
            return data["response"]["members"]
        else:
            print("无法获取家庭成员列表")
            return []
    except requests.exceptions.RequestException as e:
        print(f"获取家庭成员时出错: {e}")
        return []

def get_shared_library_info(family_group_id: str, api_key: str) -> List[Dict]:
    """获取共享库信息"""
    url = f"{STEAM_API_URL}/IFamilyGroupsService/GetSharedLibraryApps/v1/"
    params = {
        "key": api_key,
        "family_groupid": family_group_id,
        "include_own": 0,  # 不包括自己的游戏
        "include_excluded": 0  # 不包括被排除的游戏
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "response" in data and "apps" in data["response"]:
            return data["response"]["apps"]
        else:
            print("无法获取共享库游戏列表")
            return []
    except requests.exceptions.RequestException as e:
        print(f"获取共享库游戏时出错: {e}")
        return []

def get_owned_games(steam_id: str, api_key: str) -> List[Dict]:
    """获取用户拥有的游戏列表"""
    url = f"{STEAM_API_URL}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "response" in data and "games" in data["response"]:
            return data["response"]["games"]
        else:
            print("无法获取拥有的游戏列表")
            return []
    except requests.exceptions.RequestException as e:
        print(f"获取拥有的游戏时出错: {e}")
        return []

def get_player_achievements(steam_id: str, app_id: str, api_key: str) -> Dict:
    """获取玩家在特定游戏中的成就"""
    url = f"{STEAM_API_URL}/ISteamUserStats/GetPlayerAchievements/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "appid": app_id,
        "l": "english"  # 英文成就名称
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "playerstats" in data and "achievements" in data["playerstats"]:
            return data["playerstats"]
        else:
            return {"success": False, "error": "No achievements data"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def get_app_details(app_id: str) -> Dict:
    """获取游戏详细信息"""
    url = f"https://store.steampowered.com/api/appdetails"
    params = {
        "appids": app_id,
        "l": "english"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if app_id in data and data[app_id]["success"]:
            return data[app_id]["data"]
        else:
            return {}
    except requests.exceptions.RequestException as e:
        return {}

def main():
    # 获取家庭组ID
    family_group_id = get_family_group_id(STEAM_ID, STEAM_API_KEY)
    if not family_group_id:
        print("无法获取家庭组ID，程序退出")
        return
    
    print(f"找到家庭组ID: {family_group_id}")
    
    # 获取共享库游戏
    shared_library = get_shared_library_info(family_group_id, STEAM_API_KEY)
    if not shared_library:
        print("共享库中没有游戏，程序退出")
        return
    
    print(f"找到 {len(shared_library)} 款共享库游戏")
    
    # 获取自己拥有的游戏列表（用于过滤）
    owned_games = get_owned_games(STEAM_ID, STEAM_API_KEY)
    owned_app_ids = {str(game["appid"]) for game in owned_games} if owned_games else set()
    
    # 准备收集数据
    games_data = []
    
    # 处理每个共享库游戏
    for game in shared_library:
        app_id = str(game["appid"])
        owner_steam_id = str(game["owner_steamid"])
        
        # 跳过自己拥有的游戏
        if app_id in owned_app_ids:
            continue
        
        # 获取游戏详情
        app_details = get_app_details(app_id)
        game_name = app_details.get("name", f"未知游戏 (AppID: {app_id})") if app_details else f"未知游戏 (AppID: {app_id})"
        
        # 获取游戏时长（从共享库信息中）
        playtime = game.get("playtime", 0)  # 分钟
        
        # 获取成就信息
        achievements_data = get_player_achievements(STEAM_ID, app_id, STEAM_API_KEY)
        achievements = []
        total_achievements = 0
        achieved = 0
        
        if achievements_data.get("success", False):
            achievements_list = achievements_data.get("achievements", [])
            total_achievements = len(achievements_list)
            achieved = sum(1 for a in achievements_list if a.get("achieved", 0) == 1)
        
        # 添加到数据列表
        games_data.append({
            "app_id": app_id,
            "game_name": game_name,
            "owner_steamid": owner_steam_id,
            "playtime_minutes": playtime,
            "playtime_hours": round(playtime / 60, 1),
            "total_achievements": total_achievements,
            "achieved_achievements": achieved,
            "achievement_percentage": round((achieved / total_achievements * 100), 1) if total_achievements > 0 else 0
        })
        
        # 避免请求过于频繁
        time.sleep(1)
    
    # 保存到CSV文件
    if games_data:
        csv_file = "steam_family_library_games.csv"
        fieldnames = [
            "app_id", "game_name", "owner_steamid", 
            "playtime_minutes", "playtime_hours",
            "total_achievements", "achieved_achievements", "achievement_percentage"
        ]
        
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(games_data)
        
        print(f"成功保存 {len(games_data)} 款游戏信息到 {csv_file}")
    else:
        print("没有找到可用的共享库游戏数据")

if __name__ == "__main__":
    main()
