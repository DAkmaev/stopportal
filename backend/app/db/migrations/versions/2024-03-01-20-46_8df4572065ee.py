"""empty message

Revision ID: 8df4572065ee
Revises: 1d762e7a925c
Create Date: 2024-03-01 20:46:14.514628

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8df4572065ee"
down_revision = "1d762e7a925c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to companies and strategies tables
    op.add_column("companies", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("strategies", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("briefcases", sa.Column("user_id", sa.Integer(), nullable=True))

    # Create indexes
    op.create_index(op.f("ix_companies_user_id"), "companies", ["user_id"], unique=False)
    op.create_index(op.f("ix_strategies_user_id"), "strategies", ["user_id"], unique=False)
    op.create_index(op.f("ix_briefcases_user_id"), "briefcases", ["user_id"], unique=False)

    # Create foreign keys
    if op.get_context().dialect.name != "sqlite":
        op.create_foreign_key(None, "companies", "user", ["user_id"], ["id"])
        op.create_foreign_key(None, "strategies", "user", ["user_id"], ["id"])
        op.create_foreign_key(None, "briefcases", "user", ["user_id"], ["id"])


def downgrade() -> None:
    # Drop foreign keys
    if op.get_context().dialect.name != "sqlite":
        op.drop_constraint(None, "companies", type_="foreignkey")
        op.drop_constraint(None, "strategies", type_="foreignkey")
        op.drop_constraint(None, "briefcases", type_="foreignkey")

    # Drop columns
    op.drop_column("companies", "user_id")
    op.drop_column("strategies", "user_id")
    op.drop_column("briefcases", "user_id")

    # Drop indexes
    op.drop_index(op.f("ix_companies_user_id"), table_name="companies")
    op.drop_index(op.f("ix_strategies_user_id"), table_name="strategies")
    op.drop_index(op.f("ix_briefcases_user_id"), table_name="briefcases")

