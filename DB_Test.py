from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

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

if __name__ == "__main__":
    engine = create_engine('mysql+mysqlconnector://lins502:vandamme@lins502.mysql.pythonanywhere-services.com/lins502$earningsdb', pool_recycle=280)
    Base.metadata.create_all(bind=engine)
    engine.execute('SELECT * FROM companies').fetchall()