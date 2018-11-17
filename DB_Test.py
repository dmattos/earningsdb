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
    engine.execute(statement)

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
        engine.execute(statement)

# Create tables containing the company's financials
def tables_insert(series,engine):
    for i in series.DF:
        # Income Statement
        table_name = series.ccvm+'_'+i.cod+'_IS'
        try:
            df=i.IS.reset_index()
            dt={"index": NVARCHAR(length=50),"Descrição": NVARCHAR(length=255)}
            dt.update({col_name: FLOAT for col_name in df.columns[2:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(i.filing_date+' income statement already exists')
        table_name = series.ccvm+'_'+i.cod+'_BS'
        try:
            df=i.BS.reset_index()
            dt={"index": NVARCHAR(length=50),"Descrição": NVARCHAR(length=255)}
            dt.update({col_name: FLOAT for col_name in df.columns[2:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(i.filing_date+' balance sheet already exists')
        table_name = series.ccvm+'_'+i.cod+'_CF'
        try:
            df=i.CF.reset_index()
            dt={"index": NVARCHAR(length=50),"Descrição": NVARCHAR(length=255)}
            dt.update({col_name: FLOAT for col_name in df.columns[2:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print(i.filing_date+' cash flow already exists')

# Create tables containing the company's share price series
def prices_insert(series,engine):
    if(series.ticker_common != None and series.ticker_common != ''):
        table_name = series.ccvm+'_common_prices'
        try:
            df=series.common_prices.reset_index()
            dt={"date": DATETIME}
            dt.update({col_name: FLOAT for col_name in df.columns[1:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print('Common prices table already exists')
    if(series.ticker_preferred != None and series.ticker_preferred != ''):
        table_name = series.ccvm+'_preferred_prices'
        try:
            df=series.preferred_prices.reset_index()
            dt={"date": DATETIME}
            dt.update({col_name: FLOAT for col_name in df.columns[1:]})
            df.to_sql(table_name, con=engine,index=False,dtype=dt)
        except ValueError:
            print('Preferred prices table already exists')


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
    tmp = df.iloc[:,1]
    df=df.drop(['index','Date'],axis=1)
    df.index = tmp
    df.index.name = 'Date'
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

