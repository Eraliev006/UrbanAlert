"""delete all data from table

Revision ID: 0a8f2ff30fa9
Revises: daf9c14635b2
Create Date: 2025-04-28 04:55:58.473919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0a8f2ff30fa9'
down_revision: Union[str, None] = 'daf9c14635b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('DELETE FROM "user";')


def downgrade() -> None:
    """Downgrade schema."""
    pass
