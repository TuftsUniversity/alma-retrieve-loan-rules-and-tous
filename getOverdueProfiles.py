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

sys.path.append(os.path.relpath('config/'))
import secrets_local

sys.path.append(os.path.relpath('scripts/'))

from functions import *




# iterate through fulfillment full_units
oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)
# Use Service class with ChromeDriverManager
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)


OUTPUT_FILE = "Overdue and Lost Profiles.xlsx"
FORMATTED_OUTPUT_FILE = "Overdue and Lost Profiles - Highlighted.xlsx"
OUTPUT_DIR = "Output"
YELLOW = '\033[33m'
RESET = '\033[0m'
n = input(f"{YELLOW}Please close all Chrome browsers and processes before continuing, since this program uses multithreading to expedite the process of retrieving loan rules.\n\nPress any key to continue, once you have closed Chrome.\n\nThis program also uses multithreading to increase speed since drilling through fulfillment configuration windows takes a while.  But the number of threads that is best matched to your local environment is based on how reliable and fast your internet is.  Please choose one of the options below:\n\n\t1 (1 thread: Slow internet)\n\t2 (2 threads: Faster internet)\n\t3 (3 threads: Fastest internet)\n\n\tChoice:")


instance = ""
env = input(f"Run against (1) Sandbox or (2) Production? Enter 1 or 2: {RESET}").strip()
if env == "1":
    
    alma_base_url = secrets_local.alma_base_url_sandbox
    instance = "sandbox"
elif env == "2":
    alma_base_url = secrets_local.alma_base_url_prod
    instance = "prod"
else:
    print("Invalid selection. Exiting.")
    exit(1)

if (
    " " in secrets_local.alma_base_url
    or " " in secrets_local.username
    or " " in secrets_local.password
):
    print(
        "Please set your admin account credentials and Alma URL in the secrets_local.py file"
    )
    sys.exit(1)

n = int(n)
n = int(n)

if n in (1,2,3):
    N = n

else:
    print("\n\nInvalid choice.   Try again")
    sys.exit()

profile_pages_processed = []
profiles_processing = []
failed_profiles = {}

thread_complete = []



# failed_rules_processed = []

# driver = webdriver.Chrome()#home_directory_chromedriver_path)
# sys.exit()

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def iterate(sequence, driver, profile_pages_elements, thread_id):
    x = 0
    while True:
        with threading.Lock():

            profile_number_of_pages = len(profile_pages_elements)

            if sequence == "Error Checking":
                keys = list(failed_profiles.keys())
                profile_number_of_pages = len(keys)
                print(failed_profiles)
                print(profile_pages_elements)
                
         
                if x in keys:
                    current_x = keys[x]
                else:
                    continue


            else:
                current_x = x
                
            
            if x + 1 > profile_number_of_pages:
                break
            


            for li in profile_pages_elements:
                try:
                    # Look for the <a> inside <li> and match text to page number
                    link = safe_find_element_within_element(li, By.TAG_NAME, "a")
                    if link.text.strip() == str(current_x):
                        link.click()
                        break
                except:
                    continue  # Some <li> elements may not have <a> (e.g., input-only)
                       

            # Fulfillment unit initial actions
            try:
               
                profiles_df = pd.read_html(driver.page_source)[0]
                #rules_df, locations_list = navigate_to_rules_tab_get_lists(driver, current_x)
                # if sequence == "Error Checking":
                #     rule_count = len(failed_rules[current_x][1])

                # else:
                profile_count_on_page = len(profiles_df)
                y = 0
                # failover = False
                while y < profile_count_on_page:

                    try:
                        if sequence == "Error Checking":

                            if y in failed_profiles[current_x][y]:
                                 current_y = failed_profiles[current_x][y]

                            else:
                                continue


                        ## testing
                        # elif sequence == "Main Sequence" and thread_id == 0 and x in (2,3) and y in (2,3):
                        #     if current_x in failed_rules:
                        #         failed_rules[x][1].append(current_y)
                        #     else:
                        #         failed_rules[x].append([current_y])
                        else:
                            current_y = y
                        # if failover == True:
                        #     navigate_to_fulfillment_units(driver, secrets_local.alma_base_url)
                        #     click_element_with_retry(driver, By.XPATH, f'//*[contains(@id, "input_fulfillmentUnits_{x}")]')
                        #     click_element_with_retry(driver, By.XPATH, f'//*[contains(@id, "fulfillmentUnits_{x}_c.ui.table.btn.edit")]/a')
                        #     click_element_with_retry(driver, By.XPATH, '//*[@id="fulfillmentunit_editfulfillmentUnitRules_span"]/a')
                        #     time.sleep(2)
                        #     failover = False

                        # if y > 3:
                        #     break
                        if sequence == "Main Sequence":
                            if ((current_x, current_y)) in profiles_processing:
                                y += 1
                                continue

                        profiles_processing.append((current_x, current_y))
                        # Process rule
                        # try:

                        profile_name = profiles_df.loc[current_y, "Name"]
                        print(f"Thread-{thread_id} processing rule {profile_name} on overdue and lost profiles page {current_x}")
                        # --- Initialize DataFrame and Series for rule row ---
                        profile_df = pd.DataFrame(
                            columns=[
                                "Profile Type",
                                "Days After Due Date",
                                "Loan Status",
                                "User Group",
                                "Library",
                                "Locations",
                                "Item Policy",
                                "Material Type"
                            ]
                        )

                        s = pd.Series(
                            [None, None, None, None, None, None, None],
                            index=[
                                "Profile Type",
                                "Days After Due Date",
                                "Loan Status",
                                "User Group",
                                "Library",
                                "Locations",
                                "Item Policy",
                                "Material Type"
                            ],
                        )
                        profile_df = pd.concat([profile_df, pd.DataFrame([s])], ignore_index=True)
                        profile_df['Name'] = None
                        profile_df['Profile Type'] = None
                        profile_df['Days After Due Date'] = None
                        profile_df['Loan Status'] = None
                        profile_df['User Group'] = None
                        profile_df['Library'] = None
                        profile_df['Locations'] = None
                        profile_df['Item Policy'] = None
                        profile_df['Material Type'] = None

                        profile_type_element = safe_find_element(driver, By.ID, "pageBeanlostLoanProfileprofileType")
                        profile_type = profile_type_element.get_attribute("title")
                        
                        days_after_due_date_element = safe_find_element(driver, By.ID, "pageBeanlostLoanProfiledaysAfterDueDate")

                        days_afer_due_date = days_after_due_date_element.get_attribute("title")

                        statuses = get_tag_values(driver, "pageBeanprocessStatusDummyUXPInputContainer")

                        user_groups = get_tag_values(driver, "pageBeanuserGroupListDummyUXPInputContainer")

                        library_element = safe_find_element(driver, By.ID, "pageBeanlostLoanProfilelibraryStr")
                        library = library_element.get_atttribute("value")

                        locations = get_tag_values(driver, "pageBeanlocationListDummyUXP")

                        item_policies = get_tag_values(driver, "pageBeanitemPolicyListDummyUXPInputContainer")

                        material_types = get_tag_values(driver, "pageBeanmaterialTypeListDummyUXP")

                        profile_df.loc[0, "Name"] = profile_name
                        profile_df.loc[0, 'Profile Type'] = profile_type

                        profile_df.loc[0, 'Days After Due Date'] = days_afer_due_date
                        
                        profile_df.loc[0, 'Loan Status'] = statuses
                        profile_df.loc[0, 'User Group'] = user_groups
                        profile_df.loc[0, 'Library'] = library
                        profile_df.loc[0, 'Locations'] = locations
                        profile_df.loc[0, 'Item Policy'] = item_policies
                        profile_df.loc[0, 'Material Type'] = material_types

                        # --- Get Rule Name and Output ---
                        #rule_name = rules_df.loc[current_y, "Rule Name"]
                        #output = rules_df.loc[current_y, "Output"]
                        #print("Rule name: " + str(rule_name))

                        # # --- Wait for rule row to become visible ---
                        # safe_find_element(driver, By.XPATH, f"//table/tbody/tr[{current_y + 1}]")

                        # # --- Populate row values ---
                        # fulfillment_unit = fulfillment_unit.replace("\\", "-")
                        # rule_df.loc[0, "Fulfillment Unit"] = fulfillment_unit
                        # rule_df.loc[0, "Fulfillment Unit Number"] = current_x
                        # rule_df.loc[0, "Possible Locations"] = ",".join(locations_list)
                        # rule_df.loc[0, "Rule Name"] = rule_name
                        # rule_df.loc[0, "Rule Number"] = current_y
                        # rule_df.loc[0, "Output"] = output

                        # # --- Get "Enabled" Status ---
                        # enabled_value = get_enabled_value(driver, current_y)
                        # rule_df.loc[0, "Enabled"] = enabled_value

                        # # --- Navigate to Loan Rule Details ---
                        # navigate_to_loan_rule(driver, current_y)
                        # # time.sleep(2)  # Short wait to let the page load (optional)

                        # --- Get Parameter String ---
                        # parameter_list = get_parameter_list(driver)

                    

                        # for policy in parameter_list:
                        #     if any("Item Policy" in key for key in policy):
                        #         key = next(k for k in policy if "Item Policy" in k)
                        #         operator, value = policy[key]

                        #         rule_df.loc[0, 'Item Policy Operator'] = operator
                        #         rule_df.loc[0, 'Item Policy Value'] = value
                        #         pd.options.display.max_rows = None
                        #         pd.options.display.max_columns = None      
                        #         # print(rule_df)

                        #     if any("User Group" in key for key in policy):
                        #         key = next(k for k in policy if "User Group" in k)
                        #         operator, value = policy[key]

                        #         rule_df.loc[0, 'User Group Operator'] = operator
                        #         rule_df.loc[0, 'User Group Value'] = value
                        #         pd.options.display.max_columns = None      
                        #         # print(rule_df)
                        #     if any("Location" in key for key in policy):
                        #         key = next(k for k in policy if "Location" in k)
                        #         operator, value = policy[key]

                        #         rule_df.loc[0, 'Location Operator'] = operator
                        #         rule_df.loc[0, 'Location Value'] = value
                        #         pd.options.display.max_columns = None      
                            

                        
                        # # --- Navigate to Terms of Use ---
                        # navigate_to_tou(driver)
                        # # time.sleep(2)

                        # # --- Parse TOU into DataFrame ---
                        # tou_series = get_tou_as_series(driver)
                        # rule_df = rule_df.join(tou_series.to_frame(rule_df.index[0]).T)

                        # --- Remove duplicates ---
                        profile_df = profile_df.drop_duplicates(subset=["Name"])

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

                    


                        # rule_df = rule_df.applymap(escape_equals)
                        
                    
                        #if len(buffer) >= BUFFER_WRITE_INTERVAL:
                        write_buffer_to_excel(profile_df, thread_id, OUTPUT_DIR)
                        

                        y += 1
                        
                    except Exception as e:
                        print(f"Thread-{thread_id} error processing rule {rule_name}: {e}.  Restarting")
                        if current_x in failed_profiles:
                            failed_profiles[current_x].append(current_y)
                        else:
                            failed_profiles[current_x] = [current_y]
                        

                        worker_thread(thread_id, "", sequence)
                profile_pages_processed.append(current_x)


            
                # if y > 3:
                #     break
            
            except Exception as e:
                # if current_x in failed_rules:
                #     failed_rules[x][1].append(current_y)
                # else:
                #     failed_rules[x].append([current_y])
                print(f"Thread-{thread_id} error processing fulfillment unit {fulfillment_unit}: {e}")
        x += 1

        # if len(failed_rules) > 0 and len(failed_rules) < len(failed_rules_processed):
        #     ## process with retry
        #     failed_rules_processed.append(())
def worker_thread(thread_id, threads, sequence):
    driver = init_driver()
    # buffer = []
    # current_fulfillment_unit = None
    
    driver.get(alma_base_url)
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

    
   
    profiles_page_elements = navigate_to_overdue_profiles(driver, alma_base_url)
    x = 0

    

    # print(fulfillment_unit_length)

    # print(type(fulfillment_unit_length))

    ## create slight offset so threads don't trip over each other
    if thread_id == 1:
        time.sleep(5)
    if thread_id == 2:
        time.sleep(10)
    if thread_id == 3:
        time.sleep(15)
 
    if sequence == "Main Sequence":
        iterate("Main Sequence", driver, profiles_page_elements, thread_id)
    else:
        iterate("Error Checking", driver, profiles_page_elements, thread_id)

    


def escape_equals(val):
    if isinstance(val, str) and val.strip().startswith('='):
        return "'" + val  # Excel will treat it as literal text
    return val
def main():
    # Initialize driver and navigate to fulfillment units


    # Start threads
    threads = []
    for i in range(N):
        t = threading.Thread(target=worker_thread, args=(i, threads, "Main Sequence"))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    if len(failed_profiles) > 0:
        worker_thread(N + 1, threads, "Error Checking")

    final_df = merge_excel_files(OUTPUT_DIR, OUTPUT_FILE)
    final_df.to_excel(instance + " - " + OUTPUT_FILE, index=False)

    highlight_unique_values(output_file, output_file)

    print("All threads complete.")

if __name__ == "__main__":
    main()
