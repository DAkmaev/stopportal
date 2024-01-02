import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.user import UserDAO
from backend.tests.utils.common import random_lower_string


@pytest.mark.anyio
async def test_get_user_models(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests getting a list of users models."""

    dao = UserDAO(dbsession)
    names = ["Bob", "Alan", "Lucy"]
    emails = ["Bob@ya.ru", "Alan@ya.ru", "Lucy@ya.ru"]

    for i in range(3):
        password = random_lower_string()
        await dao.create_user_model(names[i], emails[i], password)

    url = fastapi_app.url_path_for("get_user_models")
    response = await client.get(url)
    users = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(users) == len(names)
    assert all(user['name'] in names for user in users)
    assert all(user['email'] in emails for user in users)


# @pytest.mark.anyio
# async def test_get_user_me(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
#     user_token_headers: dict[str, str]
# ) -> None:
#     user = await create_test_user(dbsession)
#
#
#
#     url = fastapi_app.url_path_for("read_user_me")
#     response = await client.get(url, headers=user_token_headers)
#
#     result = response.json()
#     assert response.status_code == 403
#     assert result["detail"] == "Not enough permissions"
