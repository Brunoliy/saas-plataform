"""merge_heads

Revision ID: 57fb0d64d5d
Revises: 0e442c50bf8, dfc933efdaae
Create Date: 2025-10-29 22:45:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "57fb0d64d5d"
down_revision = ("0e442c50bf8", "dfc933efdaae")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge migration - no changes needed."""
    pass


def downgrade() -> None:
    """Merge migration - no changes needed."""
    pass
