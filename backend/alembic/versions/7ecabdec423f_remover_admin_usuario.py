"""remover admin usuario

Revision ID: 7ecabdec423f
Revises: 6d80a5480493
Create Date: 2025-06-12 18:14:13.596132

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7ecabdec423f"
down_revision: str | None = "6d80a5480493"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("usuarios", "admin")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("usuarios", sa.Column("admin", sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###
