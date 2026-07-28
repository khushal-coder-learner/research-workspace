"""enable_pgvector_extension

Revision ID: 108b29de3651
Revises: f6551a020612
Create Date: 2026-07-15 19:48:40.821403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '108b29de3651'
down_revision: Union[str, Sequence[str], None] = 'f6551a020612'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")
