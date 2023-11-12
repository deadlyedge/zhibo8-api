import datetime
import time
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_TEAMS_STRING = "勇士,阿森纳,F1,皇家马德里"
ZHIBO8_URL = "https://www.zhibo8.com/"
HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


class GameInfo:
    """get and organize game info"""

    def __init__(self) -> None:
        self.default_teams = DEFAULT_TEAMS_STRING
        self.url = ZHIBO8_URL
        self.headers = HEADER
        self.game_list = []
        self.team_list = set()
        self.fav_games = []

    def get_cache(self):
        """try load cache from gameList.json
        if cache expired, get info from zhibo8.com
        and save to gameList.json
        """
        try:
            with open("gameList.json", "r", encoding="utf-8") as j_load:
                data_set = json.load(j_load)
        except FileNotFoundError:
            data_set = None

        if data_set and time.time() - data_set["timestamp"] < 60 * 60 * 2:
            self.game_list = data_set["game_list"]
            self.team_list = set(data_set["team_list"])
            print("cache loaded")
        else:
            print("cache expired")
            self.game_list = []
            self.team_list = set()

            self.get_info()

    def save_cache(self):
        """save cache to gameList.json"""
        data_set = {
            "timestamp": time.time(),
            "game_list": self.game_list,
            "team_list": list(self.team_list),
        }
        with open("gameList.json", "w", encoding="utf-8") as j_save:
            json.dump(data_set, j_save, ensure_ascii=False, indent=4)
        print(
            f"cache saved, {len(self.game_list)} games and {len(self.team_list)} teams."
        )

    def get_html(self):
        """获取网页信息"""
        response = requests.get(self.url, headers=self.headers, timeout=5)
        html = response.content.decode("utf-8")
        return html

    def get_info(self):
        """grab info from zhibo8.com"""
        html = self.get_html()
        soup = BeautifulSoup(html, "lxml")
        games = soup.find("div", class_="schedule")
        for game in games.find_all("li"):  # type: ignore
            game_info = {}
            game_info["ID"] = game.attrs["id"]
            game_info["Labels"] = game.attrs["label"].split(",")
            game_info["Time"] = game.attrs["data-time"].split()
            others = game.find("b").get_text(" ", strip=True)
            game_info["Broadcast"] = game.find("a").get_text(" ", strip=True).split()
            try:
                game_info["Team1"] = others.split()[1]
                game_info["Team2"] = others.split()[-1]
            except IndexError:
                continue
            self.game_list.append(game_info)
            self.team_list = set(game_info["Labels"]) | self.team_list

        self.save_cache()

    def show_time(self, time_in_list: list) -> list:
        """convert time to text"""
        now = datetime.datetime.now().strftime("%H:%M")
        today = datetime.date.today() - datetime.timedelta(
            days=1 if "00:00" < now < "05:00" else 0
        )
        tomorrow = today + datetime.timedelta(days=1)
        the_day_after_tomorrow = today + datetime.timedelta(days=2)
        list_day = time_in_list[0]
        list_time = time_in_list[1]
        night = "00:00" <= list_time <= "05:00"

        # 判断时间是否需要替换为汉字 如果是明天凌晨转换为‘今夜’，同理后天凌晨转换为‘明晚’
        if list_day == str(tomorrow) and night:
            return ["今夜", list_time]
        if list_day == str(today):
            return ["今天", list_time]
        if list_day == str(tomorrow):
            return ["明天", list_time]
        if list_day == str(the_day_after_tomorrow) and night:
            return ["明晚", list_time]
        return [list_day[5:10], list_time]  # 切掉年份

    def filter_game(self, teams: list):
        """favor game filter"""
        self.fav_games = []
        for game in self.game_list:
            for team in teams:
                if team in game["Labels"]:
                    game["showTime"] = self.show_time(game["Time"])
                    self.fav_games.append(game)
                    break


app = FastAPI()
origins = [
    "*",
    # "http://localhost",
    # "http://localhost:8000",
    # "http://localhost:3000",
    # "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games_info = GameInfo()


@app.get("/")
async def get_game_list(teams: str = ""):
    """entrance of get game list"""
    if not teams:
        teams = DEFAULT_TEAMS_STRING
    show_teams = teams.split(",")
    games_info.get_cache()
    games_info.filter_game(show_teams)
    return games_info.fav_games


@app.get("/teamList/")
async def get_team_list():
    """entrance of team_list"""
    games_info.get_cache()
    return games_info.team_list


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
