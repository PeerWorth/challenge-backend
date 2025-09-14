"""add unique constraint to user_consent table

Revision ID: 1a0ce3824700
Revises: 0637ac8571c0
Create Date: 2025-09-14 19:49:09.399544+09:00

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1a0ce3824700"
down_revision: Union[str, Sequence[str], None] = "0637ac8571c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Unique constraint 추가
    op.create_unique_constraint("uk_user_consent_user_event", "user_consent", ["user_id", "event"])


def downgrade() -> None:
    """Downgrade schema."""
    # Unique constraint 제거
    op.drop_constraint("uk_user_consent_user_event", "user_consent", type_="unique")
