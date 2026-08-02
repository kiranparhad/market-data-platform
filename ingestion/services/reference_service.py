import logging

from sqlalchemy.dialects.postgresql import insert

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

        # Step 2 & 3: Upsert snapshot + constituents in one transaction
        try:
            with get_session() as session:
                # Upsert snapshot
                snapshot_stmt = (
                    insert(ReferenceSnapshot)
                    .values(
                        index_id=ref_data.index_id,
                        effective_date=ref_data.effective_date,
                        version=ref_data.version,
                    )
                    .on_conflict_do_nothing(constraint="uq_reference_snapshot_version")
                    .returning(ReferenceSnapshot.id)
                )

                result = session.execute(snapshot_stmt)
                row = result.fetchone()

                if row:
                    # New snapshot was inserted
                    snapshot_id = row[0]
                else:
                    # Snapshot already exists — look up its id
                    existing = (
                        session.query(ReferenceSnapshot)
                        .filter_by(
                            index_id=ref_data.index_id,
                            effective_date=ref_data.effective_date,
                            version=ref_data.version,
                        )
                        .first()
                    )
                    snapshot_id = existing.id

                # Upsert each constituent
                for constituent in ref_data.constituents:
                    constituent_stmt = (
                        insert(ConstituentRecord)
                        .values(
                            snapshot_id=snapshot_id,
                            ticker=constituent.ticker,
                            company_name=constituent.company_name,
                            weight=constituent.weight,
                            shares_outstanding=constituent.shares_outstanding,
                            sector=constituent.sector,
                        )
                        .on_conflict_do_update(
                            constraint="uq_constituent_snapshot_ticker",
                            set_={
                                "weight": constituent.weight,
                                "shares_outstanding": constituent.shares_outstanding,
                                "company_name": constituent.company_name,
                                "sector": constituent.sector,
                            },
                        )
                    )
                    session.execute(constituent_stmt)

            return True, None

        except Exception as e:
            logger.error("DB insert failed: %s for %s", str(e), raw_data)
            return False, raw_data
