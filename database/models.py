from sqlalchemy import Boolean, Column, DateTime, Float, String, JSON

from database.connection import Base, engine


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float)
    status = Column(String)
    state = Column(JSON)
    work_now = Column(Boolean)
    last_game = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


Base.metadata.create_all(engine)
