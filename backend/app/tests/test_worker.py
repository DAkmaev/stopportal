from unittest.mock import patch, MagicMock

from app.db.dao.sync.ta_company_sync import TACompanySyncDAO
from app.db.dao.sync.ta_decisions_sync import TADecisionSyncDAO
from app.db.models.company import CompanyModel
from app.db.models.ta_decision import TADecisionModel
from app.schemas.ta import TAGenerateMessage
from app.services.ta_sync_service import TAService
from app.web.api.company.scheme import CompanyTypeEnum
from app.worker import send_telegram_task, generate_decision, ta_generate_task


@patch("app.worker.send_sync_tg_message")
def test_send_telegram_task(mock_send_sync_tg_message):
    message = "Test message"
    send_telegram_task(message)
    mock_send_sync_tg_message.assert_called_once_with(message)


# todo починить тест
# @patch("app.worker.get_sync_db_session")
# def test_generate_decision(mock_get_sync_db_session):
#     # Mocking dependencies
#     mock_db_session = MagicMock()
#     mock_get_sync_db_session.return_value.__enter__.return_value = mock_db_session
#     mock_company_dao = MagicMock(spec=TACompanySyncDAO)
#     mock_decision_dao = MagicMock(spec=TADecisionSyncDAO)
#     mock_ta_service = MagicMock(spec=TAService)
#
#     # Mocking data
#     message = TAGenerateMessage(tiker="AAPL", user_id=123, period="D",
#                                 send_message=True, update_db=True)
#     decisions = {1: TADecisionModel(id=1), 2: TADecisionModel(id=2)}
#     mocked_company = CompanyModel(type=CompanyTypeEnum.MOEX)
#
#     # Setting up mocks
#     mock_company_dao.get_company.return_value = mocked_company  # Mocking company retrieval
#     mock_ta_service.generate_ta_decision.return_value = decisions  # Mocking decision generation
#
#     # Calling the function
#     result = generate_decision(message)
#
#     # Assertions
#     assert len(
#         result) == 2  # Check if the function returns the expected number of decisions
#     assert all(isinstance(dec, dict) for dec in
#                result)  # Check if each decision is a dictionary
#     mock_ta_service.send_tg_messages.assert_called_once_with(
#         decisions.values())  # Check if send_tg_messages is called with correct arguments
#     mock_decision_dao.update_ta_models.assert_called_once_with(
#         decisions.values())  # Check if update_ta_models is called with correct arguments
#     mock_db_session.commit.assert_called_once()  # Check if the session is committed
#     assert mock_ta_service.generate_ta_decision.call_args[0][
#                0] == mock_company_dao.get_company.return_value  # Check if generate_ta_decision is called with the correct company

@patch("app.worker.TypeAdapter")
@patch("app.worker.generate_decision")
def test_ta_generate_task(mock_generate_decision, mock_type_adapter):
    # Mocking data
    mock_message = MagicMock()
    mock_type_adapter.return_value.validate_json.return_value = mock_message

    # Calling the task
    ta_generate_task("mocked_json_data")

    # Assertions
    mock_type_adapter.assert_called_once_with(TAGenerateMessage)
    mock_generate_decision.assert_called_once_with(mock_message)
