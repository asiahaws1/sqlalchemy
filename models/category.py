import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db
from models.product_category_xref import products_categories_association_table


class Categories(db.Model):
    __tablename__ = "Categories"

    category_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = db.Column(db.String(), nullable=False, unique=True)

    products = db.relationship("Products", secondary=products_categories_association_table, back_populates='categories')

    def __init__(self, category_name):
        self.category_name = category_name
