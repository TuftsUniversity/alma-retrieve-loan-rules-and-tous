#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import threading
from selenium.webdriver.chrome.service import Service
import csv
import sys
import time
import os
import time
import re

import pandas as pd
import numpy as np


import secrets_local

sys.path.append("scripts/")

from functions import *


if (
    " " in secrets_local.alma_base_url
    or " " in secrets_local.username
    or " " in secrets_local.password
):
    print(
        "Please set your admin account credentials and Alma URL in the secrets_local.py file"
    )
    sys.exit(1)

# iterate through fulfillment full_units
oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)
# Use Service class with ChromeDriverManager
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)

N = 1  # Number of threads
OUTPUT_FILE = "Bulk_Checkout_Request_Results.xlsx"
FORMATTED_OUTPUT_FILE = "Bulk_Checkout_Request_Results - Highlighted.xlsx"
OUTPUT_DIR = "Output"

fulfillment_units_processed = []
rules_processed = []

# driver = webdriver.Chrome()#home_directory_chromedriver_path)
# sys.exit()

def init_driver():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def worker_thread(thread_id, threads):
    driver = init_driver()
    # buffer = []
    # current_fulfillment_unit = None
    driver = init_driver()
    driver.get(secrets_local.alma_base_url)
    time.sleep(10)
    element = login(driver, secrets_local.username, secrets_local.password)
    time.sleep(20)
    try:
        modal = driver.find_element(By.XPATH, "//div[@id='onetrust-close-btn-container']//button")
        print("GDPR modal detected. Attempting to close it.")
        modal = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='onetrust-close-btn-container']//button"))
        )
        modal.click()
        print("GDPR modal closed.")
    except TimeoutException:
        print("No GDPR modal detected.")
    except:
        print("No GDPR modal")

    
   
    fulfillment_unit_df = navigate_to_fulfillment_units(driver, secrets_local.alma_base_url)
    x = 0

    fulfillment_unit_length = len(fulfillment_unit_df)

    print(fulfillment_unit_length)

    print(type(fulfillment_unit_length))    
    while True:
        with threading.Lock():


            if x + 1 >= len(fulfillment_unit_df):
                break
            
            fulfillment_unit = fulfillment_unit_df.loc[x, "sortable"]
            

        # Fulfillment unit initial actions
        try:
            navigate_to_fulfillment_units(driver, secrets_local.alma_base_url)
            fulfillment_unit = safe_find_element_text(driver, By.XPATH, f"//table/tbody/tr[{x+1}]/td[1]")
            rules_df, locations_list = navigate_to_rules_tab_get_lists(driver, x)
            rule_count = len(rules_df)
            y = 0

            while y < rule_count:
                if (fulfillment_unit, y) in rules_processed:
                    y += 1
                    continue

                # Process rule
                try:
                    rule_name = rules_df.loc[y, "Rule Name"]
                    print(f"Thread-{thread_id} processing rule {rule_name} in fulfillment unit {fulfillment_unit}")
                    # --- Initialize DataFrame and Series for rule row ---
                    rule_df = pd.DataFrame(
                        columns=[
                            "Fullfilment Unit",
                            "Possible Locations",
                            "Enabled",
                            "Rule Name",
                            "Unnamed: 0",
                            "Unnamed: 4",
                            "Output",
                        ]
                    )

                    s = pd.Series(
                        [None, None, None, None, None, None, None],
                        index=[
                            "Fullfilment Unit",
                            "Possible Locations",
                            "Enabled",
                            "Rule Name",
                            "Unnamed: 0",
                            "Unnamed: 4",
                            "Output",
                        ],
                    )
                    rule_df = pd.concat([rule_df, pd.DataFrame([s])], ignore_index=True)

                    # --- Get Rule Name and Output ---
                    rule_name = rules_df.loc[y, "Rule Name"]
                    output = rules_df.loc[y, "Output"]
                    print("Rule name: " + str(rule_name))

                    # --- Wait for rule row to become visible ---
                    safe_find_element(driver, By.XPATH, f"//table/tbody/tr[{y + 1}]")

                    # --- Populate row values ---
                    fulfillment_unit = fulfillment_unit.replace("\\", "-")
                    rule_df.loc[0, "Fullfilment Unit"] = fulfillment_unit
                    rule_df.loc[0, "Possible Locations"] = ",".join(locations_list)
                    rule_df.loc[0, "Rule Name"] = rule_name
                    rule_df.loc[0, "Output"] = output

                    # --- Get "Enabled" Status ---
                    enabled_value = get_enabled_value(driver, y)
                    rule_df.loc[0, "Enabled"] = enabled_value

                    # --- Navigate to Loan Rule Details ---
                    navigate_to_loan_rule(driver, y)
                    # time.sleep(2)  # Short wait to let the page load (optional)

                    # --- Get Parameter String ---
                    parameter_string = get_parameter_list(driver)
                    rule_df['Parameter'] = parameter_string
                    # --- Navigate to Terms of Use ---
                    navigate_to_tou(driver)
                    # time.sleep(2)

                    # --- Parse TOU into DataFrame ---
                    tou_series = get_tou_as_series(driver)
                    rule_df = rule_df.join(tou_series.to_frame(rule_df.index[0]).T)

                    # --- Remove duplicates ---
                    rule_df = rule_df.drop_duplicates(subset=["Rule Name"])

                    # --- Append to master ---
                    # if y == 0:
                    #     ruless_df = rule_df.copy()
                    # else:
                    #     ruless_df = pd.concat([ruless_df, rule_df], ignore_index=True)

                    # --- Return to rule list view ---
                    try:
                        click_element_with_retry(driver, By.XPATH, '//*[@id="generic_back_button"]')
                        time.sleep(2.5)
                        click_element_with_retry(driver, By.XPATH, '//*[@id="generic_back_button"]')
                    except:
                        print("No back button needed")

                

                    rules_processed.append((fulfillment_unit, y))
                    
                    #if len(buffer) >= BUFFER_WRITE_INTERVAL:
                    write_buffer_to_excel(rule_df, thread_id, OUTPUT_DIR)
                   

                except Exception as e:
                    print(f"Thread-{thread_id} error processing rule {rule_name}: {e}")

                y += 1
            fulfillment_units_processed.append(fulfillment_unit)


            
            print(f"Thread-{thread_id} finished.")
        except Exception as e:
            print(f"Thread-{thread_id} error processing fulfillment unit {fulfillment_unit}: {e}")

        x += 1

def main():
    # Initialize driver and navigate to fulfillment units


    # Start threads
    threads = []
    for i in range(N):
        t = threading.Thread(target=worker_thread, args=(i, threads))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    merge_excel_files(OUTPUT_DIR, OUTPUT_FILE)
    print("All threads complete.")

if __name__ == "__main__":
    main()
