from flask import jsonify, request

from db import db
from models.product import Products
from models.category import Categories
from models.company import Companies
from models.product_category_xref import products_categories_association_table
from models.warranty import Warranties


def _serialize_product(product, include_categories=True):
    categories_list = []
    if include_categories:
        for category in product.categories:
            categories_list.append(
                {
                    "category_id": category.category_id,
                    "category_name": category.category_name,
                }
            )

    company_dict = {
        "company_id": product.company.company_id,
        "company_name": product.company.company_name,
    }

    if product.warranty:
        warranty_dict = {
            "warranty_id": product.warranty.warranty_id,
            "warranty_months": product.warranty.warranty_months,
        }
    else:
        warranty_dict = {}

    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "description": product.description,
        "price": product.price,
        "active": product.active,
        "company": company_dict,
        "warranty": warranty_dict,
        "categories": categories_list,
    }


def add_product():
    post_data = request.form if request.form else request.get_json() or {}

    fields = ["product_name", "description", "price", "active", "company_id"]
    required_fields = ["product_name", "price", "company_id"]

    values = {}

    for field in fields:
        field_data = post_data.get(field)
        if field in required_fields and field_data is None:
            return jsonify({"message": f"{field} is required"}), 400
        values[field] = field_data

    company = db.session.query(Companies).filter(Companies.company_id == values["company_id"]).first()
    if not company:
        return jsonify({"message": f"company by id {values['company_id']} does not exist"}), 400

    new_product = Products(
        company_id=values["company_id"],
        product_name=values["product_name"],
        description=values.get("description"),
        price=values["price"],
        active=values.get("active", True),
    )

    try:
        db.session.add(new_product)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create product"}), 400

    return jsonify({"message": "product created", "result": _serialize_product(new_product)}), 201


def get_all_products():
    query = db.session.query(Products).all()
    products = []
    for product in query:
        products.append(_serialize_product(product))
    return jsonify({"message": "products found", "results": products}), 200


def get_active_products():
    query = db.session.query(Products).filter(Products.active.is_(True)).all()
    products = []
    for product in query:
        products.append(_serialize_product(product))
    return jsonify({"message": "active products found", "results": products}), 200


def get_product_by_id(product_id):
    query = db.session.query(Products).filter(Products.product_id == product_id).first()
    if not query:
        return jsonify({"message": f"product by id {product_id} does not exist"}), 404
    return jsonify({"message": "product found", "result": _serialize_product(query)}), 200


def get_products_by_company_id(company_id):
    products = db.session.query(Products).filter(Products.company_id == company_id).all()
    serialized = []
    for product in products:
        serialized.append(_serialize_product(product))
    return jsonify({"message": "products found for company", "results": serialized}), 200


def update_product_by_id(product_id):
    post_data = request.form if request.form else request.get_json() or {}
    product = db.session.query(Products).filter(Products.product_id == product_id).first()
    if not product:
        return jsonify({"message": f"product by id {product_id} does not exist"}), 404
    if "product_name" in post_data:
        product.product_name = post_data["product_name"]
    if "description" in post_data:
        product.description = post_data["description"]
    if "price" in post_data:
        product.price = post_data["price"]
    if "active" in post_data:
        product.active = post_data["active"]
    if "company_id" in post_data:
        company = db.session.query(Companies).filter(Companies.company_id == post_data["company_id"]).first()
        if not company:
            return jsonify({"message": f"company by id {post_data['company_id']} does not exist"}), 400
        product.company_id = post_data["company_id"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update product"}), 400

    return jsonify({"message": "product updated", "result": _serialize_product(product)}), 200


def delete_product_by_id(product_id):
    product = db.session.query(Products).filter(Products.product_id == product_id).first()
    if not product:
        return jsonify({"message": f"product by id {product_id} does not exist"}), 404

    try:
        db.session.execute(
            products_categories_association_table.delete().where(
                products_categories_association_table.c.product_id == product_id
            )
        )
        db.session.delete(product)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete product"}), 400

    return jsonify({"message": "product deleted"}), 200


def add_product_category_association():
    post_data = request.form if request.form else request.get_json() or {}

    product_id = post_data.get("product_id")
    category_id = post_data.get("category_id")

    if not product_id or not category_id:
        return (
            jsonify({"message": "product_id and category_id are required"}),
            400,
        )

    product = db.session.query(Products).filter(Products.product_id == product_id).first()
    if not product:
        return jsonify({"message": f"product by id {product_id} does not exist"}), 404
    category = db.session.query(Categories).filter(Categories.category_id == category_id).first()
    if not category:
        return jsonify({"message": f"category by id {category_id} does not exist"}), 404

    if category not in product.categories:
        product.categories.append(category)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create product/category association"}), 400

    return jsonify({"message": "product/category association created", "result": _serialize_product(product)}), 201
