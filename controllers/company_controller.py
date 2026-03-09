from flask import jsonify, request

from db import db
from models.company import Companies


def add_company():
    post_data = request.form if request.form else request.get_json() or {}

    fields = ["company_name"]
    required_fields = ["company_name"]

    values = {}

    for field in fields:
        field_data = post_data.get(field)

        if field in required_fields and not field_data:
            return jsonify({"message": f"{field} is required"}), 400

        values[field] = field_data

    new_company = Companies(values["company_name"])

    try:
        db.session.add(new_company)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Could not create company"}), 400

    company = {
        "company_id": new_company.company_id,
        "company_name": new_company.company_name,
    }

    return jsonify({"message": "company created", "result": company}), 201


def get_all_companies():
    query = db.session.query(Companies).all()
    company_list = []
    for company in query:
        company_dict = {
            "company_id": company.company_id,
            "company_name": company.company_name,
        }
        company_list.append(company_dict)
    return jsonify({"message": "companies found", "results": company_list}), 200


def get_company_by_id(company_id):
    query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    if not query:
        return jsonify({"message": f"company by id {company_id} does not exist"}), 404

    company = {
        "company_id": query.company_id,
        "company_name": query.company_name,
    }

    return jsonify({"message": "company found", "result": company}), 200


def update_company_by_id(company_id):
    post_data = request.form if request.form else request.get_json() or {}
    query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    if not query:
        return jsonify({"message": f"company by id {company_id} does not exist"}), 404

    query.company_name = post_data.get("company_name", query.company_name)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update record"}), 400

    updated_company_query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    company = {
        "company_id": updated_company_query.company_id,
        "company_name": updated_company_query.company_name,
    }

    return jsonify({"message": "company updated", "result": company}), 200


def delete_company_by_id(company_id):
    company_query = db.session.query(Companies).filter(Companies.company_id == company_id).first()
    if not company_query:
        return jsonify({"message": f"company by id {company_id} does not exist"}), 404

    try:
        db.session.delete(company_query)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete record"}), 400

    return jsonify({"message": "company deleted"}), 200
