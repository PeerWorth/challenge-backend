"""Initial migration with User and UserConsent tables

Revision ID: 40893359ccb6
Revises:
Create Date: 2025-09-09 17:54:28.862665+09:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "40893359ccb6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user table
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("social_id", sa.String(length=255), nullable=False),
        sa.Column("nickname", sa.String(length=255), nullable=True),
        sa.Column("birthday", sa.Date(), nullable=False),
        sa.Column("gender", sa.Boolean(), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, default=False),
    )

    # Create user_consent table
    op.create_table(
        "user_consent",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event", sa.String(length=255), nullable=False),
        sa.Column("agree", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    # Create indexes and unique constraints
    op.create_unique_constraint("uq_user_social_id", "user", ["social_id"])
    op.create_unique_constraint("uq_user_nickname", "user", ["nickname"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables (foreign keys and indexes will be dropped automatically)
    op.drop_table("user_consent")
    op.drop_table("user")
