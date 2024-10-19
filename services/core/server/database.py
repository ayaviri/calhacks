import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pg_user = os.environ.get("POSTGRES_USER")
pg_password = os.environ.get("POSTGRES_PASSWORD")
pg_host = os.environ.get("PGHOST")
pg_port = os.environ.get("PGPORT")
pg_db = os.environ.get("POSTGRES_DB")
db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
engine = create_engine(db_url)
Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
