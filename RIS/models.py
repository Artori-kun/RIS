from datetime import datetime
from RIS import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# class Doctor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), unique=False, nullable=False)
#     ssn = db.Column(db.String(14), unique=True, nullable=False)
#     dob = db.Column(db.DateTime, nullable=False)
#     speciality = db.Column(db.String(20), nullable=False)
#     salary = db.Column(db.Integer, nullable=False, default=5000)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     gender = db.Column(db.String(6), nullable=False)
#     scans = db.relationship('Scan', backref='doctor', lazy=True)
#     active = db.Column(db.Boolean, nullable=False, default=True)

#     def __repr__(self):
#         return f"User('{self.name}', '{self.email}', '{self.ssn}')"


# class Patient(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), unique=False, nullable=False)
#     ssn = db.Column(db.String(14), unique=True, nullable=False)
#     date_created = db.Column(db.DateTime, nullable=False, default = datetime.utcnow())
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     gender = db.Column(db.String(6), nullable=False)
#     address = db.Column(db.String(200))
#     dob = db.Column(db.DateTime, nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     scans = db.relationship('Scan', backref='patient', lazy=True)
    
#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}')"

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    patient_ssn = db.Column(db.String(12), unique=False, nullable=True)
    patient_name = db.Column(db.String(50), unique=False, nullable=False)
    patient_gender = db.Column(db.String(10), nullable=False)
    patient_dob = db.Column(db.DateTime, nullable=False)
    
    record_id = db.Column(db.String(8), unique=True, nullable=False)
    form_id = db.Column(db.String(8), unique=True, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.today())
    organ = db.Column(db.String(20), nullable=False)
    thickness = db.Column(db.Numeric(precision=5, scale=3), nullable=False)
    encrypt_id = db.Column(db.String(33), unique=True, nullable=False)
    conclusion = db.Column(db.Text, nullable=True)
    contrast_injection = db.Column(db.Boolean, nullable=False, default=False)
    
    series_id = db.Column(db.Text, nullable=True, default="UNKNOWN")
    profile_image = db.Column(db.Text, nullable=True, default='default.jpg')
    
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'), nullable=False)
    # def repr(self):
    #     return f"Scan('{self.date}')"

# class Receptionist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), unique=False, nullable=False)
#     ssn = db.Column(db.String(14), unique=True, nullable=False)
#     dob = db.Column(db.DateTime, nullable=False)
#     date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     gender = db.Column(db.String(6), nullable=False)
#     address = db.Column(db.String(200))
#     salary = db.Column(db.Integer, nullable=False, default=5000)
#     scans = db.relationship('Scan', backref='receptionist', lazy=True)
#     active = db.Column(db.Boolean, nullable=False, default=True)



class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    ssn = db.Column(db.String(14), nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default = datetime.utcnow())
    email = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    # address = db.Column(db.String(200))
    # salary = db.Column(db.Integer, nullable=False, default=5000)
    scans = db.relationship('Scan', backref='technician', lazy=True)
    active = db.Column(db.Boolean, nullable=False, default=True)