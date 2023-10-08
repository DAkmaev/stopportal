from typing import List

from fastapi import APIRouter, Depends

from backend.db.dao.cron_job import CronJobRunDao
from backend.db.models.cron_job_run import CronJobRunModel
from backend.web.api.cron_job_run.scheme import (CronJobRunDTO, CronJobRunInputDTO)

router = APIRouter()


@router.get("/", response_model=List[CronJobRunDTO])
async def get_all_cron_job_run_models(
    limit: int = 10,
    offset: int = 0,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> List[CronJobRunModel]:
    """
    Retrieve all cron_job_run objects from the database.

    :param cron_job_run_dao: DAO for CronJobRun models.
    :param limit: limit of company objects, defaults to 10.
    :param offset: offset of company objects, defaults to 0.
    :return: list of company objects from database.
    """
    return await cron_job_run_dao.get_all_cron_job_runs(limit=limit, offset=offset)


@router.get("/{id}]", response_model=CronJobRunDTO)
async def get_cron_job_run_models(
    id: int,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> List[CronJobRunModel]:
    """
    Retrieve one cron_job_run object  from the database.

    :param cron_job_run_dao: DAO for CronJobRun models.
    :return: list of company objects from database.
    """
    return await cron_job_run_dao.get_cron_job_run(id)


@router.post("/")
async def update_cron_job_run_model(
    new_cron_job_run_object: CronJobRunInputDTO,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> None:
    """
    Update cron_job_run model in the database.

    :param new_cron_job_run_object.
    :param cron_job_run_dao: DAO for cron_job_run models.
    """
    await cron_job_run_dao.update_cron_job_run(
        period=new_cron_job_run_object.period,
        name=new_cron_job_run_object.name
    )


@router.delete("/{cron_job_run_id}", status_code=204)
async def delete_cron_job_run_model(
    cron_job_run_id: int,
    cron_job_run_dao: CronJobRunDao = Depends(),
) -> None:
    """
    Delete cron_job_run model from the database.
    :param cron_job_run_dao:
    :param cron_job_run_id:
    """

    await cron_job_run_dao.delete_cron_job_run_model(cron_job_run_id)
