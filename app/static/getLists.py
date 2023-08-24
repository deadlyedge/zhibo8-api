import json
import time
import pymongo
import toml
import random
from threading import Timer, Thread
from queue import Queue

from pymongo.errors import DuplicateKeyError

from static import xlogger
from pyquery import PyQuery as pq

config = toml.load('../config.toml')
logger = xlogger.get_my_logger(__name__)
GRAB_TIMER_BASE = config['app']['GRAB_TIMER_BASE']

dbClient = pymongo.MongoClient(
    'mongodb://%s:%s@%s/' %
    (config['database']['user'], config['database']['password'],
     config['database']['address']))
myDB = dbClient[config['database']['name']]

header = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}
url = 'https://www.zhibo8.cc/'


def writeDB(gameList: list, teamList: set):
    logger.debug(len(gameList))
    if gameList and len(gameList) > 150:
        myDB.drop_collection('gameList')
        myDB.drop_collection('dataUpdate')
        myDB.drop_collection('teamList')
    else:
        return
    myDB.dataUpdate.create_index([('uniqueCheck', pymongo.DESCENDING)],
                                 unique=True)
    now = time.time()
    try:
        myDB.dataUpdate.insert_one({
            'uniqueCheck':
            'set',
            'timestamp':
            now,
            'updateTime':
            time.strftime("%Y-%m-%d %H:%M", time.localtime(now))
        })
    except DuplicateKeyError:
        logger.info('duplicate, no need to write.')
        return
    myDB.teamList.insert_one({'teamList': list(teamList)})
    result = myDB.gameList.insert_many(gameList)
    logger.warning('inserted %d games' % (len(result.inserted_ids), ))


def getPage():
    for retry in range(5):
        try:
            rqs = pq(url=url, headers=header, encoding='utf-8')
        except Exception as e:
            logger.warning('通过失败，重新尝试... %s' % e)
            time.sleep(5)
            continue
        return rqs
    logger.error('检查是否可以打开%s' % url)
    input('输入回车结束程序...')
    return []


def getPageBS():
    for retry in range(5):
        try:
            rqs = pq(url=url, headers=header, encoding='utf-8')
        except Exception as e:
            logger.warning('通过失败，重新尝试... %s' % e)
            time.sleep(5)
            continue
        return rqs
    logger.error('检查是否可以打开%s' % url)
    input('输入回车结束程序...')
    return []


def grabGameList():
    gameList = []
    teamList = set()
    logger.debug(url)
    try:
        page = getPage()
        allGame = page('div.schedule li').items()
    except Exception as e:
        logger.critical(e)
        allGame = None
    for game in allGame:
        gameLabel = game('li')
        teamInfo = game('b')
        if gameLabel.attr('label') and len(teamInfo.text().split()) > 1:
            teamList = set(gameLabel.attr('label').split(',')) | teamList
            try:
                gameInfo = {
                    'ID': gameLabel.attr('id'),
                    'Labels': gameLabel.attr('label').split(','),
                    'Time': gameLabel.attr('data-time').split(),
                    # 'Show Time': showTime(gameLabel.attr('data-time').split()),
                    'Team1': teamInfo.text().split()[1],
                    # 'Team1 Logo': 'https:' + teamInfo('img:first').attr('src'),
                    'Team2': teamInfo.text().split()[-1],
                    # 'Team2 Logo': 'https:' + teamInfo('img:last').attr('src'),
                    'Broadcast': game('a:first').text().split()
                }
            except AttributeError:
                return
            gameList.append(gameInfo)
    with open('gameList.json', 'w', encoding='utf-8') as jsonSave:
        json.dump(gameList, jsonSave, ensure_ascii=False, indent=4)
    writeDB(gameList, teamList)
    return


def getGameList() -> list:
    # now = time.time()
    # lastUpdate = myDB.dataUpdate.find_one()  # {'timestamp': {'$gt': 1.0}}
    # if not lastUpdate or now - lastUpdate['timestamp'] > GRAB_INTERVAL:
    #     grabGameList()
    # else:
    #     logger.info('No need to grab...')
    result = list(
        myDB.gameList.aggregate([{
            '$sort': {
                'Time.0': 1,
                'Time.1': 1
            }
        }]))
    for d in result:
        del d['_id']
    # logger.warning(teams)
    return result


def getTeamList() -> list:
    teams = myDB.teamList.find_one()
    if teams['teamList']:
        return teams['teamList']
    else:
        return []


def testTimer():
    pass


def initDB():
    grabGameList()
    logger.debug('timer ' +
                 time.strftime("%H:%M:%S", time.localtime(time.time())))
    seed = random.randint(0, 1800)
    Timer(GRAB_TIMER_BASE + seed, initDB).start()


if __name__ == '__main__':
    # getGameList()
    grabGameList()
