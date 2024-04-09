from enum import Enum


class CompanyTypeEnum(str, Enum):  # noqa: WPS600
    MOEX = "MOEX"
    YAHOO = "YAHOO"
