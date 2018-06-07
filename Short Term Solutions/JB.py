import numpy as np
import pandas as pd
import re


def jb_solver(file_path):
    df = pd.read_excel(file_path)
    df = df[pd.notnull(df['Currency'])]
    df['Debit'].fillna(0, inplace=True)
    df['Credit'].fillna(0, inplace=True)
    output_list = [pd.DataFrame([
                       ['Action', 'CcyAccountCode', 'TradeDate', 'ValueDate', 'Narration', 'Amount', 'TrasactionType',
                        'Ticker', 'Quantity', 'Price', 'DirtyPrice', 'HashTags', 'Currency']])]
    for row in df.itertuples():
        temp_list = ['CreateTransaction']
        temp_list.append('cnp489912-jbsg-6777025-{}-01'.format(row[8].lower()))
        temp_list.extend([row[2], row[4], row[3]])
        temp_list.append(float(row[6]) - float(row[5]))
        temp_list.extend(jb_text_classifier(row[3], temp_list[5], temp_list[1]))
        temp_list.extend([np.nan, np.nan, np.nan, np.nan])
        temp_list.append(row[8])
        output_list.append(pd.DataFrame([temp_list]))
    output_df = pd.concat(output_list)
    return output_df


def jb_text_classifier(narration, amount, ac_number):
    word_list = extract_cap_word(narration)
    temp_decision = []
    temp_ticker = []
    if 'repayment' in word_list:
        temp_decision.append('LoanRepay')
        temp_ticker.append(loan_ticker_generator(narration, ac_number))
    elif 'dividend' in word_list:
        if amount < 0:
            temp_decision.append('Contribution')
        elif amount > 0:
            temp_decision.append('Distribution')
        else:
            temp_decision.append('Manual Input Required')
    elif 'interest' in word_list and 'loan' in word_list:
        temp_decision.append('LoanCost')
        temp_ticker.append(loan_ticker_generator(narration, ac_number))
    elif 'payment' in word_list and 'loan' in word_list:
        temp_decision.append('LoanCreate')
        temp_ticker.append(loan_ticker_generator(narration, ac_number))
    elif 'coupon' in word_list and 'payment' in word_list:
        temp_decision.append('Distribution')
        temp_ticker.append(structured_dcps_ticker_generator(narration))
    elif 'capital' in word_list and 'gain' in word_list:
        temp_decision.append('Distribution')
        temp_ticker.append(structured_dcps_ticker_generator(narration))
    elif 'purchase' in word_list:
        temp_decision.append('Purchase')
        temp_ticker.append(structured_dcps_ticker_generator(narration))
    elif 'miscellaneous' in word_list and 'income' in word_list:
        temp_decision.append('MiscIncome')
    elif 'investment' in word_list:
        if amount < 0:
            temp_decision.append('Purchase')
        elif amount > 0:
            temp_decision.append('Sale')
        else:
            temp_decision.append('Manual Input Required')
    elif 'forex' in word_list:
        if amount < 0:
            temp_decision.append('SpotFxOut')
        elif amount > 0:
            temp_decision.append('SpotFxIn')
        else:
            temp_decision.append('Manual Input Required')
    else:
        pass

    if len(temp_decision) != 1:
        temp_decision = ['Manual Input Required']
    if len(temp_ticker) != 1:
        temp_ticker = [np.nan]
    return [temp_decision[0], temp_ticker[0]]


def extract_cap_word(input_s):
    output = [i.lower() for i in re.split(' |-', input_s) if i.isupper()]
    return output


def ticker_generator(narration, ac_number, transaction_type):
    if transaction_type == 'LoanCost' or transaction_type == 'LoanCreate' or transaction_type == 'LoanRepay':
        contract_no = narration.split('|')[0].split('Contract No: ')[1].split('-')[1]
        return 'LoanRef_{}_{}'.format(ac_number, contract_no)
    elif (transaction_type == 'Distribution' or transaction_type == 'Contribution'
          or transaction_type == 'Sale' or transaction_type == 'Purchase'):
        return 'Check Server Function'

    pass


def loan_ticker_generator(narration, ac_number):
    contract_no = narration.split('|')[0].split('Contract No: ')[1].split('-')[1]
    return 'LoanRef_{}_{}'.format(ac_number, contract_no)


def structured_dcps_ticker_generator(narration):  # distribution,contribution,purchase,sale
    security_no = narration.split('|')[0].split('Security No: ')[1]
    currency_format = r'(\s[A-Z]{6}\s)'
    matches = re.finditer(currency_format, narration)
    currency = []
    for num, match in enumerate(matches):
        currency.append('{}/{}'.format(match.group()[1:4], match.group()[4:7]))
    output = 'STRUCTUREDPRODUCT_{}_{}'.format(currency[0], security_no)
    return output

#RUN FILE
raw_file = r'C:/Users/Justin Leung/Documents/Github/text_classification/Short Term Solutions/Data Files/jb_raw_statement.xlsx'
result = jb_solver(raw_file)
save_path = r'C:/Users/Justin Leung/Documents/Github/text_classification/Short Term Solutions/Data Files/jb_raw_statement_processed.xlsx'
print('Normalising File..')
writer = pd.ExcelWriter(save_path)
result.to_excel(writer, 'Sheet1', index=False, header=False)
writer.save()
