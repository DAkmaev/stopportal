"""empty message

Revision ID: 5c7dcd539925
Revises: 
Create Date: 2024-11-14 19:24:27.929754

"""

from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4548b2e865f0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_name"), "user", ["name"], unique=False)
    op.create_table(
        "briefcases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fill_up", sa.Numeric(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_briefcases_user_id"), "briefcases", ["user_id"], unique=False
    )
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("tiker", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=True)
    op.create_index(op.f("ix_companies_tiker"), "companies", ["tiker"], unique=True)
    op.create_index(
        op.f("ix_companies_user_id"), "companies", ["user_id"], unique=False
    )
    op.create_table(
        "strategies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_strategies_name"), "strategies", ["name"], unique=True)
    op.create_index(
        op.f("ix_strategies_user_id"), "strategies", ["user_id"], unique=False
    )
    op.create_table(
        "briefcase_registry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column(
            "currency", sa.Enum("RUB", "USD", "EUR", name="currencyenum"), nullable=True
        ),
        sa.Column(
            "operation",
            sa.Enum("BUY", "SELL", "DIVIDENDS", name="registryoperationenum"),
            nullable=True,
        ),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(), nullable=True),
        sa.Column("price", sa.Numeric(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=True),
        sa.Column("briefcase_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["briefcase_id"],
            ["briefcases.id"],
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["strategy_id"],
            ["strategies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "briefcase_shares",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("briefcase_id", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["briefcase_id"],
            ["briefcases.id"],
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "companies_stop",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("period", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "companies_strategies",
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["strategy_id"],
            ["strategies.id"],
        ),
        sa.PrimaryKeyConstraint("company_id", "strategy_id"),
    )
    op.create_table(
        "stoch_decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("period", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("decision", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("k", sa.Float(), nullable=True),
        sa.Column("d", sa.Float(), nullable=True),
        sa.Column("last_price", sa.Float(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stoch_decisions_period"), "stoch_decisions", ["period"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_stoch_decisions_period"), table_name="stoch_decisions")
    op.drop_table("stoch_decisions")
    op.drop_table("companies_strategies")
    op.drop_table("companies_stop")
    op.drop_table("briefcase_shares")
    op.drop_table("briefcase_registry")
    op.drop_index(op.f("ix_strategies_user_id"), table_name="strategies")
    op.drop_index(op.f("ix_strategies_name"), table_name="strategies")
    op.drop_table("strategies")
    op.drop_index(op.f("ix_companies_user_id"), table_name="companies")
    op.drop_index(op.f("ix_companies_tiker"), table_name="companies")
    op.drop_index(op.f("ix_companies_name"), table_name="companies")
    op.drop_table("companies")
    op.drop_index(op.f("ix_briefcases_user_id"), table_name="briefcases")
    op.drop_table("briefcases")
    op.drop_index(op.f("ix_user_name"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    # ### end Alembic commands ###
