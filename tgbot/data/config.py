# - *- coding: utf- 8 - *-
import configparser

read_config = configparser.ConfigParser()
read_config.read('settings.ini')

BOT_TOKEN = read_config['settings']['token'].strip()  # Токен бота
PATH_DATABASE = 'tgbot/data/database.db'  # Путь к БД
PATH_LOGS = 'tgbot/data/logs.log'  # Путь к Логам
BOT_VERSION = '3.1'
BOT_DESCRIPTION = "Привет! Я - бот OUTPOST, ваш помощник в мире моды! Я здесь, чтобы помочь вам найти идеальную одежду для вашего стиля и настроения. У меня есть широкий ассортимент модной одежды и аксессуаров, которые помогут вам создать свой неповторимый образ. Пожалуйста, не стесняйтесь задавать мне вопросы и делиться своими предпочтениями, чтобы я мог быстро найти то, что вам нужно. Давайте начнем!"  


# Получение администраторов бота
def get_admins():
    read_admins = configparser.ConfigParser()
    read_admins.read('settings.ini')

    admins = read_admins['settings']['admin_id'].strip()
    admins = admins.replace(' ', '')

    if ',' in admins:
        admins = admins.split(',')
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while '' in admins: admins.remove('')
    while ' ' in admins: admins.remove(' ')
    while '\r' in admins: admins.remove('\r')

    admins = list(map(int, admins))

    return admins


