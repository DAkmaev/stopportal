from __future__ import annotations

from typing import List, Type

from _datetime import datetime
from app.db.dependencies import get_db_session
from app.db.models.cron_job_run import CronJobRunModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CronJobRunDao:
    """Class for accessing cron_job_run table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_all_cron_job_runs(
        self, limit: int, offset: int
    ) -> List[CronJobRunModel]:
        """
        Get all cron_job_run models with limit/offset pagination.

        :param limit: limit of cron_job_runs.
        :param offset: offset of cron_job_runs.
        :return: stream of cron_job_runs.
        """
        cron_job_runs = await self.session.execute(
            select(CronJobRunModel).limit(limit).offset(offset),
        )

        return list(cron_job_runs.scalars().fetchall())

    async def get_cron_job_run(self, id: int) -> Type[CronJobRunModel]:
        """
        Get cron_job_run models by id.

        :param id:
        :return: cron_job_run.
        """
        cron_job_run = await self.session.get(CronJobRunModel, id)

        if not cron_job_run:
            raise HTTPException(status_code=404, detail="Запись о джобе не найдена")

        return cron_job_run

    async def get_cron_job_run_by_params(
        self, period: str, name: str
    ) -> Type[CronJobRunModel]:
        """
        Get cron_job_run models by name and period.

        :param name:
        :param period:
        :return: cron_job_run.
        """
        cron_jobs_run = await self.session.execute(
            select(CronJobRunModel).where(
                CronJobRunModel.period == period, CronJobRunModel.name == name
            )
        )
        cron_job_run = cron_jobs_run.scalars().one_or_none()

        # if not cron_job_run:
        #     raise HTTPException(status_code=404, detail="Запись о джобе не найдена")

        return cron_job_run

    async def update_cron_job_run(self, period: str, name: str):
        """
        Update last run date

        :param period:
        :param name:
        :return: cron_job_run
        """
        exist_run_job = await self.get_cron_job_run_by_params(period, name)

        last_run_date = datetime.today()

        if exist_run_job is None:
            new_run = CronJobRunModel(
                period=period, name=name, last_run_date=last_run_date
            )
            self.session.add(new_run)
            return new_run

        exist_run_job.last_run_date = last_run_date

        return exist_run_job

    async def delete_cron_job_run_model(self, cron_job_run_id: int) -> None:
        """
        Delete cron_job_run in session.
        :param cron_job_run_id:
        """
        cron_job_run = await self.session.get(CronJobRunModel, cron_job_run_id)
        if not cron_job_run:
            raise HTTPException(
                status_code=404, detail="Информация о запуске джобы не найдена"
            )

        await self.session.delete(cron_job_run)
