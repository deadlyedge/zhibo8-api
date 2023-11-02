"""manage time shift functions"""
import datetime

import json
import time
from pyquery import PyQuery as pq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_TEAMS_STRING = "勇士,阿森纳,F1,皇家马德里"
ZHIBO8_URL = "https://www.zhibo8.com/"
HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

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


def get_page():
    """connect to zhibo8 site"""
    for _ in range(5):
        try:
            rqs = pq(url=ZHIBO8_URL, headers=HEADER, encoding="utf-8")
            print("通过成功")
        except Exception as e:
            print(f"通过失败，重新尝试...{e}")
            time.sleep(5)
            continue
        return rqs
    print(f"检查是否可以打开{ZHIBO8_URL}")
    input("输入回车结束程序...")
    return []


def grab_game_list() -> dict:
    """grab infos."""

    try:
        with open("gameList.json", "r", encoding="utf-8") as j_load:
            data_set = json.load(j_load)
    except FileNotFoundError:
        data_set = None

    if data_set and time.time() - data_set["timestamp"] < 60 * 60 * 2:
        return {"game_list": data_set["game_list"], "team_list": data_set["team_list"]}

    game_list = []
    team_list = set()

    try:
        page = get_page()
        all_game = page("div.schedule li").items()
    except Exception as e:
        print("error:", e)
        all_game = None

    for game in all_game:
        game_label = game("li")
        team_info = game("b")
        if game_label.attr("label") and len(team_info.text().split()) > 1:
            team_list = set(game_label.attr("label").split(",")) | team_list
            try:
                game_info = {
                    "ID": game_label.attr("id"),
                    "Labels": game_label.attr("label").split(","),
                    "Time": game_label.attr("data-time").split(),
                    "Team1": team_info.text().split()[1],
                    "Team2": team_info.text().split()[-1],
                    "Broadcast": game("a:first").text().split(),
                }
            except AttributeError:
                return {"game_list": None, "team_list": None}
            game_list.append(game_info)

    data_set = {
        "timestamp": time.time(),
        "game_list": game_list,
        "team_list": list(team_list),
    }

    with open("gameList.json", "w", encoding="utf-8") as j_save:
        json.dump(data_set, j_save, ensure_ascii=False, indent=4)
    return {"game_list": game_list, "team_list": team_list}


def show_time(time_in_list: list) -> list:
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


def fav_game(teams: list) -> list:
    """favor game filter"""
    result = []
    game_list = grab_game_list()["game_list"]
    for game in game_list:
        for team in teams:
            if team in game["Labels"]:
                game["showTime"] = show_time(game["Time"])
                result.append(game)
                break
    return result


@app.get("/")
async def get_game_list(teams: str = ""):
    """entrance of get game list"""
    if not teams:
        teams = DEFAULT_TEAMS_STRING
    show_teams = teams.split(",")
    return fav_game(show_teams)


@app.get("/teamList/")
async def get_team_list():
    """entrance of team_list"""
    return grab_game_list()["team_list"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
