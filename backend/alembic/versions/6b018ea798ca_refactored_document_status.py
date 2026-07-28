"""refactored document_status

Revision ID: 6b018ea798ca
Revises: 108b29de3651
Create Date: 2026-07-23 10:08:45.737553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6b018ea798ca'
down_revision: Union[str, Sequence[str], None] = '108b29de3651'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import alembic.op as op

def upgrade() -> None:
    """Upgrade schema."""
    # 1. Use an autocommit block to prevent transaction errors
    with op.get_context().autocommit_block():
        # 2. Add each value in a separate SQL statement
        op.execute("ALTER TYPE document_status ADD VALUE 'QUEUED'")
        op.execute("ALTER TYPE document_status ADD VALUE 'QUEUE_FAILED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Since Postgres cannot "REMOVE VALUE", you must use a migration teardown swap:
    
    # 1. Rename the existing enum type
    op.execute("ALTER TYPE document_status RENAME TO document_status_old")
    
    # 2. Re-create the type without the 'QUEUED' and 'QUEUE_FAILED' values
    op.execute("CREATE TYPE document_status AS ENUM ('UPLOADED', 'PROCESSING', 'INDEXED', 'FAILED')")
    
    # 3. Alter your table column to map to the new type
    op.execute(
        "ALTER TABLE documents ALTER COLUMN status TYPE document_status "
        "USING status::text::document_status"
    )
    
    # 4. Drop the old enum type safely
    op.execute("DROP TYPE document_status_old")
