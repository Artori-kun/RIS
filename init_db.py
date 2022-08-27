from RIS import bcrypt, db
from RIS.models import User
import os

db.create_all()
# hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
# user = User(username='admin2', email='admin2@A.com', password=hashed_password)

# for docker
hashed_password = bcrypt.generate_password_hash(os.environ.get('ADMIN_PWD')).decode('utf-8')
user = User(username=os.environ.get('ADMIN_USERNAME'), 
            email=os.environ.get('ADMIN_EMAIL'), 
            password=hashed_password)


db.session.add(user)
db.session.commit()