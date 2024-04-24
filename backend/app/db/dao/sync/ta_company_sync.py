from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.company import CompanyModel


class TACompanySyncDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_company(self, tiker: str, user_id: int) -> CompanyModel:
        company_statement = select(CompanyModel).where(
            CompanyModel.tiker == tiker,
            CompanyModel.user_id == user_id,
        )
        return self.session.execute(company_statement).scalars().one_or_none()
