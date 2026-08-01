import logging

from ingestion.models.reference import ReferenceData
from ingestion.staging.database import (
    ConstituentRecord,
    ReferenceSnapshot,
    get_session,
)

logger = logging.getLogger(__name__)


class ReferenceService:

    def ingest(self, raw_data: dict):
        # Step 1: Validate through Pydantic
        try:
            ref_data = ReferenceData(**raw_data)
        except Exception as e:
            logger.error("Validation failed: %s for %s", str(e), raw_data)
            return False, raw_data

        # Step 2 & 3: Insert snapshot + constituents in one transaction
        try:
            with get_session() as session:
                # Create snapshot record
                snapshot = ReferenceSnapshot(
                    index_id=ref_data.index_id,
                    effective_date=ref_data.effective_date,
                    version=ref_data.version,
                )
                session.add(snapshot)
                session.flush()  # get the auto-generated id

                # Create constituent records linked to this snapshot
                for constituent in ref_data.constituents:
                    record = ConstituentRecord(
                        snapshot_id=snapshot.id,
                        ticker=constituent.ticker,
                        company_name=constituent.company_name,
                        weight=constituent.weight,
                        shares_outstanding=constituent.shares_outstanding,
                        sector=constituent.sector,
                    )
                    session.add(record)

            return True, None

        except Exception as e:
            logger.error("DB insert failed: %s for %s", str(e), raw_data)
            return False, raw_data
