"""add_client_profile_fields_and_client_links

Revision ID: 0e442c50bf8
Revises: 855af8631231
Create Date: 2025-10-29 22:30:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0e442c50bf8"
down_revision = "855af8631231"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add description and bio fields to client_profiles and create client_links table."""
    # Add description and bio columns to client_profiles
    op.add_column("client_profiles", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("client_profiles", sa.Column("bio", sa.Text(), nullable=True))

    # Create client_links table
    op.create_table(
        "client_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["client_id"], ["client_profiles.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_client_links_client_id",
        "client_links",
        ["client_id"],
    )


def downgrade() -> None:
    """Remove description and bio fields from client_profiles and drop client_links table."""
    # Drop client_links table
    op.drop_index("ix_client_links_client_id", "client_links")
    op.drop_table("client_links")

    # Drop columns from client_profiles
    op.drop_column("client_profiles", "bio")
    op.drop_column("client_profiles", "description")
