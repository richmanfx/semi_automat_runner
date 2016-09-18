#!/usr/bin/python
# -*- coding: utf-8 -*-
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# from __future__ import unicode_literals

import functions

VERSION = '1.0.0'
__author__ = 'Aleksandr Jashhuk, Zoer, R5AM, www.r5am.ru'


def main():
    ini_config_name = 'semi_automat_runner.ini'

    functions.clear_console()   # Очистить консоль
    ini_config = functions.configs_read(ini_config_name)    # Считываем INI-конфиг
    # print(ini_config['browser']['browser_size'])  # Доступ к параметру в INI-файле

    # Считать данные из XML-файлов в словарь
    xml_tree_dict = functions.xml_configs_read(ini_config)
    # print(xml_tree_dict)

    # print(xml_tree_dict['online_settings'].getroot())

    # Тип сервера - Продакшн или Тестовый
    print("The '" + functions.get_server_role(ini_config, ini_config_name) + "' server is used.")

    print('BEGIN: ' + functions.current_time())

    # Получаем webdriver с браузером, указанным в INI-файле
    driver = functions.get_webdriver(ini_config, ini_config_name)

    # Выставить время до ожидания вебэлемента
    print('Elements waiting time  (implicitly_wait): ' +
          ini_config['general']['implicitly_wait'] + ' sec.')
    driver.implicitly_wait(ini_config['general']['implicitly_wait'])

    # Открываем страницу
    link = functions.get_xml_value(xml_tree_dict['test_script'], 'serviceDirectLink')
    domain_name = link.split("//")[1].split("/")[0]

    print('Open the page: ' + domain_name)
    driver.get(link)

    # Доступен ли сайт
    print('Test availability of the website: ' + domain_name)
    status = functions.site_available(driver, u'муниципальные услуги')
    if status:
        print('The website ' + domain_name + ' is available.')
    else:
        print('The website ' + domain_name + ' is not available.')
        driver.quit()
        exit(1)

    functions.console_input()   # Continue?

    print('END:  ' + functions.current_time())
    driver.quit()


if __name__ == '__main__':
    main()
