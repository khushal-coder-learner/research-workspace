"""create documents table

Revision ID: 7d2d9c4c8b11
Revises: f848eb300b32
Create Date: 2026-07-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d2d9c4c8b11"
down_revision: Union[str, Sequence[str], None] = "f848eb300b32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


document_status = sa.Enum(
    "UPLOADED",
    "PROCESSING",
    "INDEXED",
    "FAILED",
    name="document_status",
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    document_status.create(bind, checkfirst=True)
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("documents")
    document_status.drop(op.get_bind(), checkfirst=True)
