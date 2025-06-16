# Bulk Loan Rule Simulator
- The goal of this script is to allow you to completely automate the testing of all possible fulfillment unit rule scenarios at your institution captured by your fulfillment unit rules (loan and request)
- this way after changes are made to item records that could affect loan rule behavior, such as changes to item policies, or item locations, every single scenario can be tested automatically so you can be sure no changes come as a result, or only desired changes

## Install and Run
- Once downloaded, install requirements from within directory
  - python3 -m pip install -r requirments.txt
  - OR
  - python pip install -r requirements.txt

  
## Input
- gather your unique item policy and location combinations, by using a report suchn as this: 	/shared/Community/Reports/Institutions/Tufts University/	Item Policy and Item Location Combinations with At Least 1 Active Item
-   - Export as Excel
    - this file picks one examplar barcode from every unqiue item policy/location combination that has items
- Also create a user group Excel file
-   - we only have 4 or 5 meaningful groupings of users, and one can be picked to represent each
    - should have these columns
      - User Group
      - Primary Identifier
- put these in the following following folders
  - input/Item Policies and Locations
  - input/User Groups 

## Set Up
- change the secrets_local_example.py file in the config folder to have real API keys etc, and change its name to secrets_local.py
## Operation

- `python3 bulkTest.py`
- this program uses multithreading, and you can choose either 1, 2, or 3 threads depending on how robust your internet connection is
- the outputs will be aware of the which particular loan rule scenario is being tested by other threads, so they will all work together to increase the speed of operation
- the output will be gathered at the end into the main folder and the results highlighted for changes in the invoked Fulfillment Unit rules
- you can then sort and analyze this to 

# Loan Rule Report Generator


## Purpose
- drill out fulfillment unit loan rules, locations, and associated Terms of Use and policies from your Alma config

## Method
- uses Python Selenium and pandas
- like bulkTest.py it also uses multithreading
- the otu

## Install and Run

- create an Alma internal user with the role Fulfillment Adminstrator for your instituion, with password
- enter the above Alma user Primary ID, password, and your institution URL in the secrets_local.py file
- run
  - python3 getLoanRules.py
    - note that you'll need to close the GDPT cookie rules as soon as Selenium authenticates in Alma. The rest will run autonomously
  - let script run through all the loan rule


## Output
- rules for each fulfillment unit with associated parameters, TOUs, and policies will aggregate

