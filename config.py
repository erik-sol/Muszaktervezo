# Muszaktervezo/config.py
import os

# Konfigurációs beállítások
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///muszaktervezo.db")
