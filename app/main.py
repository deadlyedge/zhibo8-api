import datetime
import json
import time
from pyquery import PyQuery as pq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_TEAMS_STRING = "勇士,北京,北控,掘金,热刺,埃弗顿,F1,皇家马德里"
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


def getPage():
    for retry in range(5):
        try:
            rqs = pq(url=ZHIBO8_URL, headers=HEADER, encoding="utf-8")
            print("通过成功")
        except Exception as e:
            print("通过失败，重新尝试... %s" % e)
            time.sleep(5)
            continue
        return rqs
    print("检查是否可以打开%s" % ZHIBO8_URL)
    input("输入回车结束程序...")
    return []


def grabGameList() -> dict:
    gameList = []
    teamList = set()
    try:
        page = getPage()
        allGame = page("div.schedule li").items()
    except Exception as e:
        print("error:", e)
        allGame = None
    for game in allGame:
        gameLabel = game("li")
        teamInfo = game("b")
        if gameLabel.attr("label") and len(teamInfo.text().split()) > 1:
            teamList = set(gameLabel.attr("label").split(",")) | teamList
            try:
                gameInfo = {
                    "ID": gameLabel.attr("id"),
                    "Labels": gameLabel.attr("label").split(","),
                    "Time": gameLabel.attr("data-time").split(),
                    "Team1": teamInfo.text().split()[1],
                    "Team2": teamInfo.text().split()[-1],
                    "Broadcast": game("a:first").text().split(),
                }
            except AttributeError:
                return {"gameList": None, "teamList": None}
            gameList.append(gameInfo)
    with open("app/gameList.json", "w", encoding="utf-8") as jsonSave:
        json.dump(gameList, jsonSave, ensure_ascii=False, indent=4)
    return {"gameList": gameList, "teamList": teamList}


def showTime(timeInList: list) -> list:
    now = datetime.datetime.now().strftime("%H:%M")
    today = datetime.date.today() - datetime.timedelta(
        days=1 if "00:00" < now < "05:00" else 0
    )
    tomorrow = today + datetime.timedelta(days=1)
    theDayAfterTomorrow = today + datetime.timedelta(days=2)
    listDay = timeInList[0]
    listTime = timeInList[1]
    night = True if "00:00" <= listTime <= "05:00" else False

    # 判断时间是否需要替换为汉字 如果是明天凌晨转换为‘今夜’，同理后天凌晨转换为‘明晚’
    if listDay == str(tomorrow) and night:
        return ["今夜", listTime]
    elif listDay == str(today):
        return ["今天", listTime]
    elif listDay == str(tomorrow):
        return ["明天", listTime]
    elif listDay == str(theDayAfterTomorrow) and night:
        return ["明晚", listTime]
    else:
        return [listDay[5:10], listTime]  # 切掉年份


def favGame(teams: list) -> list:
    result = []
    gameList = grabGameList()["gameList"]
    for game in gameList:
        for team in teams:
            if team in game["Labels"]:
                game["showTime"] = showTime(game["Time"])
                result.append(game)
                # logger.info(game)
                break
    return result


@app.get("/")
async def getGameList(teams: str = ""):
    if not teams:
        teams = DEFAULT_TEAMS_STRING
    showTeams = teams.split(",")
    showGame = favGame(showTeams)
    return showGame


@app.get("/teamList/")
async def showTeamList():
    # logger.info(teamList)
    teamList = grabGameList()['teamList']
    return teamList


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
