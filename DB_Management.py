from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import exc
from sqlalchemy.types import FLOAT,NVARCHAR,VARCHAR,DATETIME
import cvm_support_v15_core
from cvm_support_v15_core import *

# Global base variable
Base = declarative_base()

# Define table containing lines with companies in database
class companies(Base):
    __tablename__="companies"
    name = Column(String(50))
    ccvm = Column(String(15),unique=True,primary_key=True)
    cnpj = Column(String(25),unique=True,primary_key=True)
    ticker_common = Column(String(15),unique=True,primary_key=True)
    ticker_preferred = Column(String(15))
    ticker_other = Column(String(15))

    def __init__(self,name,ccvm,cnpj,ticker_common,ticker_preferred,ticker_other):
        self.name = name
        self.ccvm = ccvm
        self.cnpj = cnpj
        self.ticker_common = ticker_common
        self.ticker_preferred = ticker_preferred
        self.ticker_other = ticker_other

# Define table with rows containing filings for each company - i.e. financials
class financials(Base):
    __tablename__="financials"
    name = Column(String(50))
    ccvm = Column(String(15),ForeignKey('companies.ccvm'))
    cnpj = Column(String(25),ForeignKey('companies.cnpj'))
    cod = Column(String(60),unique=True,primary_key=True)
    common_shares = Column(Float)
    preferred_shares = Column(Float)
    filing_date = Column(String(20))
    delivery_date = Column(String(20))

    def __init__(self,name,ccvm,cnpj,cod,common_shares,preferred_shares,filing_date,delivery_date):
        self.name = name
        self.ccvm = ccvm
        self.cnpj = cnpj
        sef.cod = cod
        self.common_shares = common_shares
        self.preferred_shares = preferred_shares
        self.filing_date = filing_date
        self.delivery_date = delivery_date

# Insert new companies into companies table - series is the object; name should be a string such as 'Vale' or 'Petrobras'
def companies_insert(series,engine,name=None):
    if name==None:
        company_name = series.name
    else:
        company_name = name
    ccvm = series.ccvm
    cnpj = series.cnpj
    ticker_common = series.ticker_common
    ticker_preferred = series.ticker_preferred
    if ticker_preferred == None:
        ticker_preferred=''
    statement = 'INSERT INTO companies (name,ccvm,cnpj,ticker_common,ticker_preferred) VALUES ("'\
                    +company_name+'","'+ccvm+'","'+cnpj+'","'+ticker_common+'","'+ticker_preferred+'");'
    print(statement)
    try:
        engine.execute(statement)
    except exc.IntegrityError:
        print(name+' or its CVM code, or CNPJ may be a duplicate entry')

# Insert new filings into financials table - series is the object; name should be a string such as 'Vale' or 'Petrobras'
def financials_insert(series,engine,name=None):
    if name==None:
        company_name = series.name
    else:
        company_name = name
    ccvm = series.ccvm
    cnpj = series.cnpj
    for i in series.DF:
        statement = 'INSERT INTO financials (name,ccvm,cnpj,cod,common_shares,preferred_shares,filing_date,delivery_date) VALUES ("'\
                        +company_name+'","'+ccvm+'","'+cnpj+'","'+i.cod+'",'+str(i.common_shares)+','+str(i.preferred_shares)+',"'+i.filing_date+'","'+i.delivery_date+'");'
        print(statement)
        try:
            engine.execute(statement)
        except exc.IntegrityError:
            print(name+' statement '+ i.cod+' may be a duplicate entry')

# Create tables containing the company's financials
def tables_insert(series,engine,name=None):
    for i in series.DF:
        # Income Statement
        table_name = series.ccvm+'_'+i.cod+'_IS'
        try:
            df=i.IS.reset_index()
            dt={"index": NVARCHAR(length=50),"Descrição": NVARCHAR(length=255)}
            dt.update({col_name: FLOAT for col_name in df.columns[2:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(name+' '+i.filing_date+' income statement may already exist')
        table_name = series.ccvm+'_'+i.cod+'_BS'
        try:
            df=i.BS.reset_index()
            dt={"index": NVARCHAR(length=50),"Descrição": NVARCHAR(length=255)}
            dt.update({col_name: FLOAT for col_name in df.columns[2:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(name+' '+i.filing_date+' balance sheet may already exist')
        table_name = series.ccvm+'_'+i.cod+'_CF'
        try:
            df=i.CF.reset_index()
            dt={"index": NVARCHAR(length=50),"Descrição": NVARCHAR(length=255)}
            dt.update({col_name: FLOAT for col_name in df.columns[2:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(name+' '+i.filing_date+' cash flow may already exist')

# Create tables containing the company's share price series
def prices_insert(series,engine,name=None):
    if(series.ticker_common != None and series.ticker_common != ''):
        table_name = series.ccvm+'_common_prices'
        try:
            df=series.common_prices.reset_index()
            dt={"date": DATETIME}
            dt.update({col_name: FLOAT for col_name in df.columns[1:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(name+' common prices table may already exist')
    if(series.ticker_preferred != None and series.ticker_preferred != ''):
        table_name = series.ccvm+'_preferred_prices'
        try:
            df=series.preferred_prices.reset_index()
            dt={"date": DATETIME}
            dt.update({col_name: FLOAT for col_name in df.columns[1:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(name+' preferred prices table may already exist')

# Master function to store uploaded company series object to database
def series_store(series,engine,name):
    companies_insert(series,engine,name)
    financials_insert(series,engine,name)
    tables_insert(series,engine,name)
    prices_insert(series,engine,name)

# Restore object from database
def series_load(name,ccvm,engine):
    r = engine.execute('SELECT * FROM companies WHERE name = "'+name+'";').fetchall()
    if r==[]:
        print('Failed to find company '+name)
        return 0
    else:
        if r[0][4]=='':
            ticker_preferred=None
        else:
            ticker_preferred=r[0][4]
        obj_parent = DFs_Series(ticker_common=r[0][3],ccvm=r[0][1],cnpj=r[0][2],ticker_preferred=ticker_preferred)
        r = engine.execute('SELECT * FROM financials WHERE name = "'+name+'";').fetchall()
        l = list()
        for i in r:
            obj_child = DFs(cod=i[3], filing_date=i[6], delivery_date=i[7])
            obj_child.common_shares = i[5]
            obj_child.preferred_shares = i[4]
            obj_child.IS = convert_sql_financials_to_original(table_name=i[1]+'_'+i[3]+'_IS',engine=engine)
            obj_child.CF = convert_sql_financials_to_original(table_name=i[1]+'_'+i[3]+'_CF',engine=engine)
            obj_child.BS = convert_sql_financials_to_original(table_name=i[1]+'_'+i[3]+'_BS',engine=engine)
            l.insert(0,obj_child)
        obj_parent.DF = l
        obj_parent.common_prices = convert_sql_prices_to_original(table_name=obj_parent.ccvm+'_common_prices',engine=engine)
        if ticker_preferred !=None:
            obj_parent.preferred_prices = convert_sql_prices_to_original(table_name=obj_parent.ccvm+'_preferred_prices',engine=engine)
        return obj_parent

# Retrieve financials from tables
def convert_sql_financials_to_original(table_name,engine):
    df=pd.read_sql_table(table_name,engine)
    tmp = df.iloc[:,0]
    df=df.drop('index',axis=1)
    df.index = tmp
    del df.index.name
    return df

def convert_sql_prices_to_original(table_name,engine):
    df=pd.read_sql_table(table_name,engine)
    tmp = df.iloc[:,0]
    df=df.drop('Date',axis=1)
    df.index = tmp
    return df

# Delete all tables as well as entries in financials relative to the company represented by series object
def tables_delete(series,engine):
    for i in series.DF:
        try:
            statement = 'DROP TABLE '+ series.ccvm+'_'+i.cod+'_IS;'
            engine.execute(statement)
        except exc.ProgrammingError:
            print('Unknown table: '+series.ccvm+'_'+i.cod+'_IS')
        try:
            statement = 'DROP TABLE '+ series.ccvm+'_'+i.cod+'_BS;'
            engine.execute(statement)
        except exc.ProgrammingError:
            print('Unknown table: '+series.ccvm+'_'+i.cod+'_BS')
        try:
            statement = 'DROP TABLE '+ series.ccvm+'_'+i.cod+'_CF;'
            engine.execute(statement)
        except exc.ProgrammingError:
            print('Unknown table: '+series.ccvm+'_'+i.cod+'_CF')
        statement = 'DELETE FROM financials WHERE cod="'+i.cod+'";'
        engine.execute(statement)



if __name__ == "__main__":
    engine = create_engine('mysql+mysqlconnector://lins502:vandamme@lins502.mysql.pythonanywhere-services.com/lins502$earningsdb', pool_recycle=280)
    Base.metadata.create_all(bind=engine)
    engine.execute('SELECT * FROM companies').fetchall()

