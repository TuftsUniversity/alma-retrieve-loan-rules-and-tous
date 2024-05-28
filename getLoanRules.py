#!/usr/bin/env python3
#################################################
####    Author: Henry Steele, LTS, Tufts University
####    Title: Get Loan Rules, getLoanRules.py
####    Purpose:
####        Because the fulfillment unit rules and TOU tables
####        are not retrievable via API or any other systematic way,
####        this script uses Python Selenium to drill through the loan
####        fulfillment unit rules and attach:
####            - loan rule and fulfillment unit info
####            - conditions under which it is enacted
####            - the TOU and all its terms
####            on a single lines
####        The output of this script is a table with the fulfillment unit,
####        fulfillment unit possible locations, loan rule and multiple parameters
####        if there are multiple wrapped up onto one line, and all the policies of the
####        associated TOU.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
import csv
import sys
import time
import os
import time
import re

import pandas as pd
import numpy as np


import secrets_local

sys.path.append('scripts/')
from functions import *


if " " in secrets_local.alma_base_url or " " in secrets_local.username or " " in secrets_local.password:
    print("Please set your admin account credentials and Alma URL in the secrets_local.py file")
    sys.exit(1)

oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
	os.makedirs(oDir)
#for windows
home_directory_chromedriver_path = os.path.expanduser('~') + "/chromedriver.exe"
driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome()#home_directory_chromedriver_path)
#sys.exit()

driver.get(secrets_local.alma_base_url)
time.sleep(5)
element = login(driver, secrets_local.username, secrets_local.password)
time.sleep(8)

full_units = navigate_to_fulfillment_units(driver, secrets_local.alma_base_url)

#get number of fulfillment full_units
time.sleep(2)
full_unit_count = get_fulfillment_unit_count(driver)

html = driver.page_source

fulfillment_unit_df = pd.read_html(html)[0]

print(fulfillment_unit_df)

#iterate through fulfillment full_units
x = 2

print("Fulfillment unit count: " + str(full_unit_count))
while x < 3:#full_unit_count:



    fulfillment_unit = fulfillment_unit_df.loc[x, 'sortable']

    return_list = navigate_to_rules_tab_get_lists(driver, x)


    rules_df = return_list[0]
    locations_list = return_list[1]

    rule_count = len(rules_df)


    y = 0
    start = y
    print("Number of rules in Fulfillment unit " + str(rule_count))



    while y < rule_count:

        rule_df = pd.DataFrame(columns=['Fullfilment Unit', 'Possible Locations', 'Enabled', 'Rule Name', 'Unnamed: 0', 'Unnamed: 4', 'Output'])

        s = pd.Series([None,None,None,None,None,None,None],index=['Fullfilment Unit', 'Possible Locations', 'Enabled', 'Rule Name', 'Unnamed: 0', 'Unnamed: 4', 'Output'])
        rule_df = pd.concat([rule_df, pd.DataFrame([s])], ignore_index=True)

        rule_name = rules_df.loc[y, 'Rule Name']
        print("Rule name: " + str(rule_name))
        output = rules_df.loc[y, 'Output']


        fulfillment_unit = fulfillment_unit.replace("\/", '-')
        fulfillment_unit = fulfillment_unit.replace("\\", '-')
        rule_df['Fullfilment Unit'] = fulfillment_unit
        rule_df['Possible Locations'] = ",".join(locations_list)
        rule_df['Rule Name'] = rule_name
        rule_df['Output'] = output





        time.sleep(2)

        enabled_value = ""




        enabled_value = get_enabled_value(driver, y)

        rule_df['Enabled'] = enabled_value

        navigate_to_loan_rule(driver, y)




        time.sleep(2)



        parameter_string = get_parameter_list(driver)

        rule_df['Parameter'] = parameter_string


        navigate_to_tou(driver)

        time.sleep(2)
        tou_series = get_tou_as_series(driver)


        rule_df = rule_df.join(tou_series.to_frame(rule_df.index[0]).T)

        rule_df = rule_df.drop_duplicates(subset=['Rule Name'])

        if y == start:
            ruless_df = rule_df.copy()


        ###################################
        ####    Go back to start to get the
        ####    next loan rule

        time.sleep(1)
        wait = WebDriverWait(driver, 20)
        element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="generic_back_button"]')))
        element.click()
        time.sleep(2.5)
        wait = WebDriverWait(driver, 20)
        try:
            element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="generic_back_button"]')))
            element.click()
        except:
            print("No back button needed")
        ruless_df = pd.concat([ruless_df, rule_df], ignore_index=True)


        y += 1
    ruless_df = ruless_df.drop_duplicates(subset=['Rule Name'])

    fulfillment_unit = re.sub(r'[^A-Za-z0-9 ]','-', fulfillment_unit)

    ruless_df.to_excel("Output/" + fulfillment_unit + ".xlsx", index=False)
    navigate_to_fulfillment_units(driver, secrets_local.alma_base_url)




    x += 1
