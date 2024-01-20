import logging
import httpx

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dependencies import get_db_session

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
        self.scheduler = None

    async def check_ta(self, period: str):
        logger.debug('Проверка ta')

        last_run = CronJobRunDao().get_cron_job_run(period)
        logger.debug(last_run)

        try:
            logger.debug('.')
           # result = await CronJobRunDao().update_cron_job_run(period, 'CheckStoch')
           # httpx.post('http://127.0.0.1:8000/api/cron_job_run/', data={"period": "D", "name": "CheckStoch"}, timeout=30)
            await httpx.get(f'http://127.0.0.1:8000/api/ta/?period={period}&is_cron=1', timeout=30)
           #await CronJobRunDao().update_cron_job_run(period, 'CheckStoch')
           # return result
        except Exception as e:
            logger.error(e)

        logger.debug('Проверен ta.')

    def start(self):
        logger.info("Starting scheduler service.")
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.scheduler.add_job(self.check_stoch, args=['D'], trigger='interval', seconds=20)
        # self.scheduler.add_job(self.check_stoch, args=['D'], trigger='cron',
        #                        hour=9, max_instances=1)

        self.scheduler.add_job(self.check_stoch, args=['W'], trigger='cron',
                               day_of_week='fri', hour=23, minute=27, max_instances=1)
