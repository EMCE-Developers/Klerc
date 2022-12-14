"""empty message

Revision ID: 14da9232dbb9
Revises: b6f4995591ec
Create Date: 2022-12-11 21:30:59.734832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14da9232dbb9'
down_revision = 'b6f4995591ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.drop_column('note_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.add_column(sa.Column('note_id', sa.INTEGER(), nullable=True))

    # ### end Alembic commands ###
