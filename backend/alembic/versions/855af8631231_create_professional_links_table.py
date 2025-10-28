"""create_professional_links_table

Revision ID: 855af8631231
Revises: 3b12615ab738
Create Date: 2025-10-28 11:20:56.614533

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "855af8631231"
down_revision = "3b12615ab738"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create professional_links table."""
    op.create_table(
        "professional_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("professional_id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["professional_id"], ["professional_profiles.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_professional_links_professional_id",
        "professional_links",
        ["professional_id"],
    )


def downgrade() -> None:
    """Drop professional_links table."""
    op.drop_index("ix_professional_links_professional_id", "professional_links")
    op.drop_table("professional_links")
