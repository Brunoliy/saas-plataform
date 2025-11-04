"""add_admin_role_to_account_type

Revision ID: 55b914fd2168
Revises: 855af8631231
Create Date: 2025-10-28 14:22:06.409281

"""

# revision identifiers, used by Alembic.
revision = "55b914fd2168"
down_revision = "855af8631231"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No database schema changes needed.
    # The account_type column is String(20), not a PostgreSQL ENUM.
    # The 'admin' value is validated at the application level via Python's AccountType enum.
    pass


def downgrade() -> None:
    # No database schema changes were made in upgrade, so no downgrade needed.
    pass
