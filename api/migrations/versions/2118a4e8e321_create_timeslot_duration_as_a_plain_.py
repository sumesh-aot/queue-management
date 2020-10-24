"""Create timeslot_duration as a plain integer.

Revision ID: 2118a4e8e321
Revises: 0b452e9fb67c
Create Date: 2020-09-22 16:03:39.294540

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utc


# revision identifiers, used by Alembic.
revision = '2118a4e8e321'
down_revision = '0b452e9fb67c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('timeslot_duration', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service', 'timeslot_duration')
    # ### end Alembic commands ###
