"""add publications review model

Revision ID: 9ef87188e5f1
Revises: cb7b2acb4725
Create Date: 2020-11-29 23:06:22.983288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ef87188e5f1'
down_revision = 'cb7b2acb4725'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'publication_review',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('publication_id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'booking_id', name='unique_publication_review_for_booking_id'
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('publication_review')
    # ### end Alembic commands ###
