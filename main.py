# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import requests

# mapping:
'''
"detail": {
            "10280": 10975, // 哪一边胜利了，这个可以去底下的 filterlist 找，不过没搞懂下面的dependentId是做什么的
            "10281": 27, // 双方比分
            "10284": 73,
            "10288": [ // 这里是十位选手
              {
                "10291": 11858, // 大招选择
                "10292": 3,		// 死亡
                "10293": 11744, // 小技能选择
                "10295": 10053, // 英雄选择
                "10297": [		// 称号列表
                  11970,
                  11967,
                  11969,
                  11990
                ],
                "10313": 10004, // 胜败
                "10326": 21,	// 击杀
                "10332": 20,	// 助攻
                "10337": 10031, // 选手
                "10345": 10012	// 阵营
              }
          }
'''

# data source from daoshuju.com (unauthorized)
req_url = 'https://daoshuju.com/api/project/record'
player_name = '小刘666'
size = 500
item_map = {}
all_records = []


class PlayerRecord:
    def __init__(self):
        ult = ''  # 大招选择
        death = ''  # 死亡数
        skill = ''  # 小技能选择
        hero = ''  # 英雄选择
        title_list = None  # 称号列表
        result = ''  # 胜负结果
        kill = ''  # 击杀数
        support = ''  # 助攻数
        playr = ''  # 选手名字
        comm = ''  # 阵营
        alies = []  # 队友
        enemies = []  # 对手


# 查询接口并构建数据
def req_data():
    print('Start to request data...')
    # change 'size' param to change the size of the records
    params = {
        'pageCode': 'omg42',
        'scCode': 'dy220509',
        'requestType': 0,
        'projectId': None,
        'scCodeId': None,
        'filterMap': {},
        'current': 1,
        'size': size,
        'start': '',
        'end': ''
    }
    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0'
    }
    resp = requests.post(req_url, json=params, headers=headers)
    resp_json = resp.json()
    # print(resp_json)
    full_data = resp_json['data']
    records = full_data['data']['records']
    items = full_data['items']
    item_mapping(items)
    for rec in records:
        rec_time = rec['recordTime']
        rec_detail = rec['detail']
        total_result = rec_detail['10280']
        radient_score = rec_detail['10281']
        dire_score = rec_detail['10284']
        player_list = rec_detail['10288']
        player_rec = PlayerRecord()
        player_rec.playr = 'unknown'
        other_player = []
        for player in player_list:
            playr = get_item_name(player['10337'])  # 选手名字
            if playr == player_name:
                # 如果当前选手匹配上了我们要的选手
                player_rec.playr = playr  # 选手名字
                player_rec.ult = get_item_name(player['10291'])  # 大招选择
                player_rec.death = player['10292']  # 死亡数
                player_rec.skill = get_item_name(player['10293'])  # 小技能选择
                player_rec.hero = get_item_name(player['10295'])  # 英雄选择
                player_rec.title_list = get_title_list(player['10297'])  # 称号列表
                player_rec.result = get_item_name(player['10313'])  # 胜负结果
                player_rec.kill = player['10326']  # 击杀数
                player_rec.support = player['10332']  # 助攻数
                player_rec.comm = get_item_name(player['10345'])  # 阵营
                player_rec.alies = []
                player_rec.enemies = []
                # print(player_rec.skill + ' ' + player_rec.ult)
            else:
                # 设定进队友和对手当中
                player_other = PlayerRecord()
                player_other.playr = playr  # 选手名字
                player_other.ult = get_item_name(player['10291'])  # 大招选择
                player_other.death = player['10292']  # 死亡数
                player_other.skill = get_item_name(player['10293'])  # 小技能选择
                player_other.hero = get_item_name(player['10295'])  # 英雄选择
                player_other.title_list = get_title_list(player['10297'])  # 称号列表
                player_other.result = get_item_name(player['10313'])  # 胜负结果
                player_other.kill = player['10326']  # 击杀数
                player_other.support = player['10332']  # 助攻数
                player_other.comm = get_item_name(player['10345'])  # 阵营
                other_player.append(player_other)
        if player_rec.playr == 'unknown':
            # 这里排除特殊情况：本场比赛我们要的选手没参加
            continue
        for other in other_player:
            # 再循环一次
            # 把其他选手归纳为队友对手
            if other.comm == player_rec.comm:
                player_rec.alies.append(other)
            else:
                player_rec.enemies.append(other)
        all_records.append(player_rec)


# 获取本局所有称号
def get_title_list(list):
    title_list = []
    for l in list:
        title_list.append(get_item_name(l))
    return title_list


# 构建id和名称的对照表
def item_mapping(item):
    for i in item:
        item_map[i['id']] = i['dependDataName']
    # print(item_map)


# 从对照表里找到id对应的名称
def get_item_name(item_code):
    return item_map[item_code]


def all_heroes_statistic():
    hero_map = {}
    hero_value = {}
    for record in all_records:
        hero = record.hero
        win = record.result == '胜利'
        if hero not in hero_map:
            hero_map[hero] = []
        if win:
            hero_map[hero].append(1)
        else:
            hero_map[hero].append(0)
    for hero in hero_map:
        values = hero_map[hero]
        sum = 0
        for i in values:
            sum += i
        avg = sum / len(values)
        hero_value[hero] = avg
    print(player_name + '选择这些英雄时的胜率为：')
    print(hero_value)


# 所有队友胜率
def all_alies_statistic():
    allies_map = {}
    allies_value = {}
    for record in all_records:
        for ally in record.alies:
            player = ally.playr
            win = record.result == '胜利'
            if player not in allies_map:
                allies_map[player] = []
            if win:
                allies_map[player].append(1)
            else:
                allies_map[player].append(0)
    for ally in allies_map:
        values = allies_map[ally]
        sum = 0
        for i in values:
            sum += i
        avg = sum / len(values)
        allies_value[ally] = avg
    print(player_name + '和这些选手搭档时的胜率为：')
    print(allies_value)


# 所有对手胜率
def all_enemy_statistic():
    allies_map = {}  # 偷个懒，不改了
    allies_value = {}
    for record in all_records:
        for ally in record.enemies:
            player = ally.playr
            win = record.result == '胜利'
            if player not in allies_map:
                allies_map[player] = []
            if win:
                allies_map[player].append(1)
            else:
                allies_map[player].append(0)
    for ally in allies_map:
        values = allies_map[ally]
        sum = 0
        for i in values:
            sum += i
        avg = sum / len(values)
        allies_value[ally] = avg
    print(player_name + '在这些选手对面时的胜率为：')
    print(allies_value)


def all_ult_statistics():
    hero_map = {}  # 偷个懒，不改名字了
    hero_value = {}
    for record in all_records:
        hero = record.ult
        win = record.result == '胜利'
        if hero not in hero_map:
            hero_map[hero] = []
        if win:
            hero_map[hero].append(1)
        else:
            hero_map[hero].append(0)
    for hero in hero_map:
        values = hero_map[hero]
        sum = 0
        for i in values:
            sum += i
        avg = sum / len(values)
        hero_value[hero] = avg
    print(player_name + '选择这些大招时的胜率为：')
    print(hero_value)


def all_skill_statistics():
    hero_map = {}  # 偷个懒，不改名字了
    hero_value = {}
    for record in all_records:
        hero = record.skill
        win = record.result == '胜利'
        if hero not in hero_map:
            hero_map[hero] = []
        if win:
            hero_map[hero].append(1)
        else:
            hero_map[hero].append(0)
    for hero in hero_map:
        values = hero_map[hero]
        sum = 0
        for i in values:
            sum += i
        avg = sum / len(values)
        hero_value[hero] = avg
    print(player_name + '选择这些小技能时的胜率为：')
    print(hero_value)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    req_data()
    # print(all_records)
    # todo: 所有英雄胜率，所有技能胜率，队友对手胜率，僵后选人胜率
    print('')
    all_heroes_statistic()
    print('')
    all_alies_statistic()
    print('')
    all_enemy_statistic()
    print('')
    all_ult_statistics()
    print('')
    all_skill_statistics()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
