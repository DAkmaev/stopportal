from typing import List

from app.db.models.briefcase import BriefcaseModel, BriefcaseShareModel
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session


class BriefcaseSyncDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_briefcase_model_by_user_id(self, user_id: int) -> BriefcaseModel:
        exist_statement = select(BriefcaseModel).where(
            BriefcaseModel.user_id == user_id,
        )

        briefcase = self.session.execute(exist_statement).scalars().one_or_none()

        if not briefcase:
            raise HTTPException(status_code=404, detail="Briefcase not found")

        return briefcase

    def get_all_briefcase_shares(self, briefcase_id: int) -> List[BriefcaseShareModel]:
        exist_statement = select(BriefcaseShareModel).where(
            BriefcaseShareModel.briefcase_id == briefcase_id,
        )

        return list(self.session.execute(exist_statement).scalars().fetchall())
