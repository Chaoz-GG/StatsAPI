import json

import mysql.connector

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


with open('config.json') as json_file:
    data = json.load(json_file)
    db_name = data['db_name']
    db_user = data['db_user']
    db_password = data['db_password']
    db_host = data['db_host']
    db_port = data['db_port']

mm_ranks = {
            0: 'Unranked',
            1: 'Silver 1',
            2: 'Silver 2',
            3: 'Silver 3',
            4: 'Silver 4',
            5: 'Silver Elite',
            6: 'Silver Elite Master',
            7: 'Gold Nova 1',
            8: 'Gold Nova 2',
            9: 'Gold Nova 3',
            10: 'Gold Nova Master',
            11: 'Master Guardian 1',
            12: 'Master Guardian 2',
            13: 'Master Guardian Elite',
            14: 'Distinguished Master Guardian',
            15: 'Legendary Eagle',
            16: 'Legendary Eagle Master',
            17: 'Supreme Master First Class',
            18: 'Global Elite'
        }


def non_empty_mm_stats_exist(steam_id: int):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    # noinspection SqlDialectInspection, SqlNoDataSourceInspection
    cursor.execute('select STEAM_ID from mm_stats;')

    for i in cursor:
        if steam_id in i:
            # noinspection SqlDialectInspection, SqlNoDataSourceInspection
            cursor.execute('select RANK from mm_stats where STEAM_ID = %s;', (steam_id,))

            res = cursor.fetchone()

            cursor.close()
            db.close()

            if res:
                return True

    return False


def non_empty_faceit_stats_exist(steam_id: int):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    # noinspection SqlDialectInspection, SqlNoDataSourceInspection
    cursor.execute('select STEAM_ID from faceit_stats;')

    for i in cursor:
        if steam_id in i:
            # noinspection SqlDialectInspection, SqlNoDataSourceInspection
            cursor.execute('select RANK from faceit_stats where STEAM_ID = %s;', (steam_id, ))

            res = cursor.fetchone()[0]

            cursor.close()
            db.close()

            if res:
                return True

    return False


def get_mm_stats(steam_id: int):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    # noinspection SqlDialectInspection, SqlNoDataSourceInspection
    cursor.execute(f'select * from mm_stats where STEAM_ID = %s;', (steam_id, ))

    res = cursor.fetchone()

    cursor.close()
    db.close()

    return res


def get_faceit_stats(steam_id: int):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    # noinspection SqlDialectInspection, SqlNoDataSourceInspection
    cursor.execute(f'select * from faceit_stats where STEAM_ID = %s;', (steam_id, ))

    res = cursor.fetchone()

    cursor.close()
    db.close()

    return res


def collect_mm_stats(steam_id: int):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = uc.Chrome(use_subprocess=True, options=options)

    driver.get(f'https://csgostats.gg/player/{steam_id}')

    try:
        kpd = WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="kpd"]/span'))).text

    except TimeoutException:
        return None

    try:
        rank = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/div/div[2]/div[1]/img'))
        ).get_attribute("src")

        rank = mm_ranks[int(rank.rsplit('/')[-1][:-4])]

    except TimeoutException:
        rank = mm_ranks[0]

    rating = WebDriverWait(driver, 5).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="rating"]/span'))).text
    clutch = WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="player-overview"]'
                                                                                        '/div[2]/div/div[1]/div[2]/'
                                                                                        'div[1]/span[2]'))).text

    best_weapon = WebDriverWait(driver, 5).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="player-overview"]'
                                                    '/div[3]/div/div[3]/div[1]/div/'
                                                    'div[2]/div[1]/div[1]/div/img'))
        ).get_attribute("alt")

    win_rate = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[2]/div[2]/div/div[1]'
                                                 '/div[1]/div[3]/div/div[2]/div[2]'))).text
    hs = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[2]/div[2]'
                                                           '/div/div[1]/div[1]/div[4]/div/div[2]/div[2]'))).text
    adr = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[2]/div[2]'
                                                           '/div/div[1]/div[1]/div[5]/div/div[2]/div[2]'))).text

    entry_success = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[2]/div[2]'
                                                           '/div/div[1]/div[2]/div/div[2]/div[2]/div[1]/span[2]'))).text

    win_rate = win_rate.split()[0]
    hs = hs.split()[0]
    adr = adr.split()[0]

    most_played_map = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[2]/div[2]'
                                                           '/div/div[1]/div[3]/div/div[2]/div[1]/div/div/div[2]/div[1]'
                                                           '/div[1]/div[1]/span'))).text
    most_successful_map = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[3]/div[2]/div[2]/div[2]'
                                                           '/div/div[1]/div[3]/div/div[2]/div[2]/div/div/div[2]/div[1]'
                                                           '/div[1]/div[1]/span'))).text

    kpd = float(kpd)
    rating = float(rating)
    adr = int(adr)

    return {
        "rank": rank,
        "kpd": kpd,
        "rating": rating,
        "clutch": clutch,
        "best_weapon": best_weapon,
        "win_rate": win_rate,
        "hs": hs,
        "adr": adr,
        "entry_success": entry_success,
        "most_played_map": most_played_map,
        "most_successful_map": most_successful_map
    }


def collect_faceit_stats(steam_id: int):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = uc.Chrome(use_subprocess=True, options=options)

    driver.get(f'https://faceitfinder.com/stats/{steam_id}')

    try:
        elo = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located(
                (By.XPATH, '/html/body/div[1]/main/div/div[2]/div/div[4]/div[3]/span'))).text

        elo = int(elo)

    except TimeoutException:
        return None

    try:
        rank = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div[1]/div/div/div[4]/img'))
        ).get_attribute("src")

    except TimeoutException:
        rank = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div[1]/div/div/div[3]/img'))
        ).get_attribute("src")

    rank = int(rank.rsplit('/')[-1][:-4].rsplit('_')[-2])

    kpd = WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/'
                                                                                     'div[2]/div/div[1]/div[3]/'
                                                                                     'span'))).text

    rating = WebDriverWait(driver, 5).until(
        ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div[2]/div/div[3]/div[3]/span'))).text

    win_rate = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/main/div/div[2]/div/div[2]/div[3]/span'))).text

    hs = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/main/div/div[2]/div/div[5]/div[3]/span'))).text

    matches = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/main/div/div[2]/div/div[6]/div[3]/span'))).text

    driver.get(f'https://faceitfinder.com/stats/{steam_id}/maps')

    most_played_map = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div[2]/table/tbody/'
                                                           'tr[1]/td[1]'))).text
    most_successful_map = WebDriverWait(driver, 5)\
        .until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/main/div/div[2]/table/tbody/'
                                                           'tr[1]/td[1]'))).text

    kpd = float(kpd)
    rating = float(rating)
    matches = int(matches)

    return {
        "rank": rank,
        "elo": elo,
        "kpd": kpd,
        "rating": rating,
        "win_rate": win_rate,
        "hs": hs,
        "matches": matches,
        "most_played_map": most_played_map,
        "most_successful_map": most_successful_map
    }


def get_inventory(steam_id: int):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = uc.Chrome(use_subprocess=True, options=options)

    driver.get(f'https://csgobackpack.net/index.php?nick={steam_id}&currency=USD')

    button = WebDriverWait(driver, 5).until(
        ec.element_to_be_clickable
        ((By.ID, 'get_inventory')))

    button.click()

    driver.implicitly_wait(5)

    try:
        item_count = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/p[1]'))).text

        value = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/h3[1]/p'))).text

    except TimeoutException:
        return None

    return {
        'item_count': int(item_count),
        'value': float(value[1:])
    }


def insert_mm_stats(steam_id: int, stats: dict = None):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    if stats:
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        cursor.execute(f'insert into mm_stats (STEAM_ID, RANK, KPD, RATING, CLUTCH, '
                       f'BEST_WEAPON, WIN_RATE, HS, ADR, ENTRY_SUCCESS, MOST_PLAYED_MAP, MOST_SUCCESSFUL_MAP) '
                       f'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                       (steam_id, stats["rank"], stats["kpd"],
                        stats["rating"], stats["clutch"], stats["best_weapon"], stats["win_rate"], stats["hs"],
                        stats["adr"], stats["entry_success"], stats["most_played_map"], stats["most_successful_map"]))

    else:
        try:
            # noinspection SqlDialectInspection,SqlNoDataSourceInspection
            cursor.execute('insert into mm_stats (STEAM_ID) values(%s)', (steam_id, ))

        except mysql.connector.errors.IntegrityError:
            pass

    db.commit()

    cursor.close()
    db.close()


def insert_faceit_stats(steam_id: int, stats: dict = None):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    if stats:
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        cursor.execute('insert into faceit_stats (STEAM_ID, RANK, ELO, KPD, RATING, '
                       'WIN_RATE, HS, MATCHES, MOST_PLAYED_MAP, MOST_SUCCESSFUL_MAP) '
                       'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                       (steam_id, stats["rank"], stats["elo"], stats["kpd"],
                        stats["rating"], stats["win_rate"], stats["hs"],
                        stats["matches"], stats["most_played_map"], stats["most_successful_map"]))

    else:
        try:
            # noinspection SqlDialectInspection,SqlNoDataSourceInspection
            cursor.execute('insert into faceit_stats (STEAM_ID) values(%s)', (steam_id, ))

        except mysql.connector.errors.IntegrityError:
            pass

    db.commit()

    cursor.close()
    db.close()


def update_mm_stats(steam_id: int, stats: dict):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    cursor.execute(f'update mm_stats set RANK = %s, KPD = %s, RATING = %s, '
                   f'CLUTCH = %s, BEST_WEAPON = %s, WIN_RATE = %s, HS = %s, ADR = %s, ENTRY_SUCCESS = %s, '
                   f'MOST_PLAYED_MAP = %s, MOST_SUCCESSFUL_MAP = %s where STEAM_ID = %s;',
                   (stats["rank"], stats["kpd"], stats["rating"],
                    stats["clutch"], stats["best_weapon"], stats["win_rate"], stats["hs"], stats["adr"],
                    stats["entry_success"], stats["most_played_map"], stats["most_successful_map"], steam_id))
    db.commit()

    cursor.close()
    db.close()


def update_faceit_stats(steam_id: int, stats: dict):
    db = mysql.connector.connect(host=db_host, port=db_port, user=db_user,
                                 passwd=db_password, database=db_name)
    cursor = db.cursor(buffered=True)

    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    cursor.execute(f'update faceit_stats set RANK = %s, ELO = %s, KPD = %s, RATING = %s, '
                   f'WIN_RATE = %s, HS = %s, MATCHES = %s, '
                   f'MOST_PLAYED_MAP = %s, MOST_SUCCESSFUL_MAP = %s where STEAM_ID = %s;',
                   (stats["rank"], stats["elo"], stats["kpd"], stats["rating"],
                    stats["win_rate"], stats["hs"], stats["matches"],
                    stats["most_played_map"], stats["most_successful_map"], steam_id))
    db.commit()

    cursor.close()
    db.close()
