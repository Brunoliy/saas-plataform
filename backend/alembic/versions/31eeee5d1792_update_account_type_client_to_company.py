"""update_account_type_client_to_company

Revision ID: 31eeee5d1792
Revises: 0001
Create Date: 2025-10-28 10:49:40.662631

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "31eeee5d1792"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update account_type from 'client' to 'company' for existing users."""
    # Update all users with account_type='client' to 'company'
    op.execute(
        "UPDATE users SET account_type = 'company' WHERE account_type = 'client'"
    )


def downgrade() -> None:
    """Rollback: Update account_type from 'company' back to 'client'."""
    # Rollback: Update all users with account_type='company' to 'client'
    op.execute(
        "UPDATE users SET account_type = 'client' WHERE account_type = 'company'"
    )
