from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.utils.common import create_test_company, create_test_briefcase
from app.utils.ta.ta_sync_calculator import TACalculator
