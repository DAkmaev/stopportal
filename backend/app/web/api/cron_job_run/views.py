from typing import List, Type

from app.db.dao.cron_job import CronJobRunDao
from app.db.models.cron_job_run import CronJobRunModel
from app.web.api.cron_job_run.scheme import CronJobRunDTO, CronJobRunInputDTO
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/", response_model=List[CronJobRunDTO])
async def get_all_cron_job_run_models(
    limit: int = 10,
    offset: int = 0,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> List[CronJobRunModel]:
    return await cron_job_run_dao.get_all_cron_job_runs(limit=limit, offset=offset)


@router.get("/{cron_job_id}", response_model=CronJobRunDTO)
async def get_cron_job_run_models(
    cron_job_id: int,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> Type[CronJobRunModel]:
    return await cron_job_run_dao.get_cron_job_run(cron_job_id)


@router.post("/")
async def update_cron_job_run_model(
    new_cron_job_run_object: CronJobRunInputDTO,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> None:
    await cron_job_run_dao.update_cron_job_run(
        period=new_cron_job_run_object.period,
        name=new_cron_job_run_object.name,
    )


@router.delete("/{cron_job_run_id}", status_code=204)
async def delete_cron_job_run_model(
    cron_job_run_id: int,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> None:
    await cron_job_run_dao.delete_cron_job_run_model(cron_job_run_id)
