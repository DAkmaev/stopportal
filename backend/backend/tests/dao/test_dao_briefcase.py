import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dao.briefcases import BriefcaseDAO
from backend.tests.utils.common import create_test_company, create_test_briefcase


@pytest.mark.anyio
async def test_create_and_update_briefcase_item_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    COUNT = 10
    DIVIDENDS = 100.0
    NEW_DIVIDENDS = 150.0

    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession, need_add_strategy=True)
    briefcase = await create_test_briefcase(dbsession)

    # Create a briefcase item
    await briefcase_dao.create_briefcase_item_model(
        count=COUNT,
        dividends=DIVIDENDS,
        briefcase_id=briefcase.id,
        company_id=company.id,
        strategy_id=company.strategies[0].id
    )
    briefcase_items = await briefcase_dao.get_all_briefcase_items()
    assert len(briefcase_items) == 1
    new_briefcase_item = briefcase_items[0]
    assert new_briefcase_item is not None
    assert new_briefcase_item.count == COUNT
    assert new_briefcase_item.dividends == DIVIDENDS

    # Update the created briefcase item
    updated_briefcase_item = await briefcase_dao.update_briefcase_item_model(
        briefcase_item_id=new_briefcase_item.id, count=15, dividends=NEW_DIVIDENDS
    )
    assert updated_briefcase_item is not None
    assert updated_briefcase_item.count == 15  # Updated count
    assert updated_briefcase_item.dividends == NEW_DIVIDENDS  # Updated dividends

    # Clean up - delete the test briefcase item
    await briefcase_dao.delete_briefcase_item_model(updated_briefcase_item.id)

    # Ensure the briefcase item has been deleted
    remaining_items = await briefcase_dao.get_all_briefcase_items()
    assert updated_briefcase_item not in remaining_items


@pytest.mark.anyio
async def test_get_all_briefcases(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    # Get all briefcases
    existing_briefcases = await briefcase_dao.get_all_briefcases()
    assert isinstance(existing_briefcases, list)


@pytest.mark.anyio
async def test_get_briefcase_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    FILL_UP = 100
    briefcase_dao = BriefcaseDAO(dbsession)

    # Create a briefcase
    await briefcase_dao.create_briefcase_model(FILL_UP)
    briefcases = await briefcase_dao.get_all_briefcases()
    assert len(briefcases) == 1

    # Get a briefcase model by ID
    existing_briefcase = await briefcase_dao.get_briefcase_model(briefcases[0].id)
    assert existing_briefcase is not None
    assert existing_briefcase.id == briefcases[0].id
    assert existing_briefcase.fill_up == briefcases[0].fill_up


@pytest.mark.anyio
async def test_get_briefcase_item_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    # Create a briefcase item
    await briefcase_dao.create_briefcase_item_model(
        count=1, dividends=1, company_id=company.id, briefcase_id=briefcase.id
    )
    briefcase_items = await briefcase_dao.get_all_briefcase_items()
    assert len(briefcase_items) == 1

    # Get a briefcase model by ID
    existing_briefcase_item = await briefcase_dao.get_briefcase_item_model(briefcase_items[0].id)
    assert existing_briefcase_item is not None
    assert existing_briefcase_item.id is briefcase_items[0].id

@pytest.mark.anyio
async def test_get_briefcase_items_by_company(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    # Create briefcase items for the company
    await briefcase_dao.create_briefcase_item_model(
        count=1, dividends=1, company_id=company.id, briefcase_id=briefcase.id
    )
    await briefcase_dao.create_briefcase_item_model(
        count=2, dividends=2, company_id=company.id, briefcase_id=briefcase.id
    )

    # Get briefcase items for the company
    company_briefcase_items = await briefcase_dao.get_briefcase_items_by_company(company.id)
    assert len(company_briefcase_items) == 2

    # Make sure the retrieved items belong to the correct company
    for item in company_briefcase_items:
        assert item.company_id == company.id


@pytest.mark.anyio
async def test_get_briefcase_items_by_briefcase(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    # Create briefcase items for the briefcase
    await briefcase_dao.create_briefcase_item_model(
        count=1, dividends=1, company_id=company.id, briefcase_id=briefcase.id
    )
    await briefcase_dao.create_briefcase_item_model(
        count=2, dividends=2, company_id=company.id, briefcase_id=briefcase.id
    )

    # Get briefcase items for the briefcase
    briefcase_items = await briefcase_dao.get_briefcase_items_by_briefcase(briefcase.id)
    assert len(briefcase_items) == 2

    # Make sure the retrieved items belong to the correct briefcase
    for item in briefcase_items:
        assert item.briefcase_id == briefcase.id
