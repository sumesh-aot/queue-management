"""online_appointment_email_changes

Revision ID: d2bbfaeeb7d9
Revises: fc3fd3bab5bc
Create Date: 2020-04-27 11:55:55.265894

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utc


# revision identifiers, used by Alembic.
revision = 'd2bbfaeeb7d9'
down_revision = 'fc3fd3bab5bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('publicuser', sa.Column('send_reminders', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('publicuser', 'send_reminders')
    # ### end Alembic commands ###
