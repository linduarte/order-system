"""adicionar itens no Pedido

Revision ID: 26bac5f0b4bf
Revises: 0e8028701bbf
Create Date: 2025-06-21 18:22:11.970959

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "26bac5f0b4bf"
down_revision: str | None = "0e8028701bbf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
