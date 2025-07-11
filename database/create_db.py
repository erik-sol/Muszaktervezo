# Muszaktervezo/database/create_db.py
from database.connection import engine
from models.base import Base
from models import user, shift

if __name__ == "__main__":
    print("\u2b06\ufe0f Adatb\u00e1zis inicializ\u00e1l\u00e1s...")
    Base.metadata.create_all(bind=engine)
    print("\u2705 K\u00e9sz!")
