"""empty message

Revision ID: 0f8c216c1e64
Revises: 5ff103db9365
Create Date: 2023-12-06 21:58:35.081989

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0f8c216c1e64"
down_revision = "5ff103db9365"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "stoch_decisions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("k", sa.Float(), nullable=True),
        sa.Column("d", sa.Float(), nullable=True),
        sa.Column("last_price", sa.Float(), nullable=True),
        sa.Column(
            "last_updated",
            sa.TIMESTAMP(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stoch_decisions_company_id"),
        "stoch_decisions",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stoch_decisions_period"), "stoch_decisions", ["period"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_stoch_decisions_period"), table_name="stoch_decisions")
    op.drop_index(op.f("ix_stoch_decisions_company_id"), table_name="stoch_decisions")
    op.drop_table("stoch_decisions")
    # ### end Alembic commands ###
