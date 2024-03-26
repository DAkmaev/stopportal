from asyncio import sleep

from asgiref.sync import async_to_sync
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery import celery_app
from app.db.dao.companies import CompanyDAO
from app.db.dependencies import get_db_session
from app.services.ta_generate_service import TAGenerateService


# from app.services.ta_generate_service import TAGenerateService


async def generate_decision(
    name,
):

    # company_dao = CompanyDAO(dbsession)
    # ta_service = TAGenerateService(company_dao)
    # decision = await ta_service.generate_ta_decision('LKOH', 2, 'W')
    return f'Hello {name} 1!'


@celery_app.task
def dummy_task(
    name='Test',
):
    # decision = await ta_service.generate_ta_decision(tiker, user_id, period)
    # return f'Hello {name}! decision: {decision.decision.name}'
    result = async_to_sync(generate_decision)(name)
    return result

