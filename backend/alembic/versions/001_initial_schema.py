"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')

    # Base tables will be created via metadata create_all or alembic migrations
    pass


def downgrade() -> None:
    pass
