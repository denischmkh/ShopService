"""Append tables and verify columns

Revision ID: 040378057996
Revises: bc5edc69e217
Create Date: 2024-09-07 22:49:12.626084

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '040378057996'
down_revision: Union[str, None] = 'bc5edc69e217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('verified_email', sa.Boolean(), nullable=True))

    op.create_table(
        'verification_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, unique=True, nullable=False,
                  default=uuid.uuid4),
        sa.Column('verify_code', sa.DECIMAL(6, 0), nullable=False),
        sa.Column('expire_to', sa.DateTime, default=sa.text('CURRENT_TIMESTAMP + INTERVAL \'1 DAY\'')),
    )


def downgrade() -> None:
    op.drop_table('verification_codes')

    op.drop_column('users', 'email')
    op.drop_column('users', 'verified_email')
