# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 18:53:00 2017

@author: Daniel Mattos
"""
import cvm_support_v14_core
from cvm_support_v14_core import series_Open
from cvm_support_v14_core import get_Q_Revenue
from cvm_support_v14_core import get_Q_EBITDA
from cvm_support_v14_core import get_Q_Earnings
from cvm_support_v14_core import get_Q_Market_Cap_Release_Date
from cvm_support_v14_core import series_Plot
from cvm_support_v14_core import series_Val
from cvm_support_v14_core import DFs_Series
from cvm_support_v14_core import DFs
import pickle
import time
import cmd
import os

class EarningsDBShell(cmd.Cmd):
    intro = 'Welcome to the EarningsDB shell. Type help or ? to list commands.\nAll values are in R$ thousands, except per share prices or multiples'
    prompt = '(EarningsDB) '
    file = None

    # ----- basic EarningsDB commands -----
    def do_Q_Revenue(self, arg):
        'Get quarterly Revenue:  Q_Revenue Company_Name'
        tmp = get_Q_Revenue(*parse(arg))
        print(tmp)

    def do_Q_EBITDA(self, arg):
        'Get quarterly unadjusted EBITDA:  Q_EBITDA Company_Name'
        tmp = get_Q_EBITDA(*parse(arg))
        print(tmp)

    def do_Q_Earnings(self, arg):
        'Get quarterly unadjusted Earnings:  Q_Earnings Company_Name'
        tmp = get_Q_Earnings(*parse(arg))
        print(tmp)

    def do_Plot(self, arg):
        'Plot company data:  Plot function_name Company_Name multiple=False (e.g. EV/EBITDA -> True | Revenue -> False)'
        tmp = arg.split()
        tmp[0]='get_'+tmp[0]
        arg = ' '.join(tmp)
        series_Plot(*parse(arg))

    def do_Exit(self,*args):
        'Close window and exit:  Exit'
        return True

    def do_Valuation(self, arg):
        'Get quick and dirty valuation:  Valuation Company_Name, wacc=0.12, inflation = 0.045, real_growth = 0.02'
        series_Val(*parse(arg))

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple([eval(x) for x in tuple(map(str,arg.split()))])

if __name__ == '__main__':
    Gerdau = series_Open(os.path.dirname(os.path.realpath(__file__))+'/GGBR3')
    Petrobras = series_Open(os.path.dirname(os.path.realpath(__file__))+'/PETR3')
    Grendene = series_Open(os.path.dirname(os.path.realpath(__file__))+'/GRND3')
    EarningsDBShell().cmdloop()
