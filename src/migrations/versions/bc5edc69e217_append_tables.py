"""Append tables

Revision ID: bc5edc69e217
Revises: 
Create Date: 2024-09-02 02:30:55.053408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc5edc69e217'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create 'users' table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
        sa.Column('username', sa.String(length=30), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('admin', sa.Boolean, nullable=True),
        sa.Column('active', sa.Boolean),
        sa.Column('created_at', sa.DateTime)
    )

    # Create 'categories' table
    op.create_table(
        'categories',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
        sa.Column('title', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime)
    )

    # Create 'store' table
    op.create_table(
        'store',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
        sa.Column('title', sa.String(length=30), nullable=False),
        sa.Column('description', sa.String(length=300), nullable=True),
        sa.Column('price', sa.DECIMAL(9, 2), nullable=False),
        sa.Column('image', sa.String, unique=True, nullable=True),
        sa.Column('discount', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('categories_id', sa.Uuid(as_uuid=True), nullable=True)
    )

    # Create 'baskets' table
    op.create_table(
        'baskets',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
        sa.Column('products_id', sa.Uuid(as_uuid=True)),  # ID from 'store' table
        sa.Column('users_id', sa.Uuid(as_uuid=True)),  # ID from 'users' table
        sa.Column('quantity', sa.Integer(), nullable=False)
    )

    # Add foreign keys
    op.create_foreign_key('fk_baskets_products', 'baskets', 'store', ['products_id'], ['id'])
    op.create_foreign_key('fk_baskets_users', 'baskets', 'users', ['users_id'], ['id'])
    op.create_foreign_key('fk_products_categories', 'store', 'categories', ['categories_id'], ['id'])

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('baskets')
    op.drop_table('store')
    op.drop_table('categories')
    op.drop_table('users')
