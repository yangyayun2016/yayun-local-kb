"""
天机智能决策OS - 数据库连接层
默认 SQLite（开箱即用），生产环境切换 PostgreSQL：
  export TIANJI_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/tianji
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("TIANJI_DATABASE_URL", "sqlite:///./tianji.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
