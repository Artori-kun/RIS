from datetime import datetime
from unicodedata import name
from RIS import bcrypt, db
from RIS.models import User, Receptionist
from sqlalchemy_utils import database_exists, create_database
import os

db.create_all()


# for docker
try:
    # hashed_password_admin = bcrypt.generate_password_hash('123456').decode('utf-8')
    # user = User(username='admin', email='admin@A.com', password=hashed_password_admin)
    hashed_password = bcrypt.generate_password_hash(os.environ.get('ADMIN_PWD')).decode('utf-8')
    user = User(username=os.environ.get('ADMIN_USERNAME'), 
                email=os.environ.get('ADMIN_EMAIL'), 
                password=hashed_password)

    hashed_password_base_recep = bcrypt.generate_password_hash('123456').decode('utf-8')
    base_recep_mail = 'base_recep@R.com'
    base_recep = Receptionist(id=1,
                              name='Base Receptionist',
                              ssn='00000000000000',
                              email='rezo.krifferson@gmail.com',
                              dob=datetime.utcnow(),
                              salary=100000,
                              gender='Null',
                              address='Null')
    base_recep_user = User(username='base_recep',
                           email=base_recep_mail,
                           password=hashed_password_base_recep)
    
    db.session.add(base_recep_user)
    db.session.add(base_recep)
    db.session.add(user)
    db.session.commit()
except Exception as e:
    print("Oh shit: ")