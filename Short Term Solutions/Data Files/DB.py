import numpy as np
import pandas as pd
import re


def db_solver(file_path):
    r_df = pd.read_excel(file_path)
    f_col_df = r_df[r_df.columns[0]]
    account_df = r_df[r_df.columns[r_df.shape[1] - 1]].copy()
    output_list = []
    for row in f_col_df.iteritems():
        splitted_list = re.sub('\s\s\s+', '^?', row[1], 4).strip().split('^?')
        deb_cred_col = splitted_list[-1]
        spaces = deb_cred_col.count(' ') - re.sub('\s\s\s+', '', deb_cred_col).count(
            ' ')  # space > 45 credit, space < 45 debit
        splitted_list = re.sub('\s\s\s+', '^?', row[1]).strip().split('^?')
        regex = r'^(\-?)(\d?\d?\d(,\d\d\d)*|\d+)(\.\d\d)?'
        match = re.match(regex, splitted_list[5])
        balance = match.group()
        description = splitted_list[5][len(match.group()):].replace('\n', ' ')[1:]
        try:
            splitted_list[1] = ' '.join([splitted_list[1], description])
        except:
            pass
        splitted_list[-1] = balance
        if spaces < 45:
            splitted_list.insert(4, np.nan)
        else:
            splitted_list.insert(5, np.nan)
        output_list.append(pd.DataFrame([splitted_list]))
    output_df = pd.concat(output_list)
    output_df = output_df.reset_index(drop=True)
    output_df.columns = ['Trade Date', 'Description', 'Value Date', 'Reference', 'Debit', 'Credit', 'Balance']
    output_df['Account Number'] = account_df
    return output_df


def db_ul(df):
    debit = df['Debit'].astype(str).str.replace(',','').astype(float).fillna(0).copy()
    credit = df['Credit'].astype(str).str.replace(',','').astype(float).fillna(0).copy()
    df['Debit'] = debit
    df['Credit'] = credit
    #df['Credit'] = df['Credit'].astype(str).apply(lambda x: x.str.replace(',','')).fillna(0)
    output_list = [pd.DataFrame([
                       ['Action', 'CcyAccountCode', 'TradeDate', 'ValueDate', 'Narration', 'Amount']])]
    for row in df.itertuples():
        temp_list = []
        list_of_narration = [i.lower() for i in row[2].split(' ')]
        if 'structured' in list_of_narration and 'product' in list_of_narration:
            temp_list_blank = [np.nan,np.nan,row[1],row[3],np.nan,(float(row[6])-float(row[5]))]
            temp_list = ['CreateTransaction',row[-1],row[1],row[3],' '.join([row[2],'Ref:',row[4]]),0]
            output_list.append(pd.DataFrame([temp_list_blank]))
            output_list.append(pd.DataFrame([temp_list]))
        else:
            temp_list = ['CreateTransaction',row[-1],row[1],row[3],' '.join([row[2],'Ref:',row[4]]),(float(row[6])-float(row[5]))]
            output_list.append(pd.DataFrame([temp_list]))
    output_df = pd.concat(output_list)
    return output_df

def sca_db():
    df = db_ul(db_solver(r"C:\Users\Justin Leung\Downloads\6006902.01_SCA_Apr18.xlsx"))
    writer = pd.ExcelWriter(r"C:\Users\Justin Leung\Downloads\6006902.01_SCA_Apr18_processed.xlsx")
    df.to_excel(writer,'Sheet1',header=False,index=False)
    writer.save()
    return ("DONE")

file = r"C:\Users\Justin Leung\Downloads\6006902.01_Statement_Apr18.xlsx"
df = pd.read_excel(file)
