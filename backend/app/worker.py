from asyncio import sleep

from asgiref.sync import async_to_sync
from fastapi import Depends
from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.celery import celery_app
from app.db.dao.companies import CompanyDAO
from app.db.dependencies import get_sync_db_session
from app.db.models.company import CompanyModel
from app.db.models.cron_job_run import CronJobRunModel
from app.db.models.ta_decision import TADecisionModel
from app.services.ta_generate_service import TAGenerateService
from app.settings import settings


# from app.services.ta_generate_service import TAGenerateService


def generate_decision(
    name,
):
    sync_engine = create_engine(str(settings.db_sync_url), echo=True)
    sync_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine,
    )
    with sync_session() as db:
        company_statement = (
            select(CompanyModel)
            .where(CompanyModel.id == 1)
        )
        company = db.execute(company_statement).scalars().one_or_none()
        return f'Hello {company.name} 1!'


@celery_app.task
def dummy_task(
    name='Test',
):
    # decision = await ta_service.generate_ta_decision(tiker, user_id, period)
    # return f'Hello {name}! decision: {decision.decision.name}'
    result = generate_decision(name)
    return result

