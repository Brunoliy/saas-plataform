"""add_bio_field_to_professional_profiles

Revision ID: 3b12615ab738
Revises: 31eeee5d1792
Create Date: 2025-10-28 11:12:15.469435

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '3b12615ab738'
down_revision = '31eeee5d1792'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add bio field to professional_profiles table."""
    op.add_column(
        "professional_profiles",
        sa.Column("bio", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Remove bio field from professional_profiles table."""
    op.drop_column("professional_profiles", "bio")
