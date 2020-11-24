"""add initial user review model

Revision ID: 819dc3e4d046
Revises:
Create Date: 2020-11-24 20:08:05.565433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '819dc3e4d046'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_review',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reviewer_id', sa.Integer(), nullable=False),
    sa.Column('reviewee_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_review')
    # ### end Alembic commands ###
