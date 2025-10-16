from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DATABASE_URL
from backend.app.models import Base, create_tables

# Criar engine do banco de dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        create_tables()
        print("Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        return False

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar banco automaticamente
if __name__ == "__main__":
    init_database()
