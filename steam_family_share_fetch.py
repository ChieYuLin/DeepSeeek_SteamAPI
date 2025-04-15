import requests
!pip install beautifulsoup4
from bs4 import BeautifulSoup  #核心是用Beautiful Soup这个包
import pandas as pd

'''
替换为你的 Steam 页面地址（确保你的游戏库设置为公开）
'''

STEAM_PROFILE_URL = "https://steamcommunity.com/profiles/76561198426747673/games/?tab=all"

headers = {
    'User-Agent': 'Mozilla/5.0'
}

def fetch_game_data(url):
    print("正在获取游戏数据，请稍等...")
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("获取页面失败，可能是隐私设置未公开或 Steam ID 错误。")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    games = []

    for game_div in soup.find_all('div', class_='gameListRow'):
        name_tag = game_div.find('div', class_='gameListRowItemName')
        hours_tag = game_div.find('h5')

        if not name_tag or not hours_tag:
            continue

        game_name = name_tag.text.strip()
        time_text = hours_tag.text.strip()

        try:
            hours_played = float(time_text.split(" ")[0].replace(",", "")) ## 提取小时数（注意有些是分钟、小时格式）
        except:
            hours_played = 0.0

        games.append({
            "游戏名称": game_name,
            "总游玩时间(小时)": hours_played
        })

    return games

def export_shared_games(games, filename="shared_games.csv"):
    if not games:
        print("没有获取到数据，看看你是不是没有家庭共享的游戏权限了")
        return
    df = pd.DataFrame(games)
    df = df.sort_values(by="总游玩时间(小时)", ascending=False)
    df.to_csv(filename, index=False, encoding='utf_8_sig')
    print(f"共享游戏数据已保存为 {filename}")

if __name__ == "__main__":
    games = fetch_game_data(STEAM_PROFILE_URL)
    export_shared_games(games)
