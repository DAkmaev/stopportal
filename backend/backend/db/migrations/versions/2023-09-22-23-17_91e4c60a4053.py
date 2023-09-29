"""empty message

Revision ID: 91e4c60a4053
Revises: 1f5dd8cb5de7
Create Date: 2023-09-22 23:17:19.156437

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "91e4c60a4053"
down_revision = "1f5dd8cb5de7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cron_job_run",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("last_run_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cron_job_run_period"), "cron_job_run", ["period"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_cron_job_run_period"), table_name="cron_job_run")
    op.drop_table("cron_job_run")
    # ### end Alembic commands ###
