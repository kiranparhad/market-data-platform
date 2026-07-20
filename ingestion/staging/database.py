from sqlalchemy import (
    create_engine,
    ForeignKey,
    Column,
    String,
    Float,
    Integer,
    DateTime,
    Date,
    Enum,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
import enum

DATABASE_URL = "postgresql://kiran:localdev@localhost:5432/market_data"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class TickTypeEnum(str, enum.Enum):
    TRADE = "TRADE"
    BID = "BID"
    ASK = "ASK"


class TickRecord(Base):
    __tablename__ = "ticks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    tick_type = Column(Enum(TickTypeEnum), nullable=False)
    source_id = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)


class ReferenceSnapshot(Base):
    __tablename__ = "reference_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_id = Column(String, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    version = Column(Integer, nullable=False)


class ConstituentRecord(Base):
    __tablename__ = "constituents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(
        Integer, ForeignKey("reference_snapshots.id"), nullable=False, index=True
    )
    ticker = Column(String, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    shares_outstanding = Column(BigInteger, nullable=False)
    sector = Column(String, nullable=False)


class ActionType(str, enum.Enum):
    SPLIT = "SPLIT"
    ADDITION = "ADDITION"
    REMOVAL = "REMOVAL"


class Status(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"


class CorporateActionRecord(Base):
    __tablename__ = "corporate_actions"

    action_id = Column(String, primary_key=True)
    ticker = Column(String, nullable=False, index=True)
    action_type = Column(Enum(ActionType), nullable=False)
    ratio = Column(Float, nullable=True)
    index_id = Column(String, nullable=True, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    announced_date = Column(Date, nullable=False)
    status = Column(Enum(Status), nullable=False)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    # from sqlalchemy.schema import CreateTable
    # print(CreateTable(ConstituentRecord.__table__))
    print("All tables created successfully.")
