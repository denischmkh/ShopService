"""Append column users_id

Revision ID: c5c8f47a9f3d
Revises: 040378057996
Create Date: 2024-09-07 23:24:58.716616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5c8f47a9f3d'
down_revision: Union[str, None] = '040378057996'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('verification_codes', sa.Column('users_id', sa.UUID))


def downgrade() -> None:
    op.drop_column('verification_codes', 'users_id')
