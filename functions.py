# -*- coding: utf-8 -*-
from os import system, path
from sys import platform
from configparser import ConfigParser
import xml.etree.cElementTree as ET
from pytz import timezone
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


# Очистка консоли в Windows и Linux
def clear_console():
    if platform == 'win32':
        system('cls')
    else:
        system('clear')
    print("")


# Считывает и возвращает информацию из конфигурационных файлов
def configs_read(ini_config_name):
    if not path.isfile(ini_config_name):
        print('INI-файл ' + ini_config_name + ' не существует.')
        exit(1)

    config_ini = ConfigParser()
    config_ini.read(ini_config_name, "utf-8-sig")  # sig - для BOM-символов в начале UTF-8 файла

    return config_ini


# Возвращает список ElementTree XML-конфигов, указанных в INI-файле
def xml_configs_read(ini_config):
    xml_configs_dict = {"online_settings": 0, "test_runtime": 0,
                        "testProperties_online": 0, "test_script": 0}
    xml_configs = []
    configs_path = ini_config['xml_files']['configs_path']
    for xml_file in (ini_config['xml_files']['online_settings_config'],
                     ini_config['xml_files']['test_runtime_config'],
                     ini_config['xml_files']['testProperties_online_config'],
                     ini_config['xml_files']['test_script']
                     ):
        # Существует ли файл
        # print(path.sep)
        if not path.isfile(configs_path + path.sep + xml_file):
            print(u'Файл ' + configs_path + path.sep + xml_file + u' не существует.')
            exit(1)

        xml_configs.append(ET.ElementTree(file=configs_path + path.sep + xml_file))

    # Список загоняем в словарь
    for i, key in enumerate(xml_configs_dict.keys()):
        xml_configs_dict[key] = xml_configs[i]

    return xml_configs_dict


# Из INI-файла получает роль для сервера - тест или прод
def get_server_role(ini_config, ini_config_name):
    role = ''
    if ini_config['general']['server_type'] == 'test':
        role = 'test'
    elif ini_config['general']['server_type'] == 'prod':
        role = 'prod'
    else:
        print('В файле ' + ini_config_name + ' не указан тип сервера: "prod" или "test".')
        exit(1)
    return role


# Возвращает WebDriver соответствующий браузеру, указанному в INI-файле
def get_webdriver(ini_config, ini_config_name):
    driver = webdriver

    if ini_config['browser']['browser_name'] == 'phantomjs':
        driver = webdriver.PhantomJS(executable_path='webdrivers' + path.sep + 'phantomjs')
    elif ini_config['browser']['browser_name'] == 'chrome':
        driver = webdriver.Chrome(executable_path='webdrivers' + path.sep + 'chromedriver.exe')
    elif ini_config['browser']['browser_name'] == 'firefox':
        binary = FirefoxBinary('C:' + path.sep + 'Program Files (x86)' + path.sep + 'Mozilla Firefox' +
                               path.sep + 'firefox.exe')
        driver = webdriver.Firefox(firefox_binary=binary)
    else:
        print('In configuration file ' + ini_config_name + ' is not specified the browser.')
        exit(1)
    print(u'Используется браузер: ' + ini_config['browser']['browser_name'])
    # Размеры окна браузера
    driver2 = set_browser_size(driver, ini_config)

    return driver2


# Установка размера окна браузера
def set_browser_size(driver, ini_config):
    try:
        width = ini_config['browser']['browser_size'].split()[0]
        height = ini_config['browser']['browser_size'].split()[1]
    except KeyError:
        print('The size of the window browser is not specified, will be maximum.')
        driver.maximize_window()
    else:
        driver.set_window_size(width, height)

    return driver


# Получает элемент из словаря с деревьями XML-файлов и текстовое содержание тега NAME
# Возвращает текстовое содержание соответствующего тега VALUE
def get_xml_value(xml_file, name_value):
    value = ''
    root = xml_file.getroot()  # Корневой элемент XML
    for parameter in root.findall('PARAMETERS'):
        name = parameter.find('NAME').text
        if name == name_value:
            value = parameter.find('VALUE').text
    return value


# Проверяет доступность сайта и, если недоступен, выходит из программы.
# Параметр driver Экземпляр WebDriver-а
# Возвращает boolean
def site_available(driver, part_string):
    site_title = driver.title
    try:
        site_title.index(part_string)
    except ValueError:
        status = False
    else:
        status = True
    return status


# Обработка символа в консоли
# Считывает символ с консоли, при 'q', 'Q', 'й', 'Й' - выход из приложения,
#     * при n, N, т, Т - ничего не делаем, при других символах - снова считываем
def input_symbol():
    print(u"Введи 'q' и 'Enter' - для выхода или введи 'n' 'Enter' для продолжения,: ")
    status = ''
    input_string = ''

    while input_string != 'q' and input_string != 'Q' and input_string != 'й' and input_string != 'Й' \
            and input_string != 'n' and input_string != 'N' and input_string != 'т' and input_string != 'Т':

        input_string = raw_input()

        if input_string == 'q' or input_string == 'Q' or input_string == 'й' or input_string == 'Й':
            status = 'exit'
        elif input_string == 'n' or input_string == 'N' or input_string == 'т' or input_string == 'Т':
            status = 'next'
        else:
            print('Не то ввёл: ' + input_string)

    return status


def console_input():
    if input_symbol() == 'exit':
        print ('Bye-bye!')
        exit(2)


def current_time():
    return timezone('Europe/Moscow').fromutc(datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S %Z")
