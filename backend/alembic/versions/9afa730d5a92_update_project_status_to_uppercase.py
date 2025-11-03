"""update_project_status_to_uppercase

Revision ID: 9afa730d5a92
Revises: 57fb0d64d5d
Create Date: 2025-11-03 15:17:09.923498

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9afa730d5a92"
down_revision = "57fb0d64d5d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update existing project status values from lowercase to UPPERCASE."""
    # Update all existing projects to use UPPERCASE status values
    op.execute(
        """
        UPDATE projects
        SET status = UPPER(status)
        WHERE status IN ('open', 'in_progress', 'completed', 'cancelled')
    """
    )


def downgrade() -> None:
    """Revert project status values back to lowercase."""
    # Revert all projects back to lowercase status values
    op.execute(
        """
        UPDATE projects
        SET status = LOWER(status)
        WHERE status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
    """
    )
