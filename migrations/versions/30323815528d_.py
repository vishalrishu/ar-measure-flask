"""empty message

Revision ID: 30323815528d
Revises: 
Create Date: 2021-09-30 16:42:50.625924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30323815528d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'measures', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'measures', type_='unique')
    # ### end Alembic commands ###
