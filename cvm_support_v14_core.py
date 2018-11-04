# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 13:28:50 2017

@author: Daniel Mattos
"""

import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')

from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib
matplotlib.use("Agg")

from datetime import datetime, timedelta
import matplotlib.pyplot as plt



import pandas as pd
import numpy as np
import pickle
import time

### Dictionary for Converting URLs ###
urlDic = {
    'ç': '%C3%A7',
    'ã': '%C3%A3',
    ' ': '%20',
    '&amp;': '&'
}

### Dictionary for Converting Special Characters in HTML Statements  ###
strDic = {
    '\xa0': ''
}

### Dictionary for Converting Dates to Corresponding Quarters ###
dateDic = {
    '01/01': 0,
    '31/03': 1,
    '01/04': 1,
    '30/06': 2,
    '01/07': 2,
    '30/09': 3,
    '01/10': 3,
    '31/12': 4
}

### Closest Date to a Given Date ###
def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

### Convert BR Date With Slash to Standard Format With Dash ###
def convert_date(BR_Date):
    year = BR_Date[6:10]
    month = BR_Date[3:5]
    day = BR_Date[0:2]
    return year+'-'+month+'-'+day

### Get Number of Quarters Between Dates ###
def span(date):
    beg = dateDic[date[0:5]]
    end = dateDic[date[11:16]]
    if end > beg:
        return end - beg
    else:
        return (4-beg+end)

### Handles Possible Date Inconsistency in Statements ###
def check_DF_date_consistency(statement):
    if statement.columns.values[1]==statement.columns.values[2]:
        if statement.iloc[0,1]==statement.iloc[0,2]:
            return 1
        elif statement.iloc[0,1]==0 and statement.iloc[0,2]!=0:
            return 2
        elif statement.iloc[0,1]!=0 and statement.iloc[0,2]==0:
            return 1
        else:
            return 0
    else:
        return 1

### Check if Each Statement Corresponds to the Right Number as per CVM Convention ###
def check_DF_items_consistency(series):
    error = False
    for i in series.DF:
        if i.IS.index.values[0][0]=='3' and\
            i.CF.index.values[0][0]=='6' and\
            i.BS.index.values[0][0]=='1' and\
            i.BS.index.values[len(i.BS.index.values)-1][0]=='2':
            pass
        else:
            error = True
    return error

### Replace Text According to Dictionary ###
def multipleReplace(text, wordDict):

    for key in wordDict:
        try:
            text = text.replace(key, wordDict[key])
        except AttributeError:
            text = text
        except IndexError:
            text = text
    return text

### Remove Thousands Separator and Replace Decimal Separator ###
def valor(my_str):
    try:
        val = float(my_str.replace('.','').replace(',','.'))
    except ValueError:
        val = ''
    return val

### Get Quarterly Result for Specified Accounts and Date in the IS ###
def get_Q_Account_IS(series,date,index=[],dic=[]):
    try:
        if index == []:
            for i,items in enumerate(series.DF):
                period = span(items.IS.columns.values[1])
                if date == items.filing_date:
                    if period==1:
                        if check_DF_date_consistency(items.IS)==1:
                            return get_Combo_Account_by_Name(items.IS,dic)[1]
                        elif check_DF_date_consistency(items.IS)==2:
                            return get_Combo_Account_by_Name(items.IS,dic)[2]
                            print('Please check DFs on ',items.filing_date)
                        else:
                            print('Could not handle inconsistency')
                            return 0
                    elif period>1:
                        return get_Combo_Account_by_Name(series.DF[i].IS,dic)[1]-get_Combo_Account_by_Name(series.DF[i+1].IS,dic)[2]
        else:
            for i,items in enumerate(series.DF):
                period = span(items.IS.columns.values[1])
                if date == items.filing_date:
                    if period==1:
                        if check_DF_date_consistency(items.IS)==1:
                            return get_Combo_Account_by_Index(items.IS,index)[1]
                        elif check_DF_date_consistency(items.IS)==2:
                            return get_Combo_Account_by_Name(items.IS,index)[2]
                            print('Please check DFs on ',items.filing_date)
                        else:
                            print('Could not handle inconsistency')
                            return 0
                    elif period>1:
                        return get_Combo_Account_by_Index(series.DF[i].IS,index)[1]-get_Combo_Account_by_Index(series.DF[i+1].IS,index)[2]
    except KeyError:
        return 0
    except TypeError:
        return 0
    return None

### Get Quarterly Result for Specified Accounts and Date in the CF ###
def get_Q_Account_CF(series,date,index=[],dic=[]):
    try:
        if index == []:
            for i,items in enumerate(series.DF):
                period = span(items.CF.columns.values[1])
                if date == items.filing_date:
                    if period==1:
                        if check_DF_date_consistency(items.CF)==1:
                            return get_Combo_Account_by_Name(items.CF,dic)[1]
                        elif check_DF_date_consistency(items.CF)==2:
                            return get_Combo_Account_by_Name(items.CF,dic)[2]
                            print('Please check DFs on ',items.filing_date)
                        else:
                            print('Could not handle inconsistency')
                            return 0
                    elif period>1:
                        return get_Combo_Account_by_Name(series.DF[i].CF,dic)[1]-get_Combo_Account_by_Name(series.DF[i+1].CF,dic)[1]
        else:
            for i,items in enumerate(series.DF):
                period = span(items.CF.columns.values[1])
                if date == items.filing_date:
                    if period==1:
                        if check_DF_date_consistency(items.CF)==1:
                            return get_Combo_Account_by_Index(items.CF,index)[1]
                        elif check_DF_date_consistency(items.CF)==2:
                            return get_Combo_Account_by_Name(items.CF,index)[2]
                            print('Please check DFs on ',items.filing_date)
                        else:
                            print('Could not handle inconsistency')
                            return 0
                    elif period>1:
                        return get_Combo_Account_by_Index(series.DF[i].CF,index)[1]-get_Combo_Account_by_Index(series.DF[i+1].CF,index)[1]
    except KeyError:
        return 0
    except TypeError:
        return 0
    return None

### Get End on Quarter Result for Specified Accounts and Date in the BS ###
def get_Q_Account_BS(series,date,index=[],dic=[]):
    try:
        if index == []:
            for i,items in enumerate(series.DF):
                if date == items.filing_date:
                    return get_Combo_Account_by_Name(series.DF[i].BS,dic)[1]
        else:
            for i,items in enumerate(series.DF):
                if date == items.filing_date:
                    return get_Combo_Account_by_Index(series.DF[i].BS,index)[1]
    except KeyError:
        return 0
    except TypeError:
        return 0
    return None

### Sum Multiple Lines in a Statement by Name - e.g. Depreciation and Amortization ###
def get_Combo_Account_by_Name(DF,dic,name=''):
    #exmample DF: CF
    #exmaple name = 'DA'
    #example dic = ['Deprec','Amort','Exaust','amort','deprec','exaust']
    width = len(DF.columns.values)
    values = [0]*width
    values[0] = name
    i=0
    for i in range(0,len(DF.index.values)):
        if max([any(x in DF.iloc[i,0] for x in dic)]):
            for j in range(1,width):
                try:
                    values[j] += DF.iloc[i,j]
                except ValueError:
                    values[j] += 0
                except TypeError:
                    values[j] += 0
                except KeyError:
                    values[j] += 0
    return values

### Sum Multiple Lines in a Statement by Index - e.g. EBIT ###
def get_Combo_Account_by_Index(DF,index,name=''):
    #exmample DF: IS
    #exmaple name = 'EBIT'
    #example index = ['3.05']
    width = len(DF.columns.values)
    values = [0]*width
    values[0] = name
    i=0
    for i in index:
        for j in range(1,width):
            try:
                values[j] += DF.loc[i][j]
            except ValueError:
                values[j] += 0
            except TypeError:
                values[j] += 0
            except KeyError:
                values[j] += 0
    return values

### Data Frame With Unadjusted EBITDAs ###
def get_Q_EBITDA(series):
    l = list()
    for i in series.DF:
        try:
            EBITDA =  get_Q_Account_CF(series,i.filing_date,dic=['Deprec'])\
                        +get_Q_Account_IS(series,i.filing_date,index=['3.05'])
            l.append(i.filing_date)
            l.append(EBITDA)
        except TypeError:
            EBITDA = None
        except IndexError:
            EBITDA = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EBITDA']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['EBITDA']=pd.to_numeric(df['EBITDA']).round(2)
    return df

### Data Frame With Unadjusted LTM EBITDAs ###
def get_Q_EBITDA_LTM_Release_Date(series):
    l = list()
    Q_EBITDA = get_Q_EBITDA(series)
    for i in range(4,len(Q_EBITDA)+1):
        try:
            EBITDA_LTM = float(Q_EBITDA[(i-4):i].sum())
            l.append(series.DF[len(Q_EBITDA)-i].delivery_date[0:10])
            l.append(EBITDA_LTM)
        except TypeError:
            EBITDA_LTM = None
        except IndexError:
            EBITDA_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EBITDA_LTM'])
    df.set_index('Date',inplace=True)
    df['EBITDA_LTM']=pd.to_numeric(df['EBITDA_LTM']).round(2)
    return df

### Data Frame With Unadjusted EBITDAs as of Release Date ###
def get_Q_EBITDA_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            EBITDA =  get_Q_Account_CF(series,i.filing_date,dic=['Deprec'])\
                        +get_Q_Account_IS(series,i.filing_date,index=['3.05'])
            l.append(i.delivery_date[0:10])
            l.append(EBITDA)
        except TypeError:
            EBITDA = None
        except IndexError:
            EBITDA = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EBITDA']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['EBITDA']=pd.to_numeric(df['EBITDA']).round(2)
    return df

### Data Frame With Unadjusted Revenue ###
def get_Q_Revenue(series):
    l = list()
    for i in series.DF:
        try:
            Revenue =  get_Q_Account_IS(series,i.filing_date,index=['3.01'])
            l.append(i.filing_date)
            l.append(Revenue)
        except TypeError:
            Revenue = None
        except IndexError:
            Revenue = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Revenue']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Revenue']=pd.to_numeric(df['Revenue']).round(2)
    return df

### Data Frame With Unadjusted Revenue as of Release Date ###
def get_Q_Revenue_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            Revenue =  get_Q_Account_IS(series,i.filing_date,index=['3.01'])
            l.append(i.delivery_date[0:10])
            l.append(Revenue)
        except TypeError:
            Revenue = None
        except IndexError:
            Revenue = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Revenue']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Revenue']=pd.to_numeric(df['Revenue']).round(2)
    return df

### Data Frame With Unadjusted LTM Revenue ###
def get_Q_Revenue_LTM_Release_Date(series):
    l = list()
    Q_Revenue = get_Q_Revenue(series)
    for i in range(4,len(Q_Revenue)+1):
        try:
            Revenue_LTM = float(Q_Revenue[(i-4):i].sum())
            l.append(series.DF[len(Q_Revenue)-i].delivery_date[0:10])
            l.append(Revenue_LTM)
        except TypeError:
            Revenue_LTM = None
        except IndexError:
            Revenue_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Revenue_LTM'])
    df.set_index('Date',inplace=True)
    df['Revenue_LTM']=pd.to_numeric(df['Revenue_LTM']).round(2)
    return df

### Data Frame With Unadjusted COGS ###
def get_Q_COGS(series):
    l = list()
    for i in series.DF:
        try:
            COGS =  get_Q_Account_IS(series,i.filing_date,index=['3.02'])
            l.append(i.filing_date)
            l.append(COGS)
        except TypeError:
            COGS = None
        except IndexError:
            COGS = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','COGS']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['COGS']=pd.to_numeric(df['COGS']).round(2)
    return df

### Data Frame With Unadjusted COGS as of Release Date ###
def get_Q_COGS_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            COGS =  get_Q_Account_IS(series,i.filing_date,index=['3.02'])
            l.append(i.delivery_date[0:10])
            l.append(COGS)
        except TypeError:
            COGS = None
        except IndexError:
            COGS = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','COGS']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['COGS']=pd.to_numeric(df['COGS']).round(2)
    return df

### Data Frame With Unadjusted LTM COGS ###
def get_Q_COGS_LTM_Release_Date(series):
    l = list()
    Q_COGS = get_Q_COGS(series)
    for i in range(4,len(Q_COGS)+1):
        try:
            COGS_LTM = float(Q_COGS[(i-4):i].sum())
            l.append(series.DF[len(Q_COGS)-i].delivery_date[0:10])
            l.append(COGS_LTM)
        except TypeError:
            COGS_LTM = None
        except IndexError:
            COGS_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','COGS_LTM'])
    df.set_index('Date',inplace=True)
    df['COGS_LTM']=pd.to_numeric(df['COGS_LTM']).round(2)
    return df

### Data Frame With Unadjusted SGA_Other ###
def get_Q_SGA_Other(series):
    l = list()
    for i in series.DF:
        try:
            SGA_Other =  get_Q_Account_IS(series,i.filing_date,index=['3.04'])
            l.append(i.filing_date)
            l.append(SGA_Other)
        except TypeError:
            SGA_Other = None
        except IndexError:
            SGA_Other = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','SGA_Other']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['SGA_Other']=pd.to_numeric(df['SGA_Other']).round(2)
    return df

### Data Frame With Unadjusted SGA_Other as of Release Date ###
def get_Q_SGA_Other_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            SGA_Other =  get_Q_Account_IS(series,i.filing_date,index=['3.04'])
            l.append(i.delivery_date[0:10])
            l.append(SGA_Other)
        except TypeError:
            SGA_Other = None
        except IndexError:
            SGA_Other = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','SGA_Other']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['SGA_Other']=pd.to_numeric(df['SGA_Other']).round(2)
    return df

### Data Frame With Unadjusted LTM SGA_Other ###
def get_Q_SGA_Other_LTM_Release_Date(series):
    l = list()
    Q_SGA_Other = get_Q_SGA_Other(series)
    for i in range(4,len(Q_SGA_Other)+1):
        try:
            SGA_Other_LTM = float(Q_SGA_Other[(i-4):i].sum())
            l.append(series.DF[len(Q_SGA_Other)-i].delivery_date[0:10])
            l.append(SGA_Other_LTM)
        except TypeError:
            SGA_Other_LTM = None
        except IndexError:
            SGA_Other_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','SGA_Other_LTM'])
    df.set_index('Date',inplace=True)
    df['SGA_Other_LTM']=pd.to_numeric(df['SGA_Other_LTM']).round(2)
    return df

### Data Frame With Unadjusted EBIT ###
def get_Q_EBIT(series):
    l = list()
    for i in series.DF:
        try:
            EBIT =  get_Q_Account_IS(series,i.filing_date,index=['3.05'])
            l.append(i.filing_date)
            l.append(EBIT)
        except TypeError:
            EBIT = None
        except IndexError:
            EBIT = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EBIT']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['EBIT']=pd.to_numeric(df['EBIT']).round(2)
    return df

### Data Frame With Unadjusted EBIT as of Release Date ###
def get_Q_EBIT_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            EBIT =  get_Q_Account_IS(series,i.filing_date,index=['3.05'])
            l.append(i.delivery_date[0:10])
            l.append(EBIT)
        except TypeError:
            EBIT = None
        except IndexError:
            EBIT = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EBIT']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['EBIT']=pd.to_numeric(df['EBIT']).round(2)
    return df

### Data Frame With Unadjusted LTM EBIT ###
def get_Q_EBIT_LTM_Release_Date(series):
    l = list()
    Q_EBIT = get_Q_EBIT(series)
    for i in range(4,len(Q_EBIT)+1):
        try:
            EBIT_LTM = float(Q_EBIT[(i-4):i].sum())
            l.append(series.DF[len(Q_EBIT)-i].delivery_date[0:10])
            l.append(EBIT_LTM)
        except TypeError:
            EBIT_LTM = None
        except IndexError:
            EBIT_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EBIT_LTM'])
    df.set_index('Date',inplace=True)
    df['EBIT_LTM']=pd.to_numeric(df['EBIT_LTM']).round(2)
    return df

### Data Frame With Unadjusted Earnings ###
def get_Q_Earnings(series):
    l = list()
    for i in series.DF:
        try:
            Earnings =  get_Q_Account_IS(series,i.filing_date,index=['3.09'])
            l.append(i.filing_date)
            l.append(Earnings)
        except TypeError:
            Earnings = None
        except IndexError:
            Earnings = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Earnings']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Earnings']=pd.to_numeric(df['Earnings']).round(2)
    return df

### Data Frame With Unadjusted Earnings as of Release Date ###
def get_Q_Earnings_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            Earnings =  get_Q_Account_IS(series,i.filing_date,index=['3.09'])
            l.append(i.delivery_date[0:10])
            l.append(Earnings)
        except TypeError:
            Earnings = None
        except IndexError:
            Earnings = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Earnings']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Earnings']=pd.to_numeric(df['Earnings']).round(2)
    return df

### Data Frame With Unadjusted LTM Earnings ###
def get_Q_Earnings_LTM_Release_Date(series):
    l = list()
    Q_Earnings = get_Q_Earnings(series)
    for i in range(4,len(Q_Earnings)+1):
        try:
            Earnings_LTM = float(Q_Earnings[(i-4):i].sum())
            l.append(series.DF[len(Q_Earnings)-i].delivery_date[0:10])
            l.append(Earnings_LTM)
        except TypeError:
            Earnings_LTM = None
        except IndexError:
            Earnings_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Earnings_LTM'])
    df.set_index('Date',inplace=True)
    df['Earnings_LTM']=pd.to_numeric(df['Earnings_LTM']).round(2)
    return df

### Data Frame With Unadjusted Financial Expense ###
def get_Q_Financial(series):
    l = list()
    for i in series.DF:
        try:
            Financial =  get_Q_Account_IS(series,i.filing_date,index=['3.06'])
            l.append(i.filing_date)
            l.append(Financial)
        except TypeError:
            Financial = None
        except IndexError:
            Financial = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Financial']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Financial']=pd.to_numeric(df['Financial']).round(2)
    return df

### Data Frame With Unadjusted Financial Expense as of Release Date ###
def get_Q_Financial_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            Financial =  get_Q_Account_IS(series,i.filing_date,index=['3.06'])
            l.append(i.delivery_date[0:10])
            l.append(Financial)
        except TypeError:
            Financial = None
        except IndexError:
            Financial = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Financial']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Financial']=pd.to_numeric(df['Financial']).round(2)
    return df

### Data Frame With Unadjusted LTM Financial Expense ###
def get_Q_Financial_LTM_Release_Date(series):
    l = list()
    Q_Financial = get_Q_Financial(series)
    for i in range(4,len(Q_Financial)+1):
        try:
            Financial_LTM = float(Q_Financial[(i-4):i].sum())
            l.append(series.DF[len(Q_Financial)-i].delivery_date[0:10])
            l.append(Financial_LTM)
        except TypeError:
            Financial_LTM = None
        except IndexError:
            Financial_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Financial_LTM'])
    df.set_index('Date',inplace=True)
    df['Financial_LTM']=pd.to_numeric(df['Financial_LTM']).round(2)
    return df

### Data Frame With Quarterly FCFF ###
def get_Q_FCFF(series):
    l = list()
    for i in series.DF:
        try:
            #CFO + I*(1-t) - Capex
            I = -get_Q_Account_IS(series,i.filing_date,index=['3.06'])
            T = -get_Q_Account_IS(series,i.filing_date,index=['3.08'])
            EBT = get_Q_Account_IS(series,i.filing_date,index=['3.07'])
            try:
                t = max(T/EBT,0.34)
            except ZeroDivisionError:
                t = 0
            FCFF =  get_Q_Account_CF(series,i.filing_date,index=['6.01'])\
                    +I*(1-t)\
                    +get_Q_Account_CF(series,i.filing_date,index=['6.02'])
            l.append(i.filing_date)
            l.append(FCFF)
        except TypeError:
            FCFF = None
        except IndexError:
            FCFF = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','FCFF']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['FCFF']=pd.to_numeric(df['FCFF']).round(2)
    return df

### Data Frame With Unadjusted FCFF as of Release Date ###
def get_Q_FCFF_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            #CFO + I*(1-t) - Capex
            I = -get_Q_Account_IS(series,i.filing_date,index=['3.06'])
            T = -get_Q_Account_IS(series,i.filing_date,index=['3.08'])
            EBT = get_Q_Account_IS(series,i.filing_date,index=['3.07'])
            try:
                t = max(T/EBT,0.34)
            except ZeroDivisionError:
                t = 0
            FCFF =  get_Q_Account_CF(series,i.filing_date,index=['6.01'])\
                    +I*(1-t)\
                    +get_Q_Account_CF(series,i.filing_date,index=['6.02'])
            l.append(i.delivery_date[0:10])
            l.append(FCFF)
        except TypeError:
            FCFF = None
        except IndexError:
            FCFF = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','FCFF']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['FCFF']=pd.to_numeric(df['FCFF']).round(2)
    return df

### Data Frame With Unadjusted LTM FCFF ###
def get_Q_FCFF_LTM_Release_Date(series):
    l = list()
    Q_FCFF = get_Q_FCFF_Release_Date(series)
    for i in range(4,len(Q_FCFF)+1):
        try:
            FCFF_LTM = float(Q_FCFF[(i-4):i].sum())
            l.append(series.DF[len(Q_FCFF)-i].delivery_date[0:10])
            l.append(FCFF_LTM)
        except TypeError:
            FCFF_LTM = None
        except IndexError:
            FCFF_LTM = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','FCFF_LTM'])
    df.set_index('Date',inplace=True)
    df['FCFF_LTM']=pd.to_numeric(df['FCFF_LTM']).round(2)
    return df

### Data Frame With Net Debt ###
def get_Q_Net_Debt(series):
    l = list()
    for i in series.DF:
        try:
            Net_Debt =  get_Q_Account_BS(series,i.filing_date,index=['2.01.04','2.02.01'])\
                        - get_Q_Account_BS(series,i.filing_date,index=['1.01.01','1.01.02'])
            l.append(i.filing_date)
            l.append(Net_Debt)
        except TypeError:
            Net_Debt = None
        except IndexError:
            Net_Debt = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Net_Debt'])
    df.set_index('Date',inplace=True)
    df = df.iloc[::-1]
    df['Net_Debt']=pd.to_numeric(df['Net_Debt']).round(2)
    return df

### Data Frame With Net Debt as of Release Date ###
def get_Q_Net_Debt_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            Net_Debt =  get_Q_Account_BS(series,i.filing_date,index=['2.01.04','2.02.01'])\
                        - get_Q_Account_BS(series,i.filing_date,index=['1.01.01','1.01.02'])
            l.append(i.delivery_date[0:10])
            l.append(Net_Debt)
        except TypeError:
            Net_Debt = None
        except IndexError:
            Net_Debt = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Net_Debt'])
    df.set_index('Date',inplace=True)
    df = df.iloc[::-1]
    df['Net_Debt']=pd.to_numeric(df['Net_Debt']).round(2)
    return df

### Net Debt to EBITDA as of Release Date ###
def get_Q_Net_Debt_EBITDA(series):
    t = get_Q_Net_Debt_Release_Date(series).join(get_Q_EBITDA_LTM_Release_Date(series))
    df = (((t.loc[:,'Net_Debt']/t.loc[:,'EBITDA_LTM']).dropna()).round(2)).to_frame()
    df.columns = ['Net_Debt_to_EBITDA']
    return df

def get_Q_EV_Bridge(series):
    l = list()
    for i in series.DF:
        try:
            EV_Bridge =  get_Q_Account_BS(series,i.filing_date,index=['2.01.04','2.02.01'])\
                        - get_Q_Account_BS(series,i.filing_date,index=['1.01.01','1.01.02'])
            l.append(i.delivery_date[0:10])
            l.append(EV_Bridge)
        except TypeError:
            EV_Bridge = None
        except IndexError:
            EV_Bridge = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EV_Bridge'])
    df.set_index('Date',inplace=True)
    df = df.iloc[::-1]
    df['EV_Bridge']=pd.to_numeric(df['EV_Bridge']).round(2)
    return df

### Data Frame With Past EV Bridges as of Release Dates ###
def get_Q_EV_Bridge_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            EV_Bridge =  get_Q_Account_BS(series,i.filing_date,index=['2.01.04','2.02.01','2.03.09'])\
                        -get_Q_Account_BS(series,i.filing_date,index=['1.01.01','1.01.02'])
            l.append(i.delivery_date[0:10])
            l.append(EV_Bridge)
        except TypeError:
            EV_Bridge = None
        except IndexError:
            EV_Bridge = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','EV_Bridge']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['EV_Bridge']=pd.to_numeric(df['EV_Bridge']).round(2)
    return df

### Book Value as of Release Date ###
def get_Q_BV_Release_Date(series):
    l = list()
    for i in series.DF:
        try:
            BV = get_Q_Account_BS(series,i.filing_date,index=['2.03'])\
            -get_Q_Account_BS(series,i.filing_date,index=['2.03.09'])
            l.append(i.delivery_date[0:10])
            l.append(BV)
        except TypeError:
            BV = None
        except IndexError:
            BV = None
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Book_Value']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Book_Value']=pd.to_numeric(df['Book_Value']).round(2)
    return df

### Market Cap ###
def get_Q_Market_Cap_Release_Date(series):
    # In thousands of reais
    l = list()
    for i in series.DF:
        try:
            date = convert_date(i.delivery_date[0:10])
            if series.ticker_preferred==None:
                Market_Cap = i.common_shares*series.common_prices['Close'][date]/1000
            else:
                Market_Cap = (i.common_shares*series.common_prices['Close'][date]\
                +i.preferred_shares*series.preferred_prices['Close'][date])/1000
            l.append(i.delivery_date[0:10])
            l.append(Market_Cap)
        except TypeError:
            Market_Cap = None
        except IndexError:
            Market_Cap = None
        except KeyError:
            date = convert_date(i.delivery_date[0:10])
            date = nearest(series.common_prices.index,datetime.strptime(date,'%Y-%m-%d'))
            if series.ticker_preferred==None:
                Market_Cap = i.common_shares*series.common_prices['Close'][date]/1000
            else:
                Market_Cap = (i.common_shares*series.common_prices['Close'][date]\
                +i.preferred_shares*series.preferred_prices['Close'][date])/1000
            l.append(i.delivery_date[0:10])
            l.append(Market_Cap)
    df = pd.DataFrame(np.array(l).reshape(int(len(l)/2),2), columns = ['Date','Market_Cap']).iloc[::-1]
    df.set_index('Date',inplace=True)
    df['Market_Cap']=pd.to_numeric(df['Market_Cap']).round(2)
    return df

### EV to EBITDA ###
def get_Q_EV_EBITDA_Release_Date(series):
    t = get_Q_Market_Cap_Release_Date(series).join(get_Q_EV_Bridge_Release_Date(series))
    t = t.join(get_Q_EBITDA_LTM_Release_Date(series))
    df = ((((t.loc[:,'Market_Cap']+t.loc[:,'EV_Bridge'])/t.loc[:,'EBITDA_LTM']\
            ).dropna()).round(2)).to_frame()
    df.columns = ['EV_to_EBITDA']
    return df

### Plot Series ###
def series_Plot(method, series, multiple = False):
    y = method(series).iloc[:,0].values.tolist()
    x = method(series).index.values.tolist()
    y_mean = [np.mean(y)]*len(x)
    short_date=list()
    for i in x:
        if i[3]=='0':
            short_date.append(i[4:6]+i[8:10])
        else:
            short_date.append(i[3:6]+i[8:10])
    x = list(range(0,len(short_date)))
    fig,ax = plt.subplots()
    if multiple == False:
        y = [x / 1000.0 for x in y]
        y_mean = [x / 1000.0 for x in y_mean ]
        plt.title(method.__name__[4:]+' R$MM')
    else:
        plt.title(method.__name__[4:]+' x')
    plt.xticks(x[::2], short_date[::2])
    ax.plot(x,y, label='Data', marker='o')
    ax.plot(x,y_mean, label='Mean', linestyle='--')
    ax.legend(loc='upper right')
    plt.show()
    fig.savefig("graph.png")

### Summary of Valuation Estimates ###
def series_Val(series, wacc=0.12, inflation = 0.045, real_growth = 0.02):
    cs = series.DF[0].common_shares/1000 #In thousands
    ps = series.DF[0].preferred_shares/1000 #In thousands
    cp = series.common_prices['Close'].iloc[-1]
    if ps == None:
        rc = 1
    else:
        pp = series.preferred_prices['Close'].iloc[-1]
        rp = 1/(cp/pp*cs+ps)
        rc = 1/(pp/cp*ps+cs)
    y = get_Q_FCFF_LTM_Release_Date(series)
    r = get_Q_Revenue_LTM_Release_Date(series).iloc[:,0].values.tolist()
    e = get_Q_EV_EBITDA_Release_Date(series).iloc[-1,0]
    EV_Bridge = get_Q_EV_Bridge(series).iloc[-1,0]
    result = seasonal_decompose(y, model='additive',freq=1)
    f_trend = result.trend.dropna() # Trend without NaNs
    try:
        g = min(real_growth+inflation,pow(float(r[len(r)-1])/float(r[0]),4.0/len(r))-1)
    except TypeError:
        g = real_growth+inflation
    g_steady_state = inflation
    trend_max_growth = (float(f_trend.max())*(1+g)/(wacc-g)-EV_Bridge)
    trend_max_no_growth = (float(f_trend.max())*(1+g_steady_state)/(wacc-g_steady_state)-EV_Bridge)
    trend_avg_growth = (float(f_trend.mean())*(1+g)/(wacc-g)-EV_Bridge)
    ltm_no_real_growth = ((y.iloc[-1,0])\
                        *(1+g_steady_state)/(wacc - g_steady_state)\
                        -EV_Bridge)
    bvps = get_Q_BV_Release_Date(series).iloc[-1,0]
    avg = sum([trend_max_growth,trend_max_no_growth,trend_avg_growth,ltm_no_real_growth,bvps])/5
    print('WACC BRL:       %.1f' % (100*wacc),'%')
    print('Nominal growth: %.1f' % (100*g),'%')
    print('Zero growth:    %.1f' % (100*g_steady_state),'%')
    print('*************************Valuation****************************')
    print('Max trend FCFF + growth          Common: %.2f' % (trend_max_growth*rc), end=' | ')
    print('Pref: %.2f' % (trend_max_growth*rp))
    print('Max trend FCFF + zero growth     Common: %.2f' % (trend_max_no_growth*rc), end = ' | ')
    print('Pref: %.2f' % (trend_max_no_growth*rp))
    print('Avg. trend FCFF + growth         Common: %.2f' % (trend_avg_growth*rc), end=' | ')
    print('Pref: %.2f' % (trend_avg_growth*rp))
    print('LTM FCFF + zero growth           Common: %.2f' % (ltm_no_real_growth*rc), end=' | ')
    print('Pref: %.2f' % (ltm_no_real_growth*rp))
    print('Book value per share             Common: %.2f' % (bvps*rc), end=' | ')
    print('Pref: %.2f' % (bvps*rp))
    print('**************************************************************')
    print('Average                          Common: %.2f' % (avg*rc), end=' | ')
    print('Pref: %.2f' % (avg*rp))
    print('Current price                    Common: %.2f' % cp, end=' | ')
    print('Pref: %.2f' % pp)
    print('Current EV / EBITDA LTM:                     %.2f x' % e)

### Load Pre-Saved Object ###
def series_Open(file_name):
    with open(file_name +'.pkl', 'rb') as input:
            return pickle.load(input)

class DFs:
    def __init__(self,cod, filing_date, delivery_date):
        self.cod = cod
        self.filing_date = filing_date
        self.delivery_date = delivery_date
        self.preferred_shares = None
        self.common_shares = None
        self.IS = None
        self.CF = None
        self.BS = None

class DFs_Series:
    def __init__(self,ticker_common,ccvm,cnpj,ticker_preferred=None):
        self.DF = list()
        self.ccvm = ccvm
        self.cnpj = cnpj
        self.name = ticker_common
        self.ticker_common = ticker_common
        self.ticker_preferred = ticker_preferred
        self.common_prices = None
        self.preferred_prices = None
    ### Get DF Series ###
    def get_DFs(self, last_n):
        ccvm = self.ccvm
        cnpj = self.cnpj
        self.DF = get_series(self.DF,ccvm,cnpj,last_n)
    def get_Prices(self):
        yf.pdr_override() #Temporary
        self.common_prices = pdr.get_data_yahoo(self.ticker_common+'.SA',start='2010-01-01')
        if self.ticker_preferred != None:
            self.preferred_prices = pdr.get_data_yahoo(self.ticker_preferred+'.SA',start='2010-01-01')
        else:
            self.preferred_prices = 0
    def series_save(self):
        with open(self.name+'.pkl', 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

