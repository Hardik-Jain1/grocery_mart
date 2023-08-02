from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import  bcrypt
from flask import jsonify
from datetime import datetime
from .models import *
from .validation import *


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = Users.query.filter_by(user_name=username).first()
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            return username


create_section_parser = reqparse.RequestParser()
create_section_parser.add_argument('section_name')

create_section_field = {
    'section_id':   fields.Integer,
    'section_name':    fields.String,
}

class SectionAPI(Resource):
    @marshal_with(create_section_field)
    def get(self):
        sections = Sections.query.all()
        return sections, 200

    @auth.login_required
    @marshal_with(create_section_field)
    def post(self):
        try:
            args = create_section_parser.parse_args()
            section_name = args.get("section_name", None)

            if section_name is None:
                raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="Section name is required")

            section = db.session.query(Sections).filter(Sections.section_name == section_name).first()
            if section:
                raise BusinessValidationError(status_code=409, error_code="BE1002", error_message="Section name already exist")  

            new_section = Sections(section_name=section_name)
            db.session.add(new_section)
            db.session.commit()

            return new_section
        
        except BusinessValidationError as bve:
            raise bve
        except Exception as e:
            raise InternalServerError(status_code=500)


class Section_idAPI(Resource):
    @marshal_with(create_section_field)
    def get(self, section_id):
            try:
                section = Sections.query.get(int(section_id))
                if section:
                    return  section
                else:
                    raise NotFoundError(status_code=404)
            except NotFoundError as nfe:
                raise nfe
            except Exception as e:
                raise InternalServerError(status_code=500)

    @auth.login_required
    @marshal_with(create_section_field)          
    def put(self, section_id):
        try:
            args = create_section_parser.parse_args()
            section_name = args.get("section_name",None)
            if section_name is None:
                raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="Section Name is required")
            section = Sections.query.filter_by(section_id=section_id).first()
            if section:
                section.section_name = section_name
                db.session.commit()
                updated_section = Sections.query.filter_by(section_id=section_id).first()
                return updated_section, 200              
            else:
                raise NotFoundError(status_code=404)

        except BusinessValidationError as bve:
            raise bve
        except NotFoundError as nfe:
            raise nfe
        except Exception as e:
            raise InternalServerError(status_code=500)

    @auth.login_required
    def delete(self, section_id):
        try:
            section = Sections.query.filter_by(section_id=section_id).first()
            if section:
                # products = Products.query.filter_by(section_id=section_id).all()
                # for product in products:
                #     db.session.delete(product)
                #     db.session.commit()
                    # enroll_obj=Enrollment.query.filter_by(course_id=course_obj.course_id).first()
                db.session.delete(section)
                db.session.commit()
                return "Successfully deleted", 200
            else:
                raise NotFoundError(status_code=404)
        except NotFoundError as nfe:
            raise nfe
        except Exception as e:
            raise InternalServerError(status_code=500)
    


create_product_parser = reqparse.RequestParser()
create_product_parser.add_argument('product_name')
create_product_parser.add_argument('rate_per_unit')
create_product_parser.add_argument('unit')
create_product_parser.add_argument('manufacture_date')
create_product_parser.add_argument('expiry_date')
create_product_parser.add_argument('section_id')


create_product_field = {
  "product_id": fields.Integer,
  "product_name": fields.String,
  "rate_per_unit": fields.Float,
  "unit": fields.String,
  "manufacture_date": fields.String,
  "expiry_date": fields.String,
  "section_id": fields.Integer
}

class ProductAPI(Resource):
    @marshal_with(create_product_field)
    def get(self):
        products = Products.query.all()
        return products, 200

    @auth.login_required
    @marshal_with(create_product_field)
    def post(self):
        try:
            args = create_product_parser.parse_args()
            product_name = args.get("product_name", None)
            rate_per_unit = args.get("rate_per_unit", None)
            unit = args.get("unit", None)
            manufacture_date = args.get("manufacture_date", None)
            expiry_date = args.get("expiry_date", None)
            section_id = args.get("section_id", None)


            if product_name is None:
                raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Product name is required")
            if rate_per_unit is None:
                raise BusinessValidationError(status_code=400, error_code="BE2002", error_message="Rate per unit is required")
            if manufacture_date is None:
                raise BusinessValidationError(status_code=400, error_code="BE2003", error_message="Manufacture date is required")
            if expiry_date is None:
                raise BusinessValidationError(status_code=400, error_code="BE2004", error_message="Expiry date is required")
            if section_id is None:
                raise BusinessValidationError(status_code=400, error_code="BE2005", error_message="Section id is required")
            
            product = Products.query.filter_by(product_name=product_name).first()
            if product:
                raise BusinessValidationError(status_code=409, error_code="BE2006", error_message="Product name already exist")
            else:
                manufacture_date = datetime.strptime(manufacture_date, "%Y-%m-%d").date()
                expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

                new_product = Products(product_name=product_name,
                                        rate_per_unit=rate_per_unit,
                                        manufacture_date=manufacture_date,
                                        expiry_date=expiry_date, 
                                        section_id=section_id, 
                                        unit=unit)
                db.session.add(new_product)
                db.session.commit()
                new_product = Products.query.filter_by(product_name=product_name).first()
                return new_product, 201

        except BusinessValidationError as bve:
            raise bve
        except Exception as e:
            raise InternalServerError(status_code=500)
        
class Product_idAPI(Resource):
    @marshal_with(create_product_field)
    def get(self, product_id):
            try:
                product = Products.query.filter_by(product_id=product_id).first()
                if product:
                    return product
                else:
                    raise NotFoundError(status_code=404)
            except NotFoundError as nfe:
                raise nfe
            except Exception as e:
                raise InternalServerError(status_code=500)

    @auth.login_required
    @marshal_with(create_product_field)          
    def put(self, product_id):
        try:
            args = create_product_parser.parse_args()
            product_name = args.get("product_name", None)
            rate_per_unit = args.get("rate_per_unit", None)
            unit = args.get("unit", None)
            manufacture_date = args.get("manufacture_date", None)
            expiry_date = args.get("expiry_date", None)
            section_id = args.get("section_id", None)


            if product_name is None:
                raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Product name is required")
            if rate_per_unit is None:
                raise BusinessValidationError(status_code=400, error_code="BE2002", error_message="Rate per unit is required")
            if unit is None:
                raise BusinessValidationError(status_code=400, error_code="BE2005", error_message="Unit is required")
            if manufacture_date is None:
                raise BusinessValidationError(status_code=400, error_code="BE2003", error_message="Manufacture date is required")
            if expiry_date is None:
                raise BusinessValidationError(status_code=400, error_code="BE2004", error_message="Expiry date is required")
            if section_id is None:
                raise BusinessValidationError(status_code=400, error_code="BE2005", error_message="Section id is required")
            
            product = Products.query.filter_by(product_id=product_id).first()
            if not product:
                    raise NotExistsError(status_code=404)            
            else:
                manufacture_date = datetime.strptime(manufacture_date, "%Y-%m-%d").date()
                expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

                product.product_name = product_name
                product.rate_per_unit = rate_per_unit
                product.unit = unit
                product.manufacture_date = manufacture_date
                product.expiry_date = expiry_date
                product.section_id = section_id

                db.session.commit()
                product = Products.query.filter_by(product_id=product_id).first()
                return product, 201

        except BusinessValidationError as bve:
            raise bve
        except NotFoundError as nfe:
            raise nfe
        except Exception as e:
            raise InternalServerError(status_code=500)

    @auth.login_required
    def delete(self, product_id):
        try:
            product = Products.query.filter_by(product_id=product_id).first()
            if product:
                db.session.delete(product)
                db.session.commit()
                return "Successfully deleted", 200
            else:
                raise NotFoundError(status_code=404)
        except NotFoundError as nfe:
            raise nfe
        except Exception as e:
            raise InternalServerError(status_code=500)