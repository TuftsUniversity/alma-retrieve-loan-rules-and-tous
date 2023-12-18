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
- new in 2023
  - The application now installs a current version of the chromedriver if yours is out of date.
  - If you get an error message "[WinError 5] Access is denied" You probably have a chromedriver running.  Go to Ctrl + Alt + Delete and end this process
  - If you want to download a different version of the Chromedriver follow the steps below
- download and instal, unzip, and place version of Chromedriver.exe that matches your version of Chrome from https://chromedriver.chromium.org/downloads and place in your user home directory.  Note that Chrome updates frequently so if you don't use this script often you may have to download a new version of the Chromedriver
- run
  - python3 getLoanRules.py
    - note that you'll need to close the GDPT cookie rules as soon as Selenium authenticates in Alma. The rest will run autonomously
  - let script run through all the loan rules
  - new in 2023
	- the visualize.py script organizes the loan rule table you specify from the output above and makes a version where each TOU policy value is plotted in a pivot table in a cross section of the user and location parameters, against item poliy parameters.  The number of the loan rule is next to the value so you can see in what order it's invoked in the cascading rule evaluation
    - this script uses the output of the previous script in the "Output" folder as input


*Output:*
- rules for each fulfillment unit with associated parameters, TOUs, and policies will be in separate workbooks by fulfillment unit name in the Output folder
- once you run the visualized.py script, results will be in "Output Visualized"  
