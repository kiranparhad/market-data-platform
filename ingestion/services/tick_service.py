import logging

from sqlalchemy.dialects.postgresql import insert

from ingestion.models.tick import TickEvent
from ingestion.staging.database import TickRecord, get_session

logger = logging.getLogger(__name__)


class TickService:

    def ingest(self, raw_data: dict):
        try:
            tick_data = TickEvent(**raw_data)
        except Exception as e:
            logger.error("Validation failed: %s for %s", str(e), raw_data)
            return False, raw_data

        try:
            with get_session() as session:
                stmt = (
                    insert(TickRecord)
                    .values(
                        ticker=tick_data.ticker,
                        price=tick_data.price,
                        volume=tick_data.volume,
                        tick_type=tick_data.tick_type,
                        source_id=tick_data.source_id,
                        source_name=tick_data.source_name,
                        timestamp=tick_data.timestamp,
                    )
                    .on_conflict_do_nothing(constraint="uq_tick_source_event")
                )
                session.execute(stmt)
            return True, None
        except Exception as e:
            logger.error("DB insert failed: %s for %s", str(e), raw_data)
            return False, raw_data
