import logging
from functools import reduce

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from server.src.db.dao.briefcases import BriefcaseDAO
from server.src.db.db import get_session
from server.src.db.models.briefcase import RegistryOperationEnum

logger = logging.getLogger(__name__)


class BriefcaseService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def recalculate_share(
        self,
        company_id: int,
        briefcase_id: int,
    ):
        dao = BriefcaseDAO(session=self.session)
        registries = await dao.get_all_briefcase_registry(
            briefcase_id=briefcase_id,
            company_id=company_id,
            limit=1000,
        )

        total_count = await self._calculate_total_count(registries)
        await self._update_share_model(dao, company_id, briefcase_id, total_count)

    def _process_calculation(self, acc, registry):
        if registry.operation == RegistryOperationEnum.SELL:
            return acc - registry.count
        elif registry.operation == RegistryOperationEnum.BUY:
            return acc + registry.count

        return acc

    async def _calculate_total_count(self, registries):

        return reduce(self._process_calculation, registries, 0)

    async def _update_share_model(self, dao, company_id, briefcase_id, total_count):
        share = await dao.get_briefcase_share_model_by_company(
            company_id=company_id,
            briefcase_id=briefcase_id,
        )

        if total_count > 0:
            if share:
                await dao.update_briefcase_share_model(
                    share_id=share.id,
                    updated_fields={"count": total_count},
                )
            else:
                await dao.create_briefcase_share_model(
                    count=total_count,
                    company_id=company_id,
                    briefcase_id=briefcase_id,
                )
        elif share:
            await dao.delete_briefcase_share_model(share.id)
