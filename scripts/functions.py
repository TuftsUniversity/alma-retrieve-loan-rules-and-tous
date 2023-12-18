#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


import pandas as pd
import numpy as np


from selenium.webdriver.support.ui import Select

import sys
import time
import csv
import re
import math


def login(driver, username, password):




    element = driver.find_element(By.ID, 'username')

    time.sleep(2)
    element.send_keys(username)

    element = driver.find_element(By.ID, 'password')

    element.send_keys(password)

    element.send_keys(Keys.RETURN)

    return element



def navigate_to_fulfillment_units(driver, url):
    time.sleep(2)

    driver.get(url + "/ng/page;u=%2Fful%2Faction%2FpageAction.do%3FxmlFileName%3DfulfillmentUnits.fulfillment_units_list.xml&almaConfiguration%3Dtrue&pageViewMode%3DEdit&operation%3DLOAD&pageBean.orgUnitCode%3D3851&pageBean.currentUrl%3DxmlFileName%253DfulfillmentUnits.fulfillment_units_list.xml%2526almaConfiguration%253Dtrue%2526pageViewMode%253DEdit%2526operation%253DLOAD%2526pageBean.orgUnitCode%253D3851%2526resetPaginationContext%253Dtrue%2526showBackButton%253Dfalse&pageBean.navigationBackUrl%3D..%252Faction%252Fhome.do&resetPaginationContext%3Dtrue&showBackButton%3Dfalse&pageBean.ngBack%3Dtrue;ng=true")

def get_fulfillment_unit_count(driver):
    time.sleep(3)
    count = len(driver.find_elements(By.XPATH, "//table/tbody/tr"))
    return count

def navigate_to_rules_tab_get_lists(driver, full_unit_number):
    wait = WebDriverWait(driver, 20)
    element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[contains(@id, "input_fulfillmentUnits_' + str(full_unit_number) + '")]')))
    element.click()

    #driver.find_element(By.ID, 'input_fulfillmentUnits_' + str(full_unit_number)).click()
    wait = WebDriverWait(driver, 20)
    element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[contains(@id, "fulfillmentUnits_' +  str(full_unit_number) + '_c.ui.table.btn.edit")]/a')))
    element.click()



    wait = WebDriverWait(driver, 20)
    element = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='fulfillmentunit_editfulfillmentUnitLocations_span']/a")))
    element.click()

    locations_html = driver.page_source
    wait = WebDriverWait(driver, 20)
    content = wait.until(ec.visibility_of_element_located((By.ID, "fulfillmentUnitLocationsList"))).get_attribute("outerHTML")
    locations = pd.read_html(content)
    locations_df = locations[0]

    if len(locations_df) >= 20:
        wait = WebDriverWait(driver, 20)
        element = wait.until(ec.visibility_of_element_located((By.ID, "navigaionSizeBarSize2")))
        element.click()

    locations_html = driver.page_source
    content = driver.find_element(By.XPATH, '//*[contains(@id, "fulfillmentUnitLocationsList")]').get_attribute("outerHTML")
    locations = pd.read_html(content)
    locations_df = locations[0]

    locations_list = locations_df['sorted ascending'].tolist()


    wait = WebDriverWait(driver, 20)
    element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="fulfillmentunit_editfulfillmentUnitRules_span"]/a')))
    element.click()


    time.sleep(2)
    html = driver.page_source
    rules_df = pd.read_html(html)[0]
    rule_count = len(rules_df)

    print(rules_df)
    print("\n\n\n")
    print(locations_df)

    return [rules_df, locations_list]

###################################
####    This gets the value of the
####    enabled slider switch to
####    see if the rule is active
def get_enabled_value(driver, y):


    wait = WebDriverWait(driver, 20)
    element_enable = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[contains(@id, 'ROW_" + str(y) + "_COL_activeImage')]/div")))

    enabled_or_disabled_attribute = element_enable.get_attribute('aria-label')


                                                                  #pageBeanrules        0     activeImage


    if (re.search(r'\sactive', enabled_or_disabled_attribute)):
        enabled_value = "Active"
    elif(re.search(r'inactive', enabled_or_disabled_attribute)):
        enabled_value = "Inactive"

    # if y == 6:
    #     print("enabled value: " + enabled_value)
    #     sys.exit()
    return enabled_value

def navigate_to_loan_rule(driver, y):

    wait = WebDriverWait(driver, 20)
    button = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="input_rules_' + str(y) + '"]')))

    ActionChains(driver).move_to_element(button).click(button).perform()



    wait = WebDriverWait(driver, 20)
    element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ROW_ACTION_rules_'  + str(y) + '_c.ui.table.btn.edit"]/a')))
    element.click()

    # wait = WebDriverWait(driver, 20)
    # try:
    #     element = wait.until(ec.visibility_of_element_located((By.ID, "TABLE_DATA_rules")))
    # except:
    #     print("already there")
###################################
####    This function retrieves the parameter
####    table from the loan rule and compresses the
####    potentially multi-row table into a single, key-value
####    type list and joins that into a string to enter into
####    the Parameters field of the row assoicated with this loan rule
def get_parameter_list(driver):


    time.sleep(1)
    html = driver.page_source

    try:

        parameter_df = pd.read_html(html)[0]




        parameter_list = []
        for z in range(0, len(parameter_df)):
            parameter_list.append(parameter_df.loc[z, 'Name'] + " " + parameter_df.loc[z,'Operator'] + parameter_df.loc[z, 'Value'])

        parameter_string = "; ".join(parameter_list)

    except:
        parameter_string = ""
    return parameter_string

def navigate_to_tou(driver):
    wait = WebDriverWait(driver, 20)
    element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="uiconfiguration_rule_detailsview_tou"]')))
    element.click()
    # wait = WebDriverWait(driver, 20)
    # try:
    #     element = wait.until(ec.visibility_of_element_located((By.ID, "TABLE_DATA_ruleParamsList")))
    # except:
    #     print("already there")
###################################
####    This ingests the TOU table,
####    sets the Policy Name as the dataframe index
####    and the "type" as value, and squeezes this datafram into
####    a series, that can be appeneded as additional columns in the
####    dataframe row for the associated loan rule
def get_tou_as_series(driver):
    html = driver.page_source
    tou_df = pd.read_html(html)[0]


    time.sleep(1)
    tou_df = tou_df[['Policy Name', 'Policy Type']]
    tou_df = tou_df.set_index('Policy Type')
    tou_series = tou_df.squeeze()

    return tou_series
