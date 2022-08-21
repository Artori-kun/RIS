from RIS import bcrypt, db
from RIS.models import User

db.create_all()
hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
user = User(username='admin2', email='admin2@A.com', password=hashed_password)
db.session.add(user)
db.session.commit()