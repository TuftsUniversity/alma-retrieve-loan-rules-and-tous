# alma-retrieve-loan-rules-and-tous

Author: Henry Steele, Library Technology Services, Tufts University, 2023

*Purpose:*
- drill out fulfillment unit loan rules, locations, and associated Terms of Use and policies from your Alma config

*Method:*
- uses Python Selenium and pandas

*Install and Run:*
- Once downloaded, install requirements from within directory
  - python3 -m pip install -r requirments.txt
  - OR
  - python pip install -r requirements.txt
- create an Alma internal user with the role Fulfillment Adminstrator for your instituion, with password
- enter the above Alma user Primary ID, password, and your institution URL in the secrets_local.py file
- download and instal, unzip, and place version of Chromedriver.exe that matches your version of Chrome from https://chromedriver.chromium.org/downloads and place in your user home directory.  Note that Chrome updates frequently so if you don't use this script often you may have to download a new version of the Chromedriver
- run 
  - python3 getLoanRules.py
  - let script run through all the loan rules

*Output:*
- rules for each fulfillment unit with associated parameters, TOUs, and policies will be in separate workbooks by fulfillment unit name in the Output folder



