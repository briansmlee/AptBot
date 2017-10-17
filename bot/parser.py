# by Seungmin Lee
# parses APT Groups and Operations data from apt.xlsx
# to provide easy access to backend

import openpyxl as xl
import pandas as pd
import pickle


def parse_apt():
    """ parses APT data to a list of APT groups

    example of an APT group in the list:

    [{
    names: "comment_crew, GIF89a, ShadyRAT, Shanghai Group, Byzantine Candor"
    country: "China"
    tools: "WEBC2, BISCUIT and many others",
    targets: "Mainly EN speaking countries; IT/Software companies; Financial Institutions",
    operations: "Shady RAT",
    ... (other information)}
    ... (other groups)
    ]
    """

    def parse_sheet(sheet, sheetname):
        """helper to parse dataframe sheet argument to a group dict"""

        # set col names
        sheet.columns = sheet.iloc[0]
        sheet = sheet[2:]

        for _, row in sheet.iterrows():
            group = {}
            group['country'] = sheetname
            group['names'], group['operations'] = [], []

            # iterate over each col to fill matching attrs
            for col_name in row.index:
                if pd.isnull(col_name) or pd.isnull(row[col_name]):
                    continue
                val = row[col_name]

                # for each column, parse column title and value
                if 'Name' in col_name and not val.startswith('?'):
                    group['names'].append(val)
                elif col_name == 'Toolset / Malware':
                    group['tools'] = val.split(',')
                elif col_name == 'Targets':
                    group['targets'] = val.split(',')
                elif 'Operation' in col_name:
                    group['operations'].append(val)
                else:  # if no match, add as extra info
                    group[col_name] = val

            if not group['operations']:  # remove if no ops
                group.pop('operations', None)

            groups.append(group)

    path = '../data/APT.xlsx'
    groups = []

    # parse each sheet in workbook using helper
    book = xl.load_workbook(path)
    for sheetname in book.sheetnames:
        if sheetname != 'Home' and sheetname[0] != '_':
            sheet = pd.read_excel(path, sheetname=sheetname)
            parse_sheet(sheet, sheetname)

    return groups

if __name__ == "__main__":
    groups = parse_apt()
    with open('../data/APT_dict.pkl', 'wb') as f:
        pickle.dump(groups, f)
    # pprint(groups)




