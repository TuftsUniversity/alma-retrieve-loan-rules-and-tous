import csv
import sys
import time
import os
import time
import pandas as pd
import numpy as np
import glob
import re


############################################################
############################################################
########    goal: make the drilled out loan rule data more
########    readable for CRT
########
########    method (1st refinement):
########        - roll up loan with parameters spread across multiple lines
########        so that all of these appear on 1 line
########
########    method (2nd refinement):
########        - group rows where the loan rule information is the same,
########        particularly rule name
########        - as part of this grouby function, I can combine the columns that
########          contain parameters
########        - for this use apply()
########          e.g. df.groupby('team').apply(lambda x: x['team'].count() / df.shape[0])


oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)


def mergeAndPresent(rule_df):


    x = 0
    rule_df = rule_df.reset_index()
    rule_df = rule_df.fillna("None")
    rule_df = rule_df.drop(['Overdue Notification Fine Type 1', 'Overdue Notification Fine Type 2', 'Overdue Notification Fine Type 3', 'Overdue Notification Fine Type 4', 'Overdue Notification Fine Type 5'], axis=1)
    #print(rule_df)
    rule_df.loc[rule_df['Operator'] == 0, 'Operator'] = "Equals"
    while x < len(rule_df):

        # print(rule_df.shape)
        # print(rule_df)
        # sys.exit()
        # if rule_df.iloc[x]['Unnamed: 0'] == 1:
        columns_to_apply_list = ["Is Loanable", "Is Recallable", "Due Date", "Requested Item Due Date", "Recall Period", "Renew Fee", "Lost Item Fine", "Lost Item Replacement Fee", "Lost Item Replacement Fee Refund Ratio", "Maximum Fine", "Overdue Fine", "Recalled Overdue Fine", "Grace Period", "Is Renewable", "Maximum Renewal Period", "Closed Library Due Date Management", "Cancelled Recall Due Date", "Block When Overdue", "Maximum Period For Overdue Block", "Reloan Limit", "Time frame when loan renewal is allowed"]

        # part of this row of the dataframe with TOU columns and values
        columns_to_apply = rule_df.loc[x, rule_df.columns.isin(columns_to_apply_list)]

        # part of this row of the dataframe that has the loan rule information
        # not used
        #match_columns = rule_df.loc[x, ~rule_df.columns.isin(columns_to_apply_list)]





        rule_name = rule_df.loc[x, 'Rule Name']
        # print("Rule df in merge script")
        # print(rule_df)
        # sys.exit()

        #broadcast the TOUs in each row where the rule name matches this
        change_rule_df = rule_df.loc[rule_df['Rule Name'] == rule_name]
        change_rule_df[columns_to_apply_list] = columns_to_apply.values

        #now integrate these changes back into the master dataframe
        rule_df.update(change_rule_df)

        if rule_name == "End of Day All Patrons Ginn Laptops":


            rule_df = rule_df.drop_duplicates(subset=['Rule Name', 'Value'])

        x += 1






    rule_df = rule_df.drop(['Unnamed: 0', 'Unnamed: 4'], axis=1)
    rule_df['Parameter'] = rule_df['Name'].astype('string') + " " + rule_df["Operator"].astype('string') + " " + rule_df['Value'].astype('string')

    print("Rule df in merge with parameter column")
    print(rule_df)



    #wrap up multiple lines for each loan rule, and join the separte parameters into a list
    columns_to_apply_list_master = ['Fullfilment Unit', 'Possible Locations', 'Rule Name', 'Output', "Is Loanable", "Is Recallable", "Due Date", "Requested Item Due Date", "Recall Period", "Renew Fee", "Lost Item Fine", "Lost Item Replacement Fee", "Lost Item Replacement Fee Refund Ratio", "Maximum Fine", "Overdue Fine", "Recalled Overdue Fine", "Grace Period", "Is Renewable", "Maximum Renewal Period", "Closed Library Due Date Management", "Cancelled Recall Due Date", "Block When Overdue", "Maximum Period For Overdue Block", "Reloan Limit", "Time frame when loan renewal is allowed"]
    rule_df['Parameter'] = rule_df.groupby(columns_to_apply_list_master, dropna=False)['Parameter'].transform(lambda x: ';'.join(x))

    rule_df = rule_df.drop_duplicates(subset=['Rule Name'])

    print(rule_df)
    return rule_df
    # # print(rule_df)
    # sys.exit()
    # print(filename)
    #
    # #rule_df = rule_df[rule_df['Is Loanable'] != "None"]
    # filename = filename.replace('Output', 'Merged')
    # print(filename)
    #
    # rule_df.to_excel(filename, index=False)
