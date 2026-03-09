import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class Companies(db.Model):
    __tablename__ = "Companies"

    company_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = db.Column(db.String(), nullable=False, unique=True)

    products = db.relationship("Products", foreign_keys="[Products.company_id]", back_populates="company", cascade='all')

    def __init__(self, company_name):
        self.company_name = company_name
