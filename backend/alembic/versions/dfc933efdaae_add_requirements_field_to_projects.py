"""add_requirements_field_to_projects

Revision ID: dfc933efdaae
Revises: 55b914fd2168
Create Date: 2025-10-28 16:52:54.831769

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "dfc933efdaae"
down_revision = "55b914fd2168"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add requirements JSONB field to projects table
    op.add_column(
        "projects",
        sa.Column(
            "requirements", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )


def downgrade() -> None:
    # Remove requirements field from projects table
    op.drop_column("projects", "requirements")
