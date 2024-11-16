from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config


engine = create_engine(Config.DB_CONN_STR, echo=True)

Session = sessionmaker(engine)
