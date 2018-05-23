import xlrd
import numpy as np
import pandas as pd
from itertools import compress
import xlsxwriter
import re

csv_file_path = "tabula-Apr_2018_Portfolio_D2_xxxxPWSA__CANOPY_.csv"
processed_file_path = "AHC_2_processed.xlsx"


def AHC_solver(csv_file):
    def read_csv_bad_col(csv_file):
        length_of_file = 2
        loop = True
        while loop:
            try:
                output_csv = pd.read_csv(csv_file,names=list(range(1,length_of_file)),engine='python')
                loop = False
            except:
                length_of_file += 1
        return output_csv
    def equalindex(df,row,key_word):
        footer_index = df.iloc[:,row] == key_word
        footer = (np.sort(df.index[footer_index])).tolist()
        return footer
    def containindex(df,row,key_word):
        footer_index = df.iloc[:,row].str.contains(key_word).fillna(False)
        footer = (np.sort(df.index[footer_index])).tolist()
        return footer
    '''
    def solver(df,max_col):
        footer_1 = equalindex(df,0,"INVESTMENT INCOME")
        df_1 = df[0:footer_1]    
        #footer_2_index = df.iloc[:,6].str.contains('Unrealised Gain').fillna(False)
        #footer_2 = int(np.sort(df.index[footer_2_index])) #27
        footer_2 = containindex(df,6,"Unrealised Gain")
        df_2_pre = df[footer_1:footer_2]
        for i in range(1,max_col):
            if df.loc[footer_1,i] == 'N1':
                df_2_split_index = i #5
        df_2 = df_2_pre.iloc[:,0:(df_2_split_index-1)].copy()
        df_3 = df_2_pre.iloc[:,(df_2_split_index-1):max_col]
        footer_4 = equalindex(df,3,"Cost Total")
        df_4 = df[footer_2,footer_4]
        
        return df_4
    '''
    def unrealised_solver(df):
        df = df.reset_index()
        header_index = df.iloc[:,2].str.contains("% of Total Book Value").fillna(False)
        header = np.sort(df.index[header_index]).tolist()
        df.insert(loc=3,column='new',value=pd.Series([np.nan]))
        df.iloc[:,3] = df.iloc[:,2].str.split(' ').str.get(1)
        df.iloc[:,2] = df.iloc[:,2].str.split(' ').str.get(0)#.convert_objects(convert_numeric=True)
        #df.iloc[:,2] = df.iloc[:,2].str.replace(',','')
        ori_index = df.loc[header,'index']
        df.loc[header,0:6] = ori_index,np.nan,'Book Value', "% of Total Book Value","Market Value","% of Total Market Value"       
        df = df.set_index('index')
        row,col = df.shape
        df.columns = list(range(1,col+1))
        return df
    def total_solver(df):
        index_t = df.iloc[:,2] == "Total"
        list_index = (np.sort(df.index[index_t])).tolist()
        if len(list_index) == 0: #No total, total holdings:            
            df = df.reset_index()
            df = df.drop(df.columns[2],axis =1)
            df.insert(loc=4,column='new',value=pd.Series([np.nan]))
            row_to_split = (df.iloc[:,3].str.replace(',','').str.split(' '))
            for i in row_to_split:
                if type(i) is list:
                    if len(i) == 1:
                        i = i.insert(0,np.nan)
                        #print('executed')
                    else:
                        pass
                else:
                    pass
            df.iloc[:,4] = row_to_split.str.get(1)
            df.iloc[:,3] = row_to_split.str.get(0)
            ori_index = df['index'][2]
            #print(ori_index)
            #print(df)
            df.loc[2,0:5] = ori_index,np.nan,np.nan,'Per Unit','Book Value'
            df = df.set_index('index')
            row,col = df.shape
            df.columns = list(range(1,col+1))

            #print(df)
            return df
        else:
            return df
    def nominal_solver(df):
        df = df.reset_index()
        df = df.drop(df.columns[2],axis=1)
        df.insert(loc=8,column='new',value=pd.Series([np.nan]))        
        row_to_split = (df.iloc[:,7].str.replace(',','').str.split(' '))
        first = True
        for i in row_to_split:
            if type(i) is list:
                if len(i) == 1:
                    pass
                else:
                    #print(df)
                    ori_index = df['index'][0]
                    df.iloc[:,8] = row_to_split.str.get(1)
                    df.iloc[:,7] = row_to_split.str.get(0)
                    df.loc[0,0:9] = ori_index,'Stock Security Description','Nominal','Coupon','Maturity Date','Pur.','Avg. Cost','Cost','Book Value'
                    first = False
            else:
                pass
        if first:
            df = df.drop(df.columns[8],axis = 1)
        else:
            df = df.drop(df.columns[9],axis = 1)
        df = df.set_index('index')
        row,col = df.shape
        df.columns = list(range(1,col+1))
        return df
    def counterparty_solver(df):
        df = df.reset_index()
        row_to_split = df.iloc[:,1].str.replace(',','')
        currency = []
        value = []
        value1 = []
        value2 = []
        for i in row_to_split:            
            split = re.search(r'([\D]+)([0-9,.]+)',i)
            if (split) is not None:                
                value.append(split.group(2))
                currency.append(split.group(1))
                df.iloc[:,1] = np.nan
            else:
                value.append(np.nan)
                currency.append(i)
        df.iloc[:,3] = pd.Series(value)
        df.iloc[:,2] = pd.Series(currency)
        for i in df.iloc[:,2].str.replace('',''):
            if len(i.split('\n')) == 2:
                if (i.split('\n'))[1] != '':
                    df.iloc[1,1] = i.split('\n')[0]
                    df.iloc[1,2] = i.split('\n')[1]
        for i in df.iloc[:,3].str.replace('',''):
            splitted = []
            if i is None:
                value1.append(np.nan)
                value2.append(np.nan)
            elif type(i) is float:
                value1.append(np.nan)
                value2.append(np.nan)
            else:
                for char in i:
                    splitted.append(char)
                occurences = [i for i,x in enumerate(splitted) if x == '.']
                if len(occurences) == 1:
                    value1.append(np.nan)
                    value2.append(i) 
                else:
                    value1.append(''.join(splitted[0:occurences[0]+3]))
                    value2.append(''.join(splitted[occurences[0]+3:])) 
        value1_s = pd.to_numeric(pd.Series(value1),errors='ignore')
        value2_s = pd.to_numeric(pd.Series(value2),errors='ignore')
        print (df.shape) #(16,18)
        #print(df)
        if df.shape[1] < 16:
            #print('run')
            df.insert(loc=df.shape[1],column='new',value=pd.Series([np.nan]))
        #print(df)
        try:
            df.iloc[:,13] = pd.to_numeric(df.iloc[:,13].str.replace(',',''),errors='ignore')
        except:
            df.iloc[:,13] = pd.to_numeric(df.iloc[:,13],errors='ignore')
        try:
            df.iloc[:,14] = pd.to_numeric(df.iloc[:,13].str.replace(',',''),errors='ignore')
        except:
            df.iloc[:,14] = pd.to_numeric(df.iloc[:,13],errors='ignore')
        df.iloc[:,15] = df.iloc[:,14].add(value2_s,fill_value=0)
        df.iloc[:,14] = df.iloc[:,13].add(value1_s,fill_value=0)
        df.iloc[:,13] = pd.Series([np.nan])


        index_head = df['index'][0]
        df.iloc[:,3] = pd.Series([np.nan])
        df.loc[0,0:16] = index_head, 'Counterpart Type','Counterpart','Placement Date','Local Ccy', r'Placement Amount (local Ccy)', r'Period (Days)', 'Maturity Date', r'Rate(%)', r'Maturity Amount (Local Ccy)', r'Interest To Maturity (Local Ccy)',r'Accured Inerest (Base Ccy)', 'Accured Days', r'Day(s) To Maturity', r'Market Value (Local Ccy)', r'Market Value (Base Ccy)'
        df = df.set_index('index')
        row,col = df.shape
        df.columns = list(range(1,col+1))                              
        return df
            
    def comma_remove(df):
        row,col = df.shape
        for col in df.select_dtypes([np.object]).columns[1:]:
            df[col] = df[col].str.replace(',','')
        #for i in range(2,col):
           #df.iloc[:,i] = df.iloc[:,i].str.replace(',','')
        return df
        
    def solver(df):
#getting footers
        row,col = df.shape
        doublecheck_dict = {}
        order_of_element = []
        footer_lists = [0,row]
        footer_1 = equalindex(df,0,"INVESTMENT INCOME")
        if footer_1 != 0:
            doublecheck_dict["Table before investment"] = [0]
            order_of_element.append("Table before investment")
        footer_lists += footer_1
        if len(footer_1) != 0:
            doublecheck_dict["INVESTMENT INCOME"] = footer_1
            order_of_element.append("INVESTMENT INCOME")
        footer_2 = containindex(df,6,"Unrealised Gain")
        footer_lists += footer_2
        if len(footer_2) != 0:
            doublecheck_dict["Unrealised Gain"] = footer_2
            order_of_element.append("Unrealised Gain")
        footer_3 = containindex(df,2,"Total")
        footer_3[:] = [x-1 for x in footer_3]
        footer_lists += footer_3
        if len(footer_3) != 0:
            doublecheck_dict["Total"] = footer_3
            order_of_element.append("Total")
        footer_4 = equalindex(df,0,"Transaction No.")
        footer_lists += footer_4
        if len(footer_4) != 0:
            doublecheck_dict["Transaction No."] = footer_4
            order_of_element.append("Transaction No.")
        footer_5 = containindex(df,0,"CounterpartyPlacementLocalPlacement")
        footer_lists += footer_5
        if len(footer_5) != 0:
            doublecheck_dict["CounterpartyPlacementLocalPlacement"] = footer_5
            order_of_element.append("CounterpartyPlacementLocalPlacement")
        footer_6 = equalindex(df,2,"Nominal")
        footer_lists += footer_6
        if len(footer_6) != 0:
            doublecheck_dict["Nominal"] = footer_6
            order_of_element.append("Nominal")
        footer_7 = equalindex(df,0,"GRAND TOTAL")
        footer_7[:] = [x+1 for x in footer_7]
        footer_lists += footer_7
        if len(footer_7) != 0:
            doublecheck_dict["GRAND TOTAL"] = footer_7
            order_of_element.append("GRAND TOTAL")
        footer_8 = equalindex(df,0,"Trade Date Broker NameSettlement Date")
        footer_lists += footer_8
        if len(footer_8) != 0:
            doublecheck_dict["Trade Date Broker NameSettlement Date"] = footer_8
            order_of_element.append("Trade Date Broker NameSettlement Date")
        footer_9 = equalindex(df,2,"Opening Counterparty Name Date")
        footer_lists += footer_9
        if len(footer_9) != 0:
            doublecheck_dict["Opening Counterparty Name Date"] = footer_9
            order_of_element.append("Opening Counterparty Name Date")
        footer_10 = equalindex(df,8,"Interest Received")
        footer_lists += footer_10
        if len(footer_10) != 0:
            doublecheck_dict["Interest Received"] = footer_10
            order_of_element.append("Interest Received")
        footer_11 = equalindex(df,2,"Proceed AmountTypes")
        footer_lists += footer_11
        if len(footer_11) != 0:
            doublecheck_dict["Proceed AmountTypes"] = footer_11
            order_of_element.append("Proceed AmountTypes")
        footer_12 = equalindex(df,2,"Quantity")
        footer_lists += footer_12
        if len(footer_12) != 0:
            doublecheck_dict["Quantity"] = footer_12
            order_of_element.append("Quantity")
        footer_13 = equalindex(df,2,"Units")
        footer_lists += footer_13
        if len(footer_13) != 0:
            doublecheck_dict["Units"] = footer_13
            order_of_element.append("Units")
        footer_lists = np.sort(footer_lists)
        #print(footer_lists)
        paired_lists = list(zip(footer_lists[:-1], footer_lists[1:]))
        #print(doublecheck_dict)

#restructuring dict

        dict_count = 0
        doublecheck_dict2 ={}
        output_list = []
        for item in order_of_element:
            #print (item)
            if item in doublecheck_dict:
                doublecheck_dict2[item] = list(paired_lists[i] for i in range(dict_count,dict_count+len(doublecheck_dict[item])))
                dict_count += len(doublecheck_dict[item])
        
#Cleaning list
        for item in order_of_element:
            if item == 'Unrealised Gain':
                for i in range(0,len(doublecheck_dict2[item])):
                    temp_df = comma_remove(unrealised_solver(df[(doublecheck_dict2[item][i][0]):(doublecheck_dict2[item][i][1])]))
                    output_list.append(temp_df.append(pd.Series([np.nan]),ignore_index=True))
            elif item == 'Total':
                for i in range(0,len(doublecheck_dict2[item])):
                    temp_df = comma_remove(total_solver(df[(doublecheck_dict2[item][i][0]):(doublecheck_dict2[item][i][1])]))
                    #print(total_solver(temp_df))
                    output_list.append(temp_df.append(pd.Series([np.nan]),ignore_index=True))
            elif item == 'Nominal': 
                for i in range(0,len(doublecheck_dict2[item])):
                    temp_df = comma_remove(nominal_solver(df[(doublecheck_dict2[item][i][0]):(doublecheck_dict2[item][i][1])]))
                    #print(nominal_solver(temp_df))
                    output_list.append(temp_df.append(pd.Series([np.nan]),ignore_index=True))
            elif item == 'CounterpartyPlacementLocalPlacement':
                for i in range(0,len(doublecheck_dict2[item])):
                    temp_df = counterparty_solver(df[(doublecheck_dict2[item][i][0]):(doublecheck_dict2[item][i][1])])
                    #print(counterparty_solver(temp_df))
                    output_list.append(temp_df.append(pd.Series([np.nan]),ignore_index=True))
            else:
                for i in range(0,len(doublecheck_dict2[item])):
                    try:
                        temp_df = comma_remove(df[(doublecheck_dict2[item][i][0]):(doublecheck_dict2[item][i][1])])
                    except:
                        temp_df = (df[(doublecheck_dict2[item][i][0]):(doublecheck_dict2[item][i][1])])
                    output_list.append(temp_df.append(pd.Series([np.nan]),ignore_index=True))

        return pd.concat(output_list).reset_index(drop=True),footer_lists
    df = read_csv_bad_col(csv_file)
    output_df,output_list = solver(df)
    #output_df = comma_remove(output_df)
    return (output_df).iloc[:,1:],output_list
    #return pd.to_numeric(output_df.iloc[0:,2], downcast ='signed',errors='ignore')
    #return solver(df)

df,highlight = AHC_solver(csv_file_path)

file_name = "AHC_2_processed.xlsx"
writer = pd.ExcelWriter(file_name, engine='xlsxwriter',options = {'strings_to_numbers': True})
df.to_excel(writer, sheet_name='Sheet1',index=False,header=False)
print(highlight)
workbook = writer.book
worksheet = writer.sheets['Sheet1']
format_yellow = workbook.add_format({'bg_color':'yellow'})
highlight = highlight[1:-1]
col_list = []
count_col_list = 0
for i in highlight:
    col_list.append(i+count_col_list)
    count_col_list += 1
print (col_list)
for i in col_list:
    worksheet.set_row(i,None,format_yellow)
writer.save()

