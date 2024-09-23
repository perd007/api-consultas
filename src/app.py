"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Patient, Record, Record_Obst, Pay
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
#from models import Person

api = Flask(__name__)
api.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    api.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    api.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(api, db)
db.init_app(api)
CORS(api)
setup_admin(api)

# Handle/serialize errors like a JSON object
@api.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@api.route('/')
def sitemap():
    return generate_sitemap(api)

@api.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200



#login
#validamos al usuario y le asignamos un token
@api.route('/login', methods=['POST'])
def user_login():

    data = request.get_json()
    user= data.get('user', None)
    password= data.get('password', None)

    #validamos que el usurio exista
    user_exist= User.query.filter_by(username=user).first()
    if not user_exist:
        return jsonify({"error":"User not found"}), 404
    
    #obtenemos el password y lo comparamos
    password_check= check_password_hash(user_exist.password, password)
    if not password_check:
        return jsonify({"error":"Password incorrecto"}), 401
   
    #se crea el token
    token_data={"id": user_exist.id, "user": user_exist.username}
    token= create_access_token(token_data)
    return jsonify({"token": token}), 200



########### Endpoints de Usuario###################
#get all users
@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_user = [user.serialize() for user in users]
    return jsonify(serialized_user), 200

 #GET user by id
@api.route('/user/<int:id>', methods=['GET'])
#@jwt_required()
def get_user_by_id(id):
    current_user = User.query.get(id)
    if not current_user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(current_user.serialize()), 200

# create user
@api.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username", None)
    password= data.get("password", None)
     # validamos que el usuario no exista
    user_exist = User.query.filter_by(username=username).first()
    if user_exist:
        return jsonify({"error": "User exist"}), 404
    
    #si no existe continuamos
    hashed_password = generate_password_hash(password)

    try:
        new_user = User(username=username,  password=hashed_password, is_active=True)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(error.args), 500

# edit user
@api.route('/user/<int:id>', methods=['PUT'])
#@jwt_required()
def edit_user(id):
    data = request.get_json()
    username = data.get("username", None)
    password= data.get("password", None)

     # validamos que el usuario exista
    user_exist = User.query.filter_by(id=id).first()
    if not user_exist:
        return jsonify({"error": "User exist"}), 404
    
    #si no existe el paswword se le asigna su mismo valor
    if not password:
       password=user_exist.password

    #de los contrario se hashead el nuevo
    password = generate_password_hash(password)

     
    try:
        

        update_user = User.query.get(id)

        update_user.password= password
        update_user.username = username
        db.session.commit()
        return jsonify({"User": update_user.serialize()}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify(error), 500

#delete user
@api.route('/user/<int:id>', methods=['DELETE'])
#@jwt_required()
def delete_user_by_id(id):
    user_to_delete = User.query.get(id)

    if not user_to_delete:
        return jsonify({"error": "user not found"}), 404

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify("user deleted successfully"), 200

    except Exception as error:
        db.session.rollback()
        return error, 500


##########################CRUD PATIENT#########################################


# get patient by id
@api.route("/patient/<int:id>", methods=["GET"])
#@jwt_required()
def get_patient_by_id(id):
        current_patient = Patient.query.get(id)
        if not current_patient:
            return jsonify({"error": "patient not found"}), 404
        return jsonify(current_patient.serialize()), 200



# get patients
@api.route("/patients", methods=["GET"])
#@jwt_required()
def get_patients():
    patients = Patient.query.all()
    return jsonify({"patienst": [patient.serialize() for patient in patients]}), 200
   

# create a patient
@api.route("/patient", methods=["POST"])
def create_patient():
    data = request.get_json()
    name = data.get("name", None)
    last_name= data.get("last_name", None)
    dni = data.get("dni", None)
    parish = data.get("parish", None)
    mun = data.get("mun", None)
    city = data.get("city", None)
    date = data.get("date", None)
    gender = data.get("gender", None)
    number = data.get("number", None)
    ant_fam = data.get("ant_fam", None)
    ant_per = data.get("ant_per", None)

    # validamos que el patient no exista
    patient_exist = Patient.query.filter_by(dni=dni).first()
    if patient_exist:
        return jsonify({"error": "patient exist"}), 404

    
    try:
        new_patient = Patient(
            name=name,
            last_name=last_name,
            parish=parish,
            dni=dni,
            city=city,
            mun=mun,
            gender=gender,
            number=number,
            date=date,
            ant_fam=ant_fam,
            ant_per=ant_per,
     
        )
        db.session.add(new_patient)
        db.session.commit()

        return jsonify(new_patient.serialize()), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(error.args), 500


# edit a patient
@api.route("/patient/<int:id>", methods=["PUT"])
#@jwt_required()
def edit_patient(id):
    data = request.get_json()
    name = data.get("name", None)
    last_name= data.get("last_name", None)
    dni = data.get("dni", None)
    parish = data.get("parish", None)
    mun = data.get("mun", None)
    city = data.get("city", None)
    country = data.get("country", None)
    date = data.get("date", None)
    gender = data.get("gender", None)
    number = data.get("number", None)
    ant_fam = data.get("ant_fam", None)
    ant_per = data.get("ant_per", None)


    # validamos que el patient no exista

    patient_exist = Patient.query.filter_by(id=id).first()
    if not patient_exist:
        return jsonify({"error": "patient not exist"}), 404


    try:
        update_patient = Patient.query.get(id)
        if not update_patient:
            return jsonify({"error": "patient not found"}), 404

        update_patient.name = name
        update_patient.last_name = last_name
        update_patient.parish = parish
        update_patient.mun = mun
        update_patient.dni = dni
        update_patient.country = country
        update_patient.city = city
        update_patient.date = date
        update_patient.gender = gender
        update_patient.number = number
        update_patient.ant_fam = ant_fam
        update_patient.ant_per = ant_per
        db.session.commit()
        return jsonify({"Patient": update_patient.serialize()}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify(error), 500


# delete patient
@api.route("/patient/<int:id>", methods=["DELETE"])
#@jwt_required()
def delete_patient_by_id(id):
    patient_to_delete = Patient.query.get(id)

    if not patient_to_delete:
        return jsonify({"error": "patient not found"}), 404

    try:
        db.session.delete(patient_to_delete)
        db.session.commit()
        return jsonify("patient deleted successfully"), 200

    except Exception as error:
        db.session.rollback()
        return error, 500
    
     ##########################CRUD RECORD#########################################

#get all record
@api.route('/records', methods=['GET'])
def get_records():
    records = Record.query.all()
    serialized_user = [record.serialize() for record in records]
    return jsonify(serialized_user), 200


# get record by id
@api.route("/record/<int:id>", methods=["GET"])
#@jwt_required()
def get_record_by_id(id):
        record = Record.query.get(id)
        if not record:
            return jsonify({"error": "record not found"}), 404

        return jsonify(record.serialize()), 200


# get record by patient
@api.route("/record/patient/<int:id_patient>", methods=["GET"])
#@jwt_required()
def get_record_by_id_appointment(id_patient):

        records = Record.query.filter_by(id_patient=id_patient).all()
        if not records:
            return jsonify({"error": "records not found"}), 404
        return jsonify({"patients": [record.serialize() for record in records]}), 200




# create a record
@api.route("/record/<int:id_patient>/", methods=["POST"])
#@jwt_required()
def create_record(id_patient):
        data = request.get_json()
        date = data.get("date", None)
        diagnosis = data.get("diagnosis", None)
        treatment = data.get("treatment", None)
        recommendations = data.get("recommendations", None)
        diagnosis_diff = data.get("diagnosis_diff", None)
        diagnosis_eco = data.get("diagnosis_eco", None)    
        exams = data.get("exams", None)
        medications=data.get("medications", None)
        symtomps=data.get("symtomps", None)
        phy_exa=data.get("phy_exa", None)
        signs=data.get("signs", None)
        observations=data.get("observations", None)
        id_patient = id_patient

        try:
            new_record = Record(
                date=date,
                diagnosis=diagnosis,
                treatment=treatment,
                recommendations=recommendations,
                diagnosis_diff=diagnosis_diff,
                diagnosis_eco=diagnosis_eco,
                exams=exams,
                medications=medications,
                symtomps=symtomps,
                phy_exa=phy_exa,
                signs=signs,
                observations=observations,
                id_patient=id_patient,
            )
            db.session.add(new_record)
            db.session.commit()

            return jsonify(new_record.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500


# edict a record
@api.route("/record/<int:id>", methods=["PUT"])
#@jwt_required()
def edit_record(id):

        data = request.get_json()
        date = data.get("date", None)
        diagnosis = data.get("diagnosis", None)
        treatment = data.get("treatment", None)
        recommendations = data.get("recommendations", None)
        diagnosis_diff = data.get("diagnosis_diff", None)
        diagnosis_eco = data.get("diagnosis_eco", None)    
        exams = data.get("exams", None)
        medications=data.get("medications", None)
        symtomps=data.get("symtomps", None)
        phy_exa=data.get("phy_exa", None)
        signs=data.get("signs", None)
        observations=data.get("observations", None)
      

        # validamos que el record exista
        record_exist = Record.query.filter_by(id=id).first()
        if not record_exist:
            return jsonify({"error": "record not exist"}), 404

        try:
            update_record = Record.query.get(id)
            if not update_record:
                return jsonify({"error": "record not found"}), 404

            update_record.date = date
            update_record.diagnosis = diagnosis
            update_record.treatment = treatment
            update_record.recommendations = recommendations
            update_record.diagnosis_diff = diagnosis_diff
            update_record.diagnosis_eco = diagnosis_eco
            update_record.exams = exams
            update_record. medications = medications
            update_record.symtomps = symtomps
            update_record.phy_exa = phy_exa
            update_record.signs = signs
            update_record.observations = observations

            db.session.commit()
            return jsonify({"record": update_record.serialize()}), 200

        except Exception as error:
            db.session.rollback()
            return jsonify(error), 500



# delete record
@api.route("/record/<int:id>", methods=["DELETE"])
#@jwt_required()
def delete_record_by_id(id):
        record_to_delete = Record.query.get(id)
        if not record_to_delete:
            return jsonify({"error": "record not found"}), 404

        try:
            db.session.delete(record_to_delete)
            db.session.commit()
            return jsonify("record deleted successfully"), 200

        except Exception as error:
            db.session.rollback()
            return error, 500
   


##########################CRUD RECORD_OBSTETRIC###########################

# get records obstetrics
@api.route("/records/obstetric", methods=["GET"])
#@jwt_required()
def get_records_obstetric():

        records = Record_Obst.query.all()
        if not records:
            return jsonify({"error": "records obstetric not found"}), 404
        return jsonify({"patients": [record.serialize() for record in records]}), 200


# get record obstetric by id
@api.route("/record/obstetric/<int:id>", methods=["GET"])
#@jwt_required()
def get_record_obstetric_by_id(id):
        record = Record_Obst.query.get(id)
        if not record:
            return jsonify({"error": "record obstetric not found"}), 404

        return jsonify(record.serialize()), 200


# get record obstetric by record
@api.route("/record/obstetric/<int:id_record>", methods=["GET"])
#@jwt_required()
def get_record_obstetric_by_id_appointment(id_record):

        records = Record.query.filter_by(id_record=id_record).all()
        if not records:
            return jsonify({"error": "records obstetric not found"}), 404
        return jsonify({"patients": [record.serialize() for record in records]}), 200



# create a record obstetric
@api.route("/record/obstetric/<int:id_record>/", methods=["POST"])
#@jwt_required()
def create_record_obstetric(id_record):
        data = request.get_json()
        num_births = data.get("num_births", None)
        num_abort = data.get("num_abort", None)
        menst_date = data.get("menst_date", None)
        type_preg = data.get("type_preg", None)     

        try:
            new_record_obst = Record_Obst(
                num_births=num_births,
                num_abort=num_abort,
                menst_date=menst_date,
                type_preg=type_preg,
                id_record=id_record,
            )
            db.session.add(new_record_obst)
            db.session.commit()

            return jsonify(new_record_obst.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500


# edict a record
@api.route("/record/obstetric/<int:id>", methods=["PUT"])
#@jwt_required()
def edit_record_obstetric(id):
        data = request.get_json()
        num_births = data.get("num_births", None)
        num_abort = data.get("num_abort", None)
        menst_date = data.get("menst_date", None)
        type_preg = data.get("type_preg", None) 

        # validamos que el record exista
        record_exist = Record_Obst.query.filter_by(id=id).first()
        if not record_exist:
            return jsonify({"error": "record not exist"}), 404

        try:
            update_record = Record_Obst.query.get(id)
            if not update_record:
                return jsonify({"error": "record obstetric not found"}), 404

            update_record.num_births = num_births
            update_record.num_abort = num_abort
            update_record.menst_date = menst_date
            update_record.type_preg = type_preg

            db.session.commit()
            return jsonify({"record obstretic": update_record.serialize()}), 200

        except Exception as error:
            db.session.rollback()
            return jsonify(error), 500



# delete record obtretic
@api.route("/record/obstetric/<int:id>", methods=["DELETE"])
#@jwt_required()
def delete_record_obstetric_by_id(id):
        record_to_delete = Record_Obst.query.get(id)
        if not record_to_delete:
            return jsonify({"error": "record obstetric not found"}), 404

        try:
            db.session.delete(record_to_delete)
            db.session.commit()
            return jsonify("record obstetric deleted successfully"), 200

        except Exception as error:
            db.session.rollback()
            return error, 500
   

##########################CRUD PAY###########################

# get pay by id
@api.route("/pay/<int:id>", methods=["GET"])
#@jwt_required()
def get_pay_by_id(id):
        pay = Pay.query.get(id)
        if not pay:
            return jsonify({"error": "´pay not found"}), 404

        return jsonify(pay.serialize()), 200

#get all record
@api.route('/pays', methods=['GET'])
def get_pays():
    pays = Pay.query.all()
    serialized_pay = [pay.serialize() for pay in pays]
    return jsonify(serialized_pay), 200

# get pay by record
@api.route("/pay/record/<int:id_record>", methods=["GET"])
#@jwt_required()
def get_pay_by_id_record(id_record):

        pay = Pay.query.filter_by(id_record=id_record).all()
        if not pay:
            return jsonify({"error": "pay not found"}), 404
        return jsonify({"Pay": [pay.serialize() for record in pay]}), 200



# create a pay
@api.route("/pay/<int:id_record>/", methods=["POST"])
#@jwt_required()
def create_pay(id_record):
        data = request.get_json()
        pesos = data.get("pesos", None)
        cash = data.get("cash", None)
        pay_mov = data.get("pay_mov", None)
        biopago = data.get("biopago", None)     
        point = data.get("point", None)


        try:
            new_pay = Pay(
                pesos=pesos,
                cash=cash,
                pay_mov=pay_mov,
                biopago=biopago,
                point=point,
                id_record=id_record,
            )
            db.session.add(new_pay)
            db.session.commit()

            return jsonify(new_pay.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500


# edict a pay
@api.route("/pay/<int:id>", methods=["PUT"])
#@jwt_required()
def edit_pay(id):
        data = request.get_json()
        pesos = data.get("pesos", None)
        cash = data.get("cash", None)
        pay_mov = data.get("pay_mov", None)
        biopago = data.get("biopago", None)     
        point = data.get("point", None)

        # validamos que el pago exista
        pay_exist = Pay.query.filter_by(id=id).first()
        if not pay_exist:
            return jsonify({"error": "pay not exist"}), 404

        try:
            update_pay = Pay.query.get(id)
            if not update_pay:
                return jsonify({"error": "pay not found"}), 404

            update_pay.pesos = pesos
            update_pay.cash = cash
            update_pay.pay_mov = pay_mov
            update_pay.biopago = biopago
            update_pay.point= point


            db.session.commit()
            return jsonify({"pay": update_pay.serialize()}), 200

        except Exception as error:
            db.session.rollback()
            return jsonify(error), 500



# delete pay
@api.route("/pay/<int:id>", methods=["DELETE"])
#@jwt_required()
def delete_pay_by_id(id):
        pay_to_delete = Pay.query.get(id)
        if not pay_to_delete:
            return jsonify({"error": "pay not found"}), 404

        try:
            db.session.delete(pay_to_delete)
            db.session.commit()
            return jsonify("pay deleted successfully"), 200

        except Exception as error:
            db.session.rollback()
            return error, 500
   

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    api.run(host='0.0.0.0', port=PORT, debug=False)
