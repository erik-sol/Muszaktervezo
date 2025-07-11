from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# NAS elérési út
#DB_PATH = r"N:\muszaktervezo.db"

# Helyi .db file
DB_PATH = r"muszaktervezo.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session():
    return SessionLocal()