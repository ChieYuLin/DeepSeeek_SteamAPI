import requests

API_KEY = "你的真实API密钥"
STEAM_ID = "你的SteamID64"

url = "https://api.steampowered.com/IFamilyGroupsService/GetFamilyGroupForUser/v1/"
params = {
    "key": API_KEY,
    "steamid": STEAM_ID
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    print("完整响应:", data)
    
    if "response" in data and "family_groupid" in data["response"]:
        print("家庭组ID:", data["response"]["family_groupid"])
    else:
        print("未找到家庭组ID，响应内容:", data)
except Exception as e:
    print("错误:", e)
    if hasattr(e, 'response'):
        print("错误详情:", e.response.text)
