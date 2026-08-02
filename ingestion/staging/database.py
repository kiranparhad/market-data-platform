import enum
import os
from contextlib import contextmanager
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()


@lru_cache
def get_engine():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")

    return create_engine(database_url)


@lru_cache
def get_session_factory():
    return sessionmaker(bind=get_engine())


class TickTypeEnum(str, enum.Enum):
    TRADE = "TRADE"
    BID = "BID"
    ASK = "ASK"


class TickRecord(Base):
    __tablename__ = "ticks"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "ticker",
            "timestamp",
            "tick_type",
            name="uq_tick_source_event",
        ),
        Index(
            "ix_ticks_ticker_timestamp",
            "ticker",
            "timestamp",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    volume = Column(Integer, nullable=False)
    tick_type = Column(Enum(TickTypeEnum), nullable=False)
    source_id = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)


class ReferenceSnapshot(Base):
    __tablename__ = "reference_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "index_id",
            "effective_date",
            "version",
            name="uq_reference_snapshot_version",
        ),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_id = Column(String, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    version = Column(Integer, nullable=False)


class ConstituentRecord(Base):
    __tablename__ = "constituents"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "ticker",
            name="uq_constituent_snapshot_ticker",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(
        Integer,
        ForeignKey("reference_snapshots.id"),
        nullable=False,
        index=True,
    )
    ticker = Column(String, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    weight = Column(Numeric(18, 12), nullable=False)
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
    ratio = Column(Numeric(20, 10), nullable=True)
    index_id = Column(String, nullable=True, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    announced_date = Column(Date, nullable=False)
    status = Column(Enum(Status), nullable=False)


@contextmanager
def get_session():
    session_factory = get_session_factory()
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    Base.metadata.create_all(get_engine())
    print("All tables created successfully.")
