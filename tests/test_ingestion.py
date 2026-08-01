from unittest.mock import MagicMock, patch

from ingestion.services.corporate_action_service import CorporateActionService
from ingestion.services.reference_service import ReferenceService
from ingestion.services.tick_service import TickService


@patch("ingestion.services.tick_service.get_session")
def test_tick_ingestion(mock_session):
    mock_session.return_value.__enter__ = MagicMock()
    mock_session.return_value.__exit__ = MagicMock(return_value=False)

    service = TickService()
    success, error = service.ingest(
        {
            "ticker": "AAPL",
            "price": 189.52,
            "volume": 200,
            "tick_type": "TRADE",
            "source_id": "XNAS",
            "source_name": "NASDAQ",
            "timestamp": "2026-07-16T10:30:00.123456",
        }
    )
    assert success is True
    assert error is None


@patch("ingestion.services.tick_service.get_session")
def test_invalid_tick_rejected(mock_session):
    mock_session.return_value.__enter__ = MagicMock()
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    service = TickService()
    success, error = service.ingest(
        {
            "ticker": "AAPL",
            "price": -5.0,
            "volume": 200,
            "tick_type": "TRADE",
            "source_id": "XNAS",
            "source_name": "NASDAQ",
            "timestamp": "2026-07-16T10:30:00",
        }
    )
    assert success is False
    assert error is not None


@patch("ingestion.services.tick_service.get_session")
def test_invalid_tick_missing_field(mock_session):
    mock_session.return_value.__enter__ = MagicMock()
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    service = TickService()
    success, error = service.ingest(
        {
            "ticker": "AAPL",
            "price": 100.0,
        }
    )
    assert success is False
    assert error is not None


@patch("ingestion.services.reference_service.get_session")
def test_reference_ingestion(mock_session):
    mock_session.return_value.__enter__ = MagicMock()
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    service = ReferenceService()
    success, error = service.ingest(
        {
            "index_id": "SPX500",
            "effective_date": "2026-07-16",
            "version": 1,
            "constituents": [
                {
                    "ticker": "AAPL",
                    "company_name": "Apple Inc",
                    "weight": 0.072,
                    "shares_outstanding": 15204137000,
                    "sector": "Technology",
                },
                {
                    "ticker": "MSFT",
                    "company_name": "Microsoft Corp",
                    "weight": 0.068,
                    "shares_outstanding": 7432654000,
                    "sector": "Technology",
                },
            ],
        }
    )
    assert success is True
    assert error is None


@patch("ingestion.services.corporate_action_service.get_session")
def test_corporate_action_ingestion(mock_session):
    mock_session.return_value.__enter__ = MagicMock()
    mock_session.return_value.__exit__ = MagicMock(return_value=False)
    service = CorporateActionService()
    success, error = service.ingest(
        {
            "action_id": "CA-2026-001",
            "ticker": "AAPL",
            "action_type": "SPLIT",
            "ratio": 4.0,
            "effective_date": "2026-08-01",
            "announced_date": "2026-07-10",
            "status": "CONFIRMED",
        }
    )
    assert success is True
    assert error is None
