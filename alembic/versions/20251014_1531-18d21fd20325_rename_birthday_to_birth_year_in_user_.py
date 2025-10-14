"""rename birthday to birth_year in user table

Revision ID: 18d21fd20325
Revises: eefce945ef2f
Create Date: 2025-10-14 15:31:14.585801+09:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "18d21fd20325"
down_revision: Union[str, Sequence[str], None] = "eefce945ef2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("user", "birthday", new_column_name="birth_year", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("user", "birth_year", new_column_name="birthday", existing_type=sa.Integer(), nullable=True)
