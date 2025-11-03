"""update_proposal_status_to_uppercase

Revision ID: a162d8aeb9b2
Revises: 9afa730d5a92
Create Date: 2025-11-03 16:42:55.647580

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "a162d8aeb9b2"
down_revision = "9afa730d5a92"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update existing proposal status values from lowercase to UPPERCASE."""
    # Update all existing proposals to use UPPERCASE status values
    op.execute(
        """
        UPDATE proposals
        SET status = UPPER(status)
        WHERE status IN ('submitted', 'accepted', 'rejected')
    """
    )


def downgrade() -> None:
    """Revert proposal status values back to lowercase."""
    # Revert all proposals back to lowercase status values
    op.execute(
        """
        UPDATE proposals
        SET status = LOWER(status)
        WHERE status IN ('SUBMITTED', 'ACCEPTED', 'REJECTED')
    """
    )
