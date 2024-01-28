"""empty message

Revision ID: 0aa670f3eab2
Revises: e1ba5093f7bc
Create Date: 2023-10-04 23:50:23.028409

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0aa670f3eab2"
down_revision = "e1ba5093f7bc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "stock_stop",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("stock_stop")
    # ### end Alembic commands ###