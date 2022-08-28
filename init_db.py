from RIS import bcrypt, db
from RIS.models import User
from sqlalchemy_utils import database_exists, create_database
import os

db.create_all()
# hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
# user = User(username='admin2', email='admin2@A.com', password=hashed_password)

# for docker
try:
    hashed_password = bcrypt.generate_password_hash(os.environ.get('ADMIN_PWD')).decode('utf-8')
    user = User(username=os.environ.get('ADMIN_USERNAME'), 
                email=os.environ.get('ADMIN_EMAIL'), 
                password=hashed_password)


    db.session.add(user)
    db.session.commit()
except Exception as e:
    print("Oh shit: ")