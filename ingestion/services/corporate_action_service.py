from ingestion.models.corporate_action import CorporateAction
from ingestion.staging.database import CorporateActionRecord,get_session
import logging

logger = logging.getLogger(__name__)


class CorporateActionService:

    def ingest(self, raw_data: dict):
        # Step 1: Validate through Pydantic
        try:
            corp_action_data = CorporateAction(**raw_data)
        except Exception as e:
            logger.error("Validation failed: %s for %s", str(e), raw_data)
            return False, raw_data

        # Step 2: Convert to SQLAlchemy record
        record = CorporateActionRecord(
            action_id = corp_action_data.action_id,
            ticker = corp_action_data.ticker,
            action_type = corp_action_data.action_type,
            ratio = corp_action_data.ratio,
            index_id = corp_action_data.index_id,
            effective_date = corp_action_data.effective_date,
            announced_date = corp_action_data.announced_date,
            status = corp_action_data.status,
        )
        # Step 3: Insert into database
        try:
            with get_session() as session:
                session.add(record)
            return True, None
        except Exception as e:
            logger.error("DB insert failed: %s for %s", str(e), raw_data)
            return False, raw_data