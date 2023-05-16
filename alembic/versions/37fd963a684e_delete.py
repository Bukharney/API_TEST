"""delete

Revision ID: 37fd963a684e
Revises: 3cdb988d1aca
Create Date: 2023-05-17 00:25:20.184558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "37fd963a684e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """DROP TABLE IF EXISTS 
            login_logout, 
            stocks, 
            brokers, 
            users, 
            accounts, 
            bank_tsc, 
            orders, 
            transactions, 
            news, 
            turnover,
            dividend
            CASCADE;
            """
        )
    )


def downgrade() -> None:
    pass
