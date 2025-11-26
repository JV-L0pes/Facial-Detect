from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from config import DATABASE_URL
from app.models import Base, create_tables

# Criar engine do banco de dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        create_tables()

        # Verificar se a coluna passage_count existe, se não, adicionar
        from sqlalchemy import text

        with engine.connect() as conn:
            # Verificar se a coluna existe
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if "passage_count" not in columns:
                print("🔄 Adicionando coluna passage_count à tabela users...")
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN passage_count INTEGER DEFAULT 0")
                )
                conn.commit()
                print("✅ Coluna passage_count adicionada com sucesso!")

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
