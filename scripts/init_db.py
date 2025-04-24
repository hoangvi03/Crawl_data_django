from sqlalchemy import create_engine
from models import Base

engine = create_engine('postgresql://postgres:205812258@localhost/trangvang_db')
Base.metadata.create_all(engine)