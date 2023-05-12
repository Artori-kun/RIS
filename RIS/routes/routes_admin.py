from flask import render_template, url_for, flash, redirect, abort
from RIS import app, db, bcrypt, db
from RIS.forms import NewTechnician, UpdateTechnician
from RIS.models import Technician, User, Scan
from flask_login import current_user, login_required
import hashlib
import csv

from RIS.utils.utils import send_credentials

@app.route("/admin")
@login_required
def admin():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            # doctors = Doctor.query.filter_by(active=True)
            # receptionists = Receptionist.query.filter_by(active=True)
            technicians = Technician.query.filter_by(active=True)
            
            scans = db.session.query(
                Scan.patient_ssn,
                Scan.patient_name,
                Scan.patient_gender,
                Scan.patient_dob,
                Scan.date_taken,
                Scan.form_id,
                Scan.record_id,
                Scan.organ,
                Scan.conclusion,
                Technician.name
            ).filter(
                Scan.technician_id == Technician.id
            ).all()
            
            return render_template('admin.html', technicians=technicians, scans=scans)
        else:
            abort(403)
    return redirect(url_for('login'))


# @app.route("/admin/addDoctor", methods=['GET', 'POST'])
# @login_required
# def addDoctor():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'A':
#             form = NewDoctor()
#             if form.validate_on_submit():
#                 # id = int(str(uuid.uuid4().int)[:5])
#                 password = int(hashlib.sha1(
#                     form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
#                 mail = f'{password}@D.com'
#                 hashed_password = bcrypt.generate_password_hash(
#                     str(password)).decode('utf-8')
                
                
#                 doctor = Doctor(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
#                                 dob=form.dob.data, speciality=form.speciality.data, salary=form.salary.data, gender=0)
#                 user = User(id=password, username=password,
#                             email=mail, password=hashed_password)
#                 db.session.add(doctor)
#                 db.session.add(user)
#                 db.session.commit()
#                 send_credentials(form.email.data, mail,
#                                  password, form.name.data)
#                 with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
#                     csv_writer = csv.writer(csv_file)
#                     csv_writer.writerow([hashed_password])
#                 flash(
#                     f'Doctor has been created mail={mail}, password={password}', 'success')
#                 return redirect(url_for('admin'))
#             return render_template('superuser/addDoctor_su.html', title='Add Doctor', form=form)
#         else:
#             abort(403)


# @app.route("/admin/addReceptionist", methods=['GET', 'POST'])
# @login_required
# def addReceptionist():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'A':
#             form = NewReceptionist()
#             if form.validate_on_submit():
#                 # id = int(str(uuid.uuid4().int)[:5])
#                 password = int(hashlib.sha1(
#                     form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
#                 mail = f'{password}@R.com'
#                 hashed_password = bcrypt.generate_password_hash(
#                     str(password)).decode('utf-8')
                
                
#                 receptionist = Receptionist(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
#                                             dob=form.dob.data, salary=form.salary.data, gender=form.gender.data, address=form.address.data)
#                 user = User(id=password, username=password,
#                             email=mail, password=hashed_password)
#                 db.session.add(receptionist)
#                 db.session.add(user)
#                 db.session.commit()
#                 send_credentials(form.email.data, mail,
#                                  password, form.name.data)
#                 with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
#                     csv_writer = csv.writer(csv_file)
#                     csv_writer.writerow([hashed_password])
#                 flash(
#                     f'Receptionist has been created mail={mail}, password={password}', 'success')
#                 return redirect(url_for('admin'))
#             return render_template('superuser/addReceptionist_su.html', title='Add Receptionist', form=form)
#         else:
#             abort(403)


@app.route("/admin/addTechnician", methods=['GET', 'POST'])
@login_required
def addTechnician():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            form = NewTechnician()
            if form.validate_on_submit():
                # id = int(str(uuid.uuid4().int)[:5])
                password = int(hashlib.sha1(
                    form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
                mail = f'{form.username.data}@T.com'
                hashed_password = bcrypt.generate_password_hash(
                    str(password)).decode('utf-8')
                
                
                technician = Technician(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
                                        dob=form.dob.data, gender=form.gender.data)
                user = User(id=password, username=form.username.data,
                            email=mail, password=hashed_password)
                db.session.add(technician)
                db.session.add(user)
                db.session.commit()
                send_credentials(form.email.data, mail,
                                 password, form.name.data)
                with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([hashed_password])
                flash(
                    f'Technician has been created mail={mail}, password={password}', 'success')
                return redirect(url_for('admin'))
            return render_template('addTechnician.html', title='Add Technician', form=form)
        else:
            abort(403)


# @app.route("/admin/recep_patients/<int:id>/")
# @login_required
# def recep_patients(id):
#     if current_user.email[-5] == 'A':
#         receptionist = Receptionist.query.filter_by(id=id).first()
#         recep_patients = Scan.query.filter_by(receptionist=receptionist)
#         return render_template("recep_patients.html", p_data=recep_patients, name=receptionist.name)
#     else:
#         abort(403)


@app.route("/admin/tech_scans/<int:id>/")
@login_required
def tech_scans(id):
    if current_user.email[-5] == 'A':
        technician = Technician.query.filter_by(id=id).first()
        tech_scans = Scan.query.filter_by(technician=technician)
        return render_template("tech_scans.html", scans_data=tech_scans, name=technician.name)
    else:
        abort(403)


# @app.route("/admin/doc_patients/<int:id>/")
# @login_required
# def doc_patients(id):
#     if current_user.email[-5] == 'A':
#         doctor = Doctor.query.filter_by(id=id).first()
#         doc_patients = Scan.query.filter_by(doctor=doctor)
#         return render_template("doc_patients.html", p_data=doc_patients, name=doctor.name)
#     else:
#         abort(403)
        

# @app.route("/admin/doctor/edit/<int:id>/", methods = ['GET', 'POST'])
# @login_required
# def doc_update(id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'A':
#             doctor = Doctor.query.filter_by(id=id).first()
#             doctor_user = User.query.filter_by(id=id).first()
            
#             if doctor_user.active is False:
#                 abort(404)
            
#             form = UpdateDoctor(obj=doctor)
#             if form.validate_on_submit():
#                 form.populate_obj(doctor)
#                 db.session.add(doctor)
#                 db.session.commit()
                
#                 flash('Doctor updated', 'success')
                
#                 return redirect(url_for('admin'))
#             return render_template("superuser/addDoctor_su.html", form=form)
#         else:
#             abort(403)
#     else:
#         redirect(url_for('login'))

# @app.route("/admin/doctor/disable/<int:id>/", methods = ['GET', 'POST'])
# @login_required
# def doc_disable(id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'A':
#             doctor = Doctor.query.filter_by(id=id).first()
#             doctor_user = User.query.filter_by(id=id).first()
            
#             if doctor_user.active is False or doctor.active is False:
#                 abort(404)
#             else:
#                 doctor.active = False
#                 doctor_user.active = False
                
#                 db.session.add(doctor)
#                 db.session.add(doctor_user)
#                 db.session.commit()
                
#                 flash('Doctor disabled', 'success')
                
#                 return redirect(url_for('admin'))
#         else:
#             abort(403)
#     else:
#         redirect(url_for('login'))
        
@app.route("/admin/technician/edit/<int:id>/", methods = ['GET', 'POST'])
@login_required
def tech_update(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            tech = Technician.query.filter_by(id=id).first()
            tech_user = User.query.filter_by(id=id).first()
            
            if tech_user.active is False:
                abort(404)
            
            form = UpdateTechnician(obj=tech, username=tech_user.username)
            if form.validate_on_submit():
                form.populate_obj(tech)
                
                tech_user.username = form.username.data
                tech_user.email = f'{form.username.data}@T.com'
                
                # db.session.add(tech)
                # db.session.add(tech_user)
                db.session.commit()
                
                flash('Technician updated', 'success')
                
                return redirect(url_for('admin'))
            return render_template("addTechnician.html", form=form)
        else:
            abort(403)
    else:
        redirect(url_for('login'))

@app.route("/admin/technician/disable/<int:id>/", methods = ['GET', 'POST'])
@login_required
def tech_disable(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            tech = Technician.query.filter_by(id=id).first()
            tech_user = User.query.filter_by(id=id).first()
            
            if tech_user.active is False or tech.active is False:
                abort(404)
            else:
                tech.active = False
                tech_user.active = False
                
                # db.session.add(tech)
                # db.session.add(tech_user)
                db.session.commit()
                
                flash('Technician disabled', 'success')
                
                return redirect(url_for('admin'))
        else:
            abort(403)
    else:
        redirect(url_for('login'))
        
# @app.route("/admin/recep/edit/<int:id>/", methods = ['GET', 'POST'])
# @login_required
# def recep_update(id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'A':
#             recep = Receptionist.query.filter_by(id=id).first()
#             recep_user = User.query.filter_by(id=id).first()
            
#             if recep_user.active is False:
#                 abort(404)
            
#             form = UpdateReceptionist(obj=recep)
#             form.populate_obj(recep)
#             if form.validate_on_submit():
                
#                 db.session.add(recep)
#                 db.session.commit()
                
#                 flash('Receptionist updated', 'success')
                
#                 return redirect(url_for('admin'))
#             return render_template("superuser/addReceptionist_su.html", form=form)
#         else:
#             abort(403)
#     else:
#         redirect(url_for('login'))

# @app.route("/admin/recep/disable/<int:id>/", methods = ['GET', 'POST'])
# @login_required
# def recep_disable(id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'A':
#             recep = Receptionist.query.filter_by(id=id).first()
#             recep_user = User.query.filter_by(id=id).first()
            
#             if recep_user.active is False or recep.active is False:
#                 abort(404)
#             else:
#                 recep.active = False
#                 recep_user.active = False
                
#                 db.session.add(recep)
#                 db.session.add(recep_user)
#                 db.session.commit()
                
#                 flash('Receptionist disabled', 'success')
                
#                 return redirect(url_for('admin'))
#         else:
#             abort(403)
#     else:
#         redirect(url_for('login'))