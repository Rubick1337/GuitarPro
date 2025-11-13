import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv не установлен")

Base = declarative_base()


def create_database_connection():
    """
    Создает и возвращает подключение к базе данных
    """
    try:
        # Получаем параметры из переменных окружения
        db_name = os.getenv('DB_NAME', 'guitarpro_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')

        # Формируем строку подключения
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        print(f"🔗 Подключаемся к: {database_url.replace(db_password, '***')}")

        # Создаем движок
        engine = create_engine(database_url, echo=True)  # echo=True для отладки

        # Создаем фабрику сессий
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        print("✅ Подключение к PostgreSQL установлено")
        return engine, SessionLocal

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None, None