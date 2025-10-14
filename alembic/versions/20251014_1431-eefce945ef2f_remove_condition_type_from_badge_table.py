"""remove condition_type from badge table

Revision ID: eefce945ef2f
Revises: 1cb812ff96f5
Create Date: 2025-10-14 14:31:57.864203+09:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eefce945ef2f"
down_revision: Union[str, Sequence[str], None] = "1cb812ff96f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("condition_type", "badge", type_="unique")
    op.drop_column("badge", "condition_type")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("badge", sa.Column("condition_type", sa.String(), nullable=False))
    op.create_unique_constraint("condition_type", "badge", ["condition_type"])
