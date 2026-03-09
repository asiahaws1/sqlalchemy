import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class Warranties(db.Model):
    __tablename__ = "Warranties"

    warranty_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warranty_months = db.Column(db.Integer(), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Products.product_id'), unique=True, nullable=False)

    product = db.relationship("Products", foreign_keys='[Warranties.product_id]', back_populates="warranty", uselist=False)

    def __init__(self, warranty_months, product_id):
        self.warranty_months = warranty_months
        self.product_id = product_id
