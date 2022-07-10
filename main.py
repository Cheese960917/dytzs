# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import time
import datetime

import requests
import csv

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
player_name = '小刘666'  # 玩家ID，注意这里的ID需要和网站上面的ID相同
code_cup = 'dy220701'  # 第一届天之上杯: dy220509，第二届 dy220701
size = 500  # 获取多少条比赛记录
item_map = {}  # 对照表
all_records = []  # 从网站获取到的所有记录，存在这里


# 这个类用来存储"一位选手"在"一局比赛记录"当中的表现
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
        time = ''  # 时间
        alies = []  # 队友
        enemies = []  # 对手


# 查询接口并构建数据
def req_data():
    print('Start to request data...')
    # change 'size' param to change the size of the records
    params = {
        'pageCode': 'omg42',
        'scCode': code_cup,
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
        player_rec.time = rec_time
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


# 所有英雄的数据和胜率
def all_heroes_statistic():
    hero_map = {}
    for record in all_records:
        hero = record.hero
        win = record.result == '胜利'
        if hero not in hero_map:
            hero_map[hero] = []
        if win:
            hero_map[hero].append(1)
        else:
            hero_map[hero].append(0)
    hero_value = []
    for hero in hero_map:
        values = hero_map[hero]
        win = 0
        lose = 0
        sum = 0
        for i in values:
            sum += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum / len(values)
        hero_value.append([hero, win, lose, round(avg, 2)])
    header = ['英雄', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_hero' + '.csv'
    write_into_file(file_name, header, hero_value)


# 所有队友胜率
def all_alies_statistic():
    allies_map = {}
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
    hero_value = []
    for ally in allies_map:
        values = allies_map[ally]
        win = 0
        lose = 0
        sum_of_ally = 0
        for i in values:
            sum_of_ally += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum_of_ally / len(values)
        hero_value.append([ally, win, lose, round(avg, 2)])
    header = ['队友', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_ally' + '.csv'
    write_into_file(file_name, header, hero_value)


# 所有对手胜率
def all_enemy_statistic():
    enemy_map = {}
    for record in all_records:
        for enemy in record.enemies:
            player = enemy.playr
            win = record.result == '胜利'
            if player not in enemy_map:
                enemy_map[player] = []
            if win:
                enemy_map[player].append(1)
            else:
                enemy_map[player].append(0)
    enemy_value = []
    for enemy in enemy_map:
        values = enemy_map[enemy]
        win = 0
        lose = 0
        sum_of_enemy = 0
        for i in values:
            sum_of_enemy += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum_of_enemy / len(values)
        enemy_value.append([enemy, win, lose, round(avg, 2)])
    header = ['对手', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_enemy' + '.csv'
    write_into_file(file_name, header, enemy_value)


# 计算所有大招的使用次数和胜率数据
def all_ult_statistics():
    ult_map = {}
    for record in all_records:
        ult = record.ult
        win = record.result == '胜利'
        if ult not in ult_map:
            ult_map[ult] = []
        if win:
            ult_map[ult].append(1)
        else:
            ult_map[ult].append(0)
    ult_value = []
    for ult in ult_map:
        values = ult_map[ult]
        win = 0
        lose = 0
        sum_of_ult = 0
        for i in values:
            sum_of_ult += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum_of_ult / len(values)
        ult_value.append([ult, win, lose, round(avg, 2)])
    header = ['大招', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_ult' + '.csv'
    write_into_file(file_name, header, ult_value)


# 计算所有小技能的使用次数和胜率数据
def all_skill_statistics():
    skill_map = {}
    for record in all_records:
        skill = record.skill
        win = record.result == '胜利'
        if skill not in skill_map:
            skill_map[skill] = []
        if win:
            skill_map[skill].append(1)
        else:
            skill_map[skill].append(0)
    skill_value = []
    for skill in skill_map:
        values = skill_map[skill]
        win = 0
        lose = 0
        sum_of_skill = 0
        for i in values:
            sum_of_skill += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum_of_skill / len(values)
        skill_value.append([skill, win, lose, round(avg, 2)])
    header = ['技能', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_skill' + '.csv'
    write_into_file(file_name, header, skill_value)


# 所有称号数据
def all_titles_statistic():
    title_map = {}
    for record in all_records:
        title_list = record.title_list
        if title_list is None or len(title_list) == 0:
            title_list = ['白板']
        for title in title_list:
            win = record.result == '胜利'
            if title not in title_map:
                title_map[title] = []
            if win:
                title_map[title].append(1)
            else:
                title_map[title].append(0)
    title_value = []
    for title in title_map:
        values = title_map[title]
        win = 0
        lose = 0
        sum_of_title = 0
        for i in values:
            sum_of_title += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum_of_title / len(values)
        title_value.append([title, win, lose, round(avg, 2)])
    header = ['称号', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_title' + '.csv'
    write_into_file(file_name, header, title_value)


# 僵后选人胜率
def pick_player_statistic():
    def sort_by_time(record):
        return time.mktime(datetime.datetime.strptime(
            record.time, "%Y-%m-%d %H:%M:%S").timetuple())

    new_list = all_records.copy()  # 由于要排序，copy一下
    new_list.sort(key=sort_by_time) # 按时间排序
    win = 0
    lose = 0
    flag = 0  # 本局拿到僵的标志
    jdate = None  # 拿到僵的日期
    pick_record_list = []  # 僵选人的场合
    for record in new_list:
        title_list = record.title_list
        if flag == 1:
            # 这里代表上一把拿到了僵
            flag = 0
            if jdate != datetime.datetime.strptime(record.time, "%Y-%m-%d %H:%M:%S").date():
                # 如果僵过后那一局没有发生在同一天
                jdate = None
                continue
            else:
                # 僵选人的那一局
                jdate = None
                pick_record_list.append(record)
                if record.result == '胜利':
                    win += 1
                else:
                    lose += 1
        if title_list is None or len(title_list) == 0:
            continue
        for title in title_list:
            # 这里判断这一把有没有拿到僵
            if title == '僵':
                flag = 1
                jdate = datetime.datetime.strptime(record.time, "%Y-%m-%d %H:%M:%S").date()
    total = win + lose
    rate = win / total
    print(f'{player_name} 在拿到僵后一共选了 {total} 次人, 其中胜利 {win} 次， 失败 {lose} 次，选人胜率为 {round(rate, 2)}')
    print('注意存在以下情况：')
    print('1、选手拿到僵时在当天最后一局，之后不打了')
    print('2、选手拿到僵后去吃饭了，跳过了后面几局')
    print('这些情况难以统计，所以概率可能出现误差，敬请谅解。')
    picked_alies_statistic(pick_record_list)


# 僵选人的队友胜率
def picked_alies_statistic(picked_list):
    allies_map = {}
    for record in picked_list:
        for ally in record.alies:
            player = ally.playr
            win = record.result == '胜利'
            if player not in allies_map:
                allies_map[player] = []
            if win:
                allies_map[player].append(1)
            else:
                allies_map[player].append(0)
    hero_value = []
    for ally in allies_map:
        values = allies_map[ally]
        win = 0
        lose = 0
        sum_of_ally = 0
        for i in values:
            sum_of_ally += i
            if i == 1:
                win += 1
            else:
                lose += 1
        avg = sum_of_ally / len(values)
        hero_value.append([ally, win, lose, round(avg, 2)])
    header = ['选人', '胜场', '负场', '胜率']
    file_name = datetime.date.today().__str__() + '_' + player_name + '_picked_ally' + '.csv'
    write_into_file(file_name, header, hero_value)

# 把内容写入文件
# file_name: 文件名
# header: 第一行
# content_list: 具体内容
def write_into_file(file_name, header, content_list):
    with open(file_name, 'w', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for content in content_list:
            writer.writerow(content)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    req_data()
    # todo: 所有英雄胜率，所有技能胜率，队友对手胜率，僵后选人胜率
    all_heroes_statistic()
    all_alies_statistic()
    all_enemy_statistic()
    all_ult_statistics()
    all_skill_statistics()
    all_titles_statistic()
    pick_player_statistic()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
