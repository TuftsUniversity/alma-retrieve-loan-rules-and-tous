import pandas as pd
from tkinter.filedialog import askopenfilename
import glob
import os
import sys
import re
# Function to parse parameters from the 'Parameter' column and extract 'Location', 'Item Policy', and 'User Group'


def convert(parameter):


    parameter_name = re.search(r'^(Location|User Group|Item Policy)', parameter).group(1)

    operator = re.search(r'^(Location|User Group|Item Policy)\s*(=|In List|Is Empty|Is Not Empty|Not Equals|Not In List|Contains)', parameter).group(2)

    values = re.search(r'^(Location|User Group|Item Policy)\s*(=|In List|Is Empty|Is Not Empty|Not Equals|Not In List|Contains)(.+)$', parameter).group(3)
    parameter = parameter_name + ": " + str(operator) + "(" + values + ")"



    return parameter
def parse_parameter_with_user_group(parameter_str):
    location, item_policy, user_group = None, None, None

    try:



        parameters = parameter_str.split(';')



        for param in parameters:
            if param.strip().startswith("Location"):
                location = param.strip()

                location = convert(location)


            elif param.strip().startswith("Item Policy"):
                item_policy = param.strip()
                item_policy = convert(item_policy)
            elif param.strip().startswith("User Group"):
                user_group = param.strip()
                user_group = convert(user_group)




    except:
        result = "no parameters"

    return location, item_policy, user_group
# Function to extract and convert the row number prefix to an integer or return None if invalid
def extract_and_convert_row_number_prefix_safe(value):
    if pd.isna(value) or ":" not in value:
        return None
    return int(value.split(":")[0])

# Sorting rows and columns by the lowest integer prefix, ignoring cells without a valid prefix
def sort_rows_by_lowest_integer_prefix_safe(pivot_table):
    sort_values = pivot_table.apply(lambda row: min(
        [extract_and_convert_row_number_prefix_safe(val) for val in row if extract_and_convert_row_number_prefix_safe(val) is not None],
        default=float('inf')), axis=1)
    return pivot_table.reindex(sort_values.sort_values().index)

def sort_columns_by_lowest_integer_prefix_safe(pivot_table):
    sort_values = pivot_table.apply(lambda col: min(
        [extract_and_convert_row_number_prefix_safe(val) for val in col if extract_and_convert_row_number_prefix_safe(val) is not None],
        default=float('inf')), axis=0)
    return pivot_table[sort_values.sort_values().index]

# Constants for column names corresponding to "I" through "X" in the Excel file
columns_ix_names = ['Is Loanable', 'Is Recallable', 'Due Date', 'Requested Item Due Date', 'Recall Period',
                    'Renew Fee', 'Lost Item Fine', 'Lost Item Replacement Fee', 'Lost Item Replacement Fee Refund Ratio',
                    'Maximum Fine', 'Overdue Fine', 'Recalled Overdue Fine', 'Grace Period', 'Is Renewable',
                    'Maximum Renewal Period', 'Closed Library Due Date Management']

# Load the data

# Load the data
#filename = askopenfilename(title="select the fulfillment unit sheet you'd like to parse")
oDir = "./Output Visualized"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)


files = glob.glob('Output/*', recursive = True)


y = 0
for y in range(0, len(files)):
    filename = files[y]
    if filename == "Output" or filename == "Loan Rules":
        continue
    print(filename)

    filename_base = re.sub(r'.+?([^\\]+)\.xlsx$', r'\1', filename)

    df_full = pd.read_excel(filename, usecols=['Parameter', 'Due Date'] + columns_ix_names, engine='openpyxl')
    #df_full['Parameter'] = df_full['Parameter'].fillna("None")
    df_full[['Location', 'Item Policy', 'User Group']] = df_full.apply(
        lambda row: pd.Series(parse_parameter_with_user_group(row['Parameter'])), axis=1
    )
    # pd.set_option('display.max_columns', None)
    # print(df_full)
    #
    # sys.exit()
    #df_full.loc[df_full['Location'] == "None", 'Location'] == "Location: None"
    df_full['Location_User_Group'] = df_full['Location'] + " - " + df_full['User Group']

    # print(df_full)
    #
    # sys.exit()
    # Create pivot tables for each column and apply the updated sorting
    writer = pd.ExcelWriter(oDir + '/' + filename_base + ' - Visualized.xlsx', engine='xlsxwriter')
    for column in columns_ix_names:
        df_full[f'{column}_with_row'] = df_full.index.to_series().apply(lambda x: f"{x+1}: ") + df_full[column].astype(str)

        pivot_table = df_full.pivot_table(
            index='Location_User_Group',
            columns='Item Policy',
            values=f'{column}_with_row',
            aggfunc='first'
        )

        # print(df_full)
        # print(pivot_table)
        # sys.exit()


        pivot_table_sorted_rows = sort_rows_by_lowest_integer_prefix_safe(pivot_table)
        pivot_table_sorted_both = sort_columns_by_lowest_integer_prefix_safe(pivot_table_sorted_rows)
        pivot_table_sorted_both.to_excel(writer, sheet_name=column[:31])
        # 
    # print(pivot_table)


    # Save the Excel file
    writer.close()


    # Read and store data from each sheet

    workbook = pd.ExcelFile(oDir + '/' + filename_base + ' - Visualized.xlsx')


    data_sheets = {sheet_name: pd.read_excel(workbook, sheet_name=sheet_name) for sheet_name in workbook.sheet_names}
    workbook.close()
    import os


    #os.remove(oDir + '/' + filename_base + ' - Visualized.xlsx')
    # Write data to a new workbook
    new_writer = pd.ExcelWriter(oDir + '/' + filename_base + ' - Visualized.xlsx', engine='xlsxwriter')
    for sheet_name, df in data_sheets.items():
        df.to_excel(new_writer, sheet_name=sheet_name, index=False)
    new_writer.close()
    y += 1
