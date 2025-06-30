import pandas as pd
import os
import glob
import threading
import requests
import time
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import sys
# Add the full path to "scripts" based on current script location
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, "scripts")

if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)
from functions_drill import *
sys.path.append(os.path.relpath('config/'))
import secrets_local

# --- Constants & Configurations ---
INPUT_DIR_ITEM_POLICY = "./input/Item Policies and Locations"
INPUT_DIR_USER_GROUP = "./input/User Groups"
OUTPUT_FILE = "Bulk_Loan_Request_Results.xlsx"
FORMATTED_OUTPUT_FILE = "Bulk_Loan_Request_Results - Highlighted.xlsx"
OUTPUT_DIR = "Output"
BUFFER_WRITE_INTERVAL = 10
global row_index
YELLOW = '\033[33m'
RESET = '\033[0m'
n = input(f"{YELLOW}Please close all Chrome browsers and processes before continuing, since this program uses multithreading to expedite the process of retrieving loan rules.\n\nPress any key to continue, once you have closed Chrome.\n\nThis program also uses multithreading to increase speed since drilling through fulfillment configuration windows takes a while.  But the number of threads that is best matched to your local environment is based on how reliable and fast your internet is.  Please choose one of the options below:\n\n\t1 (1 thread: Slow internet)\n\t2 (2 threads: Faster internet)\n\t3 (3 threads: Fastest internet)\n\n\tChoice: {RESET}")
# Prompt for environment

instance = ""
env = input(f"Run against (1) Sandbox or (2) Production? Enter 1 or 2: {RESET}").strip()
if env == "1":
    
    api_base_url = secrets_local.alma_base_url_sandbox
    instance = "sandbox"
elif env == "2":
    api_base_url = secrets_local.alma_base_url_prod
    instance = "prod"
else:
    print("Invalid selection. Exiting.")
    exit(1)

n = int(n)

if n in (1,2,3):
    N = n

else:
    print("\n\nInvalid choice.   Try again")
    sys.exit()
row_index_lock = threading.Lock()
row_index = 0
order_of_loan_policy_columns = []
order_of_request_policy_columns = []
def load_first_excel(directory):
    files = glob.glob(os.path.join(directory, "*.xlsx"))
    if not files:
        print(f"No Excel files found in {directory}. Exiting.")
        exit()
    return pd.read_excel(files[0], dtype="str", engine="openpyxl")

item_policy_data = load_first_excel(INPUT_DIR_ITEM_POLICY)
user_group_data = load_first_excel(INPUT_DIR_USER_GROUP)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def worker_thread(thread_id, combined_df):

    driver = init_driver()
    buffer = []
    current_user_id = None

    def navigate_to_checkout():
        driver.get(api_base_url)
        login(driver, secrets_local.username, secrets_local.password)
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

        driver.get(api_base_url + "/ng/page;u=%2Fful%2Faction%2FpageAction.do%3FxmlFileName%3Dtou.fulfillment_configuration_utility.xml&pageViewMode%3DEdit&operation%3DLOAD&backUrl%3D%2Fful%2Faction%2Fmenu.do%3F&pageBean.selectedTab%3DtouType.loan&pageBean.touType%3DLoan&pageBean.displayDueDate%3Dtrue&pageBean.displayReturnDate%3Dtrue&pageBean.currentUrl%3DxmlFileName%253Dtou.fulfillment_configuration_utility.xml%2526pageViewMode%253DEdit%2526operation%253DLOAD%2526backUrl%253D%252Fful%252Faction%252Fmenu.do%253F%2526pageBean.selectedTab%253DtouType.loan%2526pageBean.touType%253DLoan%2526pageBean.displayDueDate%253Dtrue%2526pageBean.displayReturnDate%253Dtrue%2526resetPaginationContext%253Dtrue%2526showBackButton%253Dfalse&pageBean.navigationBackUrl%3D..%252Faction%252Fhome.do&resetPaginationContext%3Dtrue&showBackButton%3Dfalse&menuKey%3Dcom.exlibris.dps.adm.general.menu.initial.Fulfillment.FulfillmentHeader.FulConfigurationUtility")

    navigate_to_checkout()

    while True:

        global row_index
        with row_index_lock:
            if row_index >= len(combined_df):
                break
            
            row = combined_df.iloc[row_index]
            row_index += 1

        user_id = row["Primary Identifier"]
        barcode = row["Barcode"]
        item_policy = row["Item Policy"]
        location = row["Temporary Location Name"] if row["Temporary Physical Location In Use"] == "Yes" else row["Location Name"]
        user_group = row["User Group"]

        def load_user():
            nonlocal current_user_id
            try:
                user_menu = safe_find_element(driver, By.ID, "PICKUP_ID_pageBeandisplayNameOfUserOrUserIdendifier")
                user_menu.click()

                modal = safe_find_element(driver, By.CLASS_NAME, "modal")
                driver.switch_to.frame(driver.find_element(By.ID, "iframePopupIframe"))

                search_button = safe_find_element(driver, By.ID, "simpleSearchIndexButton")
                search_button.click()

                time.sleep(2)
                primary_identifier_link = safe_find_element(driver, By.XPATH, "//li[@id='TOP_NAV_Search_index_HFrUser.user_name']//a[text()='Primary identifier']")
                primary_identifier_link.click()

                input_field = safe_find_element(driver, By.ID, "ALMA_MENU_TOP_NAV_Search_Text")
                input_field.send_keys(user_id)
                
                search_button = safe_find_element(driver, By.ID, "simpleSearchBtn")
                search_button.click()

                row_el = safe_find_element(driver, By.XPATH, "//table[@id='TABLE_DATA_userList']/tbody/tr")
                row_el.click()
                time.sleep(4)
                current_user_id = user_id
                print(driver.page_source)
            except Exception as e:
                print(f"Thread-{thread_id} error switching user: {e}")

        if user_id != current_user_id:
            load_user()

        try:
            
            print(f"Processing item {barcode} - {item_policy} - {location}")
            send_keys_with_retry(driver, By.XPATH, "//input[@id='pageBeanbarcode']", barcode)
            click_element_with_retry(driver, By.ID, "cbuttonok")

            loan_result = get_table_html_with_retry(driver, By.ID, "TABLE_DATA_policiesList", "loan")
            
            request_result = get_table_html_with_retry(driver, By.ID, "TABLE_DATA_policiesList", "request")
            loan_result_policy_dict = loan_result[2]
            request_result_policy_dict = request_result[2]

            if row_index == 0:
                global order_of_loan_policy_columns, order_of_request_policy_columns
                order_of_loan_policy_columns = list(loan_result_policy_dict.keys())
                order_of_request_policy_columns = list(request_result_policy_dict.keys())

            # Create initial row dict with static values first
            row_dict = {
                "User ID": user_id,
                "User Group": user_group,
                "Barcode": barcode,
                "Item Policy": item_policy,
                "Location": location,
                "Fulfillment Unit Name": loan_result[3],
                "Fulfillment Rule (Loan)": loan_result[0],
                "TOU (Loan)": loan_result[1],
                "Fulfillment Rule (Request)": request_result[0],
                "TOU (Request)": request_result[1]
            }
            # Now safely add policy values
            row_dict.update(loan_result_policy_dict)
            row_dict.update(request_result_policy_dict)

            # Reorder the policy columns using the column order
            # ordered_loan_dict = {col: row_dict.get(col, "") for col in order_of_loan_policy_columns}
            # ordered_request_dict = {col: row_dict.get(col, "") for col in order_of_request_policy_columns}

            # # Re-apply reordered keys to the final row dict
            # row_dict.update(ordered_loan_dict)
            # row_dict.update(ordered_request_dict)

            buffer.append(row_dict)

            
        except Exception as e:
            print(f"Thread-{thread_id} failed to process item {barcode}: {e}")
            print(f"Thread-{thread_id} attempting recovery...")

            # Try to reload the page and reset the user
            navigate_to_checkout()
            load_user()

        if len(buffer) >= BUFFER_WRITE_INTERVAL:
            write_buffer_to_excel(buffer, thread_id, OUTPUT_DIR)
            buffer.clear()

    if buffer:
        write_buffer_to_excel(buffer, thread_id, OUTPUT_DIR)
    
    driver.quit()
    print(f"Thread-{thread_id} finished.")

def cross_join(df1, df2):
    df1["key"] = 1
    df2["key"] = 1
    return pd.merge(df1, df2, on="key").drop("key", axis=1)

def main():
    global row_index
    combined_df = cross_join(user_group_data, item_policy_data)
    combined_df = combined_df.sort_values(by=["Primary Identifier", "Location Name", "Item Policy"])

    if os.path.exists(OUTPUT_DIR) and os.listdir(OUTPUT_DIR):
        
        row_index, start_thread_id = retrieve_current_row_index(OUTPUT_DIR)
        print("previous analysis in progress.  start at row " + str(row_index) + " in the combined item policy/user group/location sheet\n")
    else:
        start_thread_id = 0

    threads = []
    for i in range(N):
        thread_id = start_thread_id + i
        print("thread id" + str(thread_id) + "\n")
        t = threading.Thread(target=worker_thread, args=(thread_id, combined_df))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    final_df = merge_excel_files(start_thread_id + N, OUTPUT_DIR)
    final_df.to_excel(instance + " - " + OUTPUT_FILE, index=False)

    highlight_unique_values(OUTPUT_FILE, instance + " - " + OUTPUT_FILE)
    print("All threads complete.")

if __name__ == "__main__":
    main()
