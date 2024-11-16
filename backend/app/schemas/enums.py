from enum import Enum


class DecisionEnum(str, Enum):  # noqa: WPS600
    BUY = "BUY"
    SELL = "SELL"
    RELAX = "RELAX"
    UNKNOWN = "UNKNOWN"


class PeriodEnum(str, Enum):  # noqa: WPS600
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    ALL = "All"


class CompanyTypeEnum(str, Enum):  # noqa: WPS600
    MOEX = "MOEX"
    YAHOO = "YAHOO"
