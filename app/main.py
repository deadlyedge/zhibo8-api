import datetime
from threading import Thread
import toml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from static import xlogger, getLists

config = toml.load("config.toml")
logger = xlogger.get_my_logger(__name__)

DEFAULT_TEAMS_STRING = config["app"]["DEFAULT_TEAMS_STRING"]
# getLists.initDB()

# logger.debug(gameList)
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


def getDB():
    getLists.initDB()


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
    gameList = getLists.getGameList()
    for game in gameList:
        for team in teams:
            if team in game["Labels"]:
                game["showTime"] = showTime(game["Time"])
                result.append(game)
                # logger.info(game)
                break
    return result


Thread(target=getDB).start()


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
    teamList = getLists.getTeamList()
    return teamList


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
