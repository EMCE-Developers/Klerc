"""empty message

Revision ID: 446de33cf9de
Revises: 9b29726e8556
Create Date: 2022-12-10 11:17:33.390009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '446de33cf9de'
down_revision = '9b29726e8556'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cat_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_column('cat_id')

    # ### end Alembic commands ###
