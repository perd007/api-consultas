"""empty message

Revision ID: bf3097d7722b
Revises: 16629c0fd06d
Create Date: 2024-09-22 22:15:38.243454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf3097d7722b'
down_revision = '16629c0fd06d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.alter_column('dni',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=15),
               existing_nullable=False)
        batch_op.alter_column('number',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=15),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.alter_column('number',
               existing_type=sa.String(length=15),
               type_=sa.INTEGER(),
               existing_nullable=False)
        batch_op.alter_column('dni',
               existing_type=sa.String(length=15),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
