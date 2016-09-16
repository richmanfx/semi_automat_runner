#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import sleep

import functions
import datetime

VERSION = '1.0.0'
__author__ = 'Aleksandr Jashhuk, Zoer, R5AM, www.r5am.ru'


def main():
    ini_config_name = 'semi_automat_runner.ini'

    functions.clear_console()  # Очистить консоль
    ini_config = functions.configs_read(ini_config_name)  # Считываем INI-конфиг
    # print(ini_config['browser']['browser_size'])          # Доступ к параметру в INI-файле

    # Считать данные из XML-файлов в словарь
    xml_tree_dict = functions.xml_configs_read(ini_config)
    # print xml_tree_dict

    # print(xml_tree_dict['online_settings'].getroot())

    # Тип сервера - Продакшн или Тестовый
    server_role = functions.get_server_role(ini_config, ini_config_name)
    print('Используется ' + server_role + '-сервер.')
    print('Начало работы: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Получаем webdriver с браузером, указанным в INI-файле
    driver = functions.get_webdriver(ini_config, ini_config_name)

    # Выставить время до ожидания вебэлемента
    print(u'Время ожидания элементов (implicitly_wait), сукунд: ' +
          ini_config['general']['implicitly_wait'])
    driver.implicitly_wait(ini_config['general']['implicitly_wait'])

    # Открываем страницу
    link = functions.get_xml_value(xml_tree_dict['test_script'], 'serviceDirectLink')
    print(u'Открываем страницу: ' + link)
    driver.get(link)

    sleep(10)
    print('Конец работы:  ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    driver.close()


if __name__ == '__main__':
    main()
