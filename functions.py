# -*- coding: utf-8 -*-
from os import system, path
from sys import platform
from configparser import ConfigParser
import xml.etree.cElementTree as ElTr
from pytz import timezone
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


# Очистка консоли в Windows и Linux
def clear_console():
    """ Console clearing in windows and linux. """
    if platform == 'win32':
        system('cls')
    else:
        system('clear')
    print("")


# Считывает и возвращает информацию из конфигурационных файлов
def configs_read(ini_config_name):
    """ Reads and returns information from the configuration files. """
    if not path.isfile(ini_config_name):
        print('INI-file ' + ini_config_name + ' does not exist.')
        exit(1)

    config_ini = ConfigParser()
    config_ini.read(ini_config_name, "utf-8-sig")   # sig - для BOM-символов в начале UTF-8 файла

    return config_ini


# Возвращает список ElementTree XML-конфигов, указанных в INI-файле
def xml_configs_read(ini_config):
    """ Returns a list of ElementTree XML-config files specified in INI-file. """
    xml_configs_dict = {"online_settings": 0, "test_runtime": 0,
                        "testProperties_online": 0, "test_script": 0}
    xml_configs = []
    configs_path = ini_config['xml_files']['configs_path']
    for xml_file in (ini_config['xml_files']['online_settings_config'],
                     ini_config['xml_files']['test_runtime_config'],
                     ini_config['xml_files']['testProperties_online_config'],
                     ini_config['xml_files']['test_script']
                     ):

        if not path.isfile(configs_path + path.sep + xml_file):     # Существует ли файл
            print('File ' + configs_path + path.sep + xml_file + ' does not exist.')
            exit(1)

        xml_configs.append(ElTr.ElementTree(file=configs_path + path.sep + xml_file))

    for i, key in enumerate(xml_configs_dict.keys()):   # Список загоняем в словарь
        xml_configs_dict[key] = xml_configs[i]

    return xml_configs_dict


# Из INI-файла получает роль для сервера - тест или прод
def get_server_role(ini_config, ini_config_name):
    """ Gets from INI-file the role for the server - 'test' or 'prod'. """
    role = ''
    if ini_config['general']['server_type'] == 'test':
        role = 'test'
    elif ini_config['general']['server_type'] == 'prod':
        role = 'prod'
    else:
        print('In file ' + ini_config_name + ' not specified servers type: "prod" or "test".')
        exit(1)
    return role


# Возвращает WebDriver соответствующий браузеру, указанному в INI-файле
def get_webdriver(ini_config, ini_config_name):
    """ Returns WebDriver the appropriate browser that you specified in the INI-file. """
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
        print('In config file ' + ini_config_name + ' not specified the browser.')
        exit(1)
    print("Use '" + ini_config['browser']['browser_name'] + "'")

    driver2 = set_browser_size(driver, ini_config)  # Размеры окна браузера

    return driver2


# Установка размера окна браузера
def set_browser_size(driver, ini_config):
    """ Sets the size of the browser window. """
    try:
        width = ini_config['browser']['browser_size'].split()[0]
        height = ini_config['browser']['browser_size'].split()[1]
    except KeyError:
        print('The size of the browser window is not specified in the INI-file, will be maximum size.')
        driver.maximize_window()
    else:
        driver.set_window_size(width, height)

    return driver


# Получает элемент из словаря с деревьями XML-файлов и текстовое содержание тега NAME
# Возвращает текстовое содержание соответствующего тега VALUE
def get_xml_value(xml_file, name_value):
    """ Gets the element from the dictionary with a tree of XML-files and text content of the NAME-tag.
        Returns the text content of the corresponding VALUE-tag. """
    value = ''
    root = xml_file.getroot()   # Корневой элемент XML
    for parameter in root.findall('PARAMETERS'):
        name = parameter.find('NAME').text
        if name == name_value:
            value = parameter.find('VALUE').text
    return value


# Проверяет доступность сайта и, если недоступен, выходит из программы.
# Параметры: driver - экземпляр WebDriver-а, part_string - часть title страницы
# Возвращает: boolean
def site_available(driver, part_string):
    """ Checks the availability of the website and, if unavailable, out of the program. """
    site_title = driver.title
    try:
        site_title.index(part_string)
    except ValueError:
        status = False
    else:
        status = True
    return status


# Обработка символа в консоли
# Считывает символ с консоли, при 'q', 'Q' - выход из приложения,
#  при 'n', 'N' - ничего не делаем и идём дальше, при других символах - снова считываем
def input_symbol():
    """
    Processing symbol in the console:
                                     'q', 'Q' - quit application;
                                     'n', 'N' - do nothing and continue;
                                     with other characters - again read
    """
    print("Input 'q' and 'Enter' to exit or input 'n' 'Enter' to continue: ")
    status = ''
    input_string = ''

    while input_string != 'q' and input_string != 'Q' and input_string != 'n' and input_string != 'N':

        input_string = raw_input()

        if input_string == 'q' or input_string == 'Q':
            status = 'exit'
            print(u'Quit.')
        elif input_string == 'n' or input_string == 'N':
            print(u'Continue.')
            status = 'next'
        else:
            print('Bad input: ' + input_string)

    return status


def console_input():
    """ Check the result of the character input and, if necessary, exit the application. """
    if input_symbol() == 'exit':
        print('Bye-bye!')
        exit(2)


# Возврат форматированных текущих даты и времени с временнОй зоной
def current_time():
    """ Return a formatted current date and time with time zone. """
    return timezone('Europe/Moscow').fromutc(datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S %Z")


# Авторизация ЕСИА, возврат результата в boolean
def authorization(driver, user_name, user_password):
    """ ESIA authorization, returning the result as boolean """
    # Переход в Личный кабинет
    personal_office_element = driver.find_element_by_xpath(
        "//a[@href='lk/main/login/entry.htm']/span[text()='Личный кабинет']")
    personal_office_element.click()

    # Кнопка 'Авторизация по ЕСИА'
    esia_authorization_button = driver.find_element_by_xpath(
        "//a[@href='saml/login' and text()='Авторизация по ЕСИА']")
    esia_authorization_button.click()

    # Сысылка "СНИЛС"
    snils_link_element = driver.find_element_by_xpath(
        "//*[@id='authnFrm']/*/a[@data-bind='visible: snils.canSwitchTo, click: toSnils']")
    snils_link_element.click()

    # Логинимся
    username_field = driver.find_element_by_xpath('.//*[@id="snils"]')
    username_field.send_keys(user_name)

    password_field = driver.find_element_by_xpath('.//*[@id="password"]')
    password_field.send_keys(user_password)

    print(user_password)

    driver.find_element_by_xpath('.//*[@data-bind="click: loginByPwd"]').click()


''' password_field = driver.find_element_by_xpath('.//*[@id="inputPassword"]')
    password_field.send_keys(get_test_script_cfg.user_pswd)
    driver.find_element_by_xpath('.//*[@id="doLogin"]').click()
'''
