"""add_admin_role_to_account_type

Revision ID: 55b914fd2168
Revises: 855af8631231
Create Date: 2025-10-28 14:22:06.409281

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "55b914fd2168"
down_revision = "855af8631231"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'admin' value to the accounttype enum in PostgreSQL
    op.execute("ALTER TYPE accounttype ADD VALUE IF NOT EXISTS 'admin'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing values from enums directly
    # This would require more complex migration (recreate enum, update column, etc.)
    # For safety, we'll just warn that this cannot be automatically downgraded
    pass
