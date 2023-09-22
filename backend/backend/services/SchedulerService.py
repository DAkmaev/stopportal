import logging
import httpx

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = None

    async def check_stoch(self, period: str):
        logger.debug('Проверка stoch')
        try:
            httpx.get(f'http://127.0.0.1:8000/api/stoch/?period={period}')
        except Exception as e:
            logger.error(e)

        logger.debug('Проверен stoch.')

    def start(self):
        logger.info("Starting scheduler service.")
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.scheduler.add_job(self.check_stoch, args=['D'], trigger='cron',
                               hour=9, max_instances=1)

        self.scheduler.add_job(self.check_stoch, args=['W'], trigger='cron',
                               day_of_week='mon', hour=9, minute=10, max_instances=1)
