from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "name": self.username,
            # do not serialize the password, its a security breach
        }
    
    

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    last_name=db.Column(db.String(120), unique=False, nullable=False)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    parish = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    mun = db.Column(db.String(40), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=True)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    number = db.Column(db.String(15), unique=False, nullable=False)
    ant_fam= db.Column(db.String(1000), unique=False, nullable=False)
    ant_per= db.Column(db.String(1000), unique=False, nullable=False)
    record = db.relationship("Record", backref="patient", lazy=True)

    def __repr__(self):
        return f"<Patient {self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "dni": self.dni,
            "last_name": self.last_name,
            "city": self.city,
            "parish": self.parish,
            "mun": self.mun,
            "date": self.date,
            "gender": self.gender,
            "number": self.number,
            "ant_fam": self.ant_fam,
            "ant_per": self.ant_per,
        }


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.String(1000), unique=False, nullable=False)
    recommendations=db.Column(db.String(1000), unique=False, nullable=False)
    treatment = db.Column(db.String(1000), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)
    diagnosis_diff = db.Column(db.String(1000), unique=False, nullable=False)
    diagnosis_eco = db.Column(db.String(1000), unique=False, nullable=False)    
    exams = db.Column(db.String(1000), unique=False, nullable=False)
    medications=db.Column(db.String(1000), unique=False, nullable=False)
    symtomps=db.Column(db.String(1000), unique=False, nullable=False)
    phy_exa=db.Column(db.String(1000), unique=False, nullable=False)
    signs=db.Column(db.String(1000), unique=False, nullable=False)
    type_pat=db.Column(db.String(30), unique=False, nullable=False)
    observations=db.Column(db.String(1000), unique=False, nullable=False)
    id_patient = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    record_obstr = db.relationship("Record_Obst", backref="record", lazy=True)
    pay = db.relationship("Pay", backref="record", lazy=True)

    def __repr__(self):
        return f"<Record {self.date}>"

    def serialize(self):
        return {
            "id": self.id,
            "diagnosis": self.diagnosis,
            "recommendations": self.recommendations,
            "treatment": self.treatment,
            "date": self.date,
            "diagnosis_diff": self.diagnosis_diff,
            "diagnosis_eco": self.diagnosis_eco,
            "exams": self.exams,
            "medications": self.medications,
            "symtomps": self.symtomps,
            "phy_exa": self.phy_exa,
            "signs": self.signs,
            "type_pat": self.type_pat,
            "observations": self.observations,


        }

class Record_Obst(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_births = db.Column(db.Integer, unique=False, nullable=False)
    num_abort = db.Column(db.Integer, unique=False, nullable=False)
    menst_date = db.Column(db.Date, unique=False, nullable=False)
    type_preg=db.Column(db.String(20), unique=False, nullable=False)
    id_record = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
 

    def __repr__(self):
        return f"<Record_Obst{self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "num_births": self.num_births,
            "num_abort": self.num_abort,
            "menst_date": self.menst_date,
            "type_preg": self.type_preg,

        }


class Pay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pesos = db.Column(db.Integer, unique=False, nullable=False)
    cash = db.Column(db.Integer, unique=False, nullable=False)
    pay_mov = db.Column(db.Float, unique=False, nullable=False)
    biopago = db.Column(db.Float, unique=False, nullable=False)
    point = db.Column(db.Float, unique=False, nullable=False)
    id_record = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
 

    def __repr__(self):
        return f"<Pay {self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "pesos": self.pesos,
            "cash": self.cash,
            "pay_mov": self.pay_mov,
            "biopago": self.biopago,
            "point": self.point,
            "id_record": self.id_record,

        }

