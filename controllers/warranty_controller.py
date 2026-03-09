from flask import jsonify, request

from db import db
from models.warranty import Warranties
from models.product import Products


def add_warranty():
    post_data = request.form if request.form else request.get_json() or {}

    fields = ["warranty_months", "product_id"]
    required_fields = ["warranty_months", "product_id"]

    values = {}

    for field in fields:
        field_data = post_data.get(field)
        if field in required_fields and field_data is None:
            return jsonify({"message": f"{field} is required"}), 400
        values[field] = field_data

    product = db.session.query(Products).filter(Products.product_id == values["product_id"]).first()
    if not product:
        return jsonify({"message": f"product by id {values['product_id']} does not exist"}), 400

    if product.warranty:
        return (
            jsonify({"message": "product already has a warranty associated"}),
            400,
        )

    new_warranty = Warranties(
        warranty_months=values["warranty_months"],
        product_id=values["product_id"],
    )

    try:
        db.session.add(new_warranty)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create warranty"}), 400

    warranty = {
        "warranty_id": new_warranty.warranty_id,
        "warranty_months": new_warranty.warranty_months,
        "product_id": new_warranty.product_id,
    }

    return jsonify({"message": "warranty created", "result": warranty}), 201


def get_warranty_by_id(warranty_id):
    query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()
    if not query:
        return jsonify({"message": f"warranty by id {warranty_id} does not exist"}), 404

    warranty = {
        "warranty_id": query.warranty_id,
        "warranty_months": query.warranty_months,
        "product_id": query.product_id,
    }

    return jsonify({"message": "warranty found", "result": warranty}), 200


def update_warranty_by_id(warranty_id):
    post_data = request.form if request.form else request.get_json() or {}
    warranty = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()
    if not warranty:
        return jsonify({"message": f"warranty by id {warranty_id} does not exist"}), 404

    if "warranty_months" in post_data:
        warranty.warranty_months = post_data["warranty_months"]

    if "product_id" in post_data:
        product = db.session.query(Products).filter(Products.product_id == post_data["product_id"]).first()
        if not product:
            return jsonify({"message": f"product by id {post_data['product_id']} does not exist"}), 400
        if product.warranty and product.warranty.warranty_id != warranty_id:
            return jsonify({"message": "new product already has a different warranty"}), 400
        warranty.product_id = post_data["product_id"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update warranty"}), 400

    updated = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    result = {
        "warranty_id": updated.warranty_id,
        "warranty_months": updated.warranty_months,
        "product_id": updated.product_id,
    }

    return jsonify({"message": "warranty updated", "result": result}), 200


def delete_warranty_by_id(warranty_id):
    warranty = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()
    if not warranty:
        return jsonify({"message": f"warranty by id {warranty_id} does not exist"}), 404

    try:
        db.session.delete(warranty)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete warranty"}), 400

    return jsonify({"message": "warranty deleted"}), 200

