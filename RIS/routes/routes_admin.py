from __future__ import print_function
from crypt import methods
from flask import render_template, url_for, flash, redirect, request, abort
from RIS import app, db, bcrypt
from RIS.forms import (NewDoctor, NewReceptionist, NewTechnician, UpdateDoctor, UpdateReceptionist, UpdateTechnician)
from RIS.models import Technician, User, Patient, Doctor, Receptionist, Scan
from flask_login import login_user, current_user, logout_user, login_required
import hashlib
import csv
import uuid

from RIS.utils import save_picture, save_profile_picture, calculate_age, send_reset_email, send_credentials

@app.route("/admin")
@login_required
def admin():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            doctors = Doctor.query.filter_by(active=True)
            receptionists = Receptionist.query.filter_by(active=True)
            technicians = Technician.query.filter_by(active=True)
            return render_template('admin.html', doctors=doctors, receptionists=receptionists, technicians=technicians)
        else:
            abort(403)
    return redirect(url_for('login'))


@app.route("/admin/addDoctor", methods=['GET', 'POST'])
@login_required
def addDoctor():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            form = NewDoctor()
            if form.validate_on_submit():
                # id = int(str(uuid.uuid4().int)[:5])
                password = int(hashlib.sha1(
                    form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
                mail = f'{password}@D.com'
                hashed_password = bcrypt.generate_password_hash(
                    str(password)).decode('utf-8')
                
                
                doctor = Doctor(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
                                dob=form.dob.data, speciality=form.speciality.data, salary=form.salary.data, gender=0)
                user = User(id=password, username=password,
                            email=mail, password=hashed_password)
                db.session.add(doctor)
                db.session.add(user)
                db.session.commit()
                send_credentials(form.email.data, mail,
                                 password, form.name.data)
                with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([hashed_password])
                flash(
                    f'Doctor has been created mail={mail}, password={password}', 'success')
                return redirect(url_for('admin'))
            return render_template('superuser/addDoctor_su.html', title='Add Doctor', form=form)
        else:
            abort(403)


@app.route("/admin/addReceptionist", methods=['GET', 'POST'])
@login_required
def addReceptionist():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            form = NewReceptionist()
            if form.validate_on_submit():
                # id = int(str(uuid.uuid4().int)[:5])
                password = int(hashlib.sha1(
                    form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
                mail = f'{password}@R.com'
                hashed_password = bcrypt.generate_password_hash(
                    str(password)).decode('utf-8')
                
                
                receptionist = Receptionist(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
                                            dob=form.dob.data, salary=form.salary.data, gender=form.gender.data, address=form.address.data)
                user = User(id=password, username=password,
                            email=mail, password=hashed_password)
                db.session.add(receptionist)
                db.session.add(user)
                db.session.commit()
                send_credentials(form.email.data, mail,
                                 password, form.name.data)
                with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([hashed_password])
                flash(
                    f'Receptionist has been created mail={mail}, password={password}', 'success')
                return redirect(url_for('admin'))
            return render_template('superuser/addReceptionist_su.html', title='Add Receptionist', form=form)
        else:
            abort(403)


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
                mail = f'{password}@T.com'
                hashed_password = bcrypt.generate_password_hash(
                    str(password)).decode('utf-8')
                
                
                technician = Technician(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
                                        dob=form.dob.data, salary=form.salary.data, gender=form.gender.data, address=form.address.data)
                user = User(id=password, username=password,
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
            return render_template('superuser/addTechnician_su.html', title='Add Technician', form=form)
        else:
            abort(403)


@app.route("/admin/recep_patients/<int:id>/")
@login_required
def recep_patients(id):
    if current_user.email[-5] == 'A':
        receptionist = Receptionist.query.filter_by(id=id).first()
        recep_patients = Scan.query.filter_by(receptionist=receptionist)
        return render_template("recep_patients.html", p_data=recep_patients, name=receptionist.name)
    else:
        abort(403)


@app.route("/admin/tech_patients/<int:id>/")
@login_required
def tech_patients(id):
    if current_user.email[-5] == 'A':
        technician = Technician.query.filter_by(id=id).first()
        tech_patients = Scan.query.filter_by(technician=technician)
        return render_template("tech_patients.html", p_data=tech_patients, name=technician.name)
    else:
        abort(403)


@app.route("/admin/doc_patients/<int:id>/")
@login_required
def doc_patients(id):
    if current_user.email[-5] == 'A':
        doctor = Doctor.query.filter_by(id=id).first()
        doc_patients = Scan.query.filter_by(doctor=doctor)
        return render_template("doc_patients.html", p_data=doc_patients, name=doctor.name)
    else:
        abort(403)
        

@app.route("/admin/doctor/edit/<int:id>/", methods = ['GET', 'POST'])
@login_required
def doc_update(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            doctor = Doctor.query.filter_by(id=id).first()
            doctor_user = User.query.filter_by(id=id).first()
            
            if doctor_user.active is False:
                abort(404)
            
            form = UpdateDoctor(obj=doctor)
            if form.validate_on_submit():
                form.populate_obj(doctor)
                db.session.add(doctor)
                db.session.commit()
                
                flash('Doctor updated', 'success')
                
                return redirect(url_for('admin'))
            return render_template("superuser/addDoctor_su.html", form=form)
        else:
            abort(403)
    else:
        redirect(url_for('login'))

@app.route("/admin/doctor/disable/<int:id>/", methods = ['GET', 'POST'])
@login_required
def doc_disable(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            doctor = Doctor.query.filter_by(id=id).first()
            doctor_user = User.query.filter_by(id=id).first()
            
            if doctor_user.active is False or doctor.active is False:
                abort(404)
            else:
                doctor.active = False
                doctor_user.active = False
                
                db.session.add(doctor)
                db.session.add(doctor_user)
                db.session.commit()
                
                flash('Doctor disabled', 'success')
                
                return redirect(url_for('admin'))
        else:
            abort(403)
    else:
        redirect(url_for('login'))
        
@app.route("/admin/technician/edit/<int:id>/", methods = ['GET', 'POST'])
@login_required
def tech_update(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            tech = Technician.query.filter_by(id=id).first()
            tech_user = User.query.filter_by(id=id).first()
            
            if tech_user.active is False:
                abort(404)
            
            form = UpdateTechnician(obj=tech)
            if form.validate_on_submit():
                form.populate_obj(tech)
                db.session.add(tech)
                db.session.commit()
                
                flash('Technician updated', 'success')
                
                return redirect(url_for('admin'))
            return render_template("superuser/addTechnician_su.html", form=form)
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
                
                db.session.add(tech)
                db.session.add(tech_user)
                db.session.commit()
                
                flash('Technician disabled', 'success')
                
                return redirect(url_for('admin'))
        else:
            abort(403)
    else:
        redirect(url_for('login'))
        
@app.route("/admin/recep/edit/<int:id>/", methods = ['GET', 'POST'])
@login_required
def recep_update(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            recep = Receptionist.query.filter_by(id=id).first()
            recep_user = User.query.filter_by(id=id).first()
            
            if recep_user.active is False:
                abort(404)
            
            form = UpdateReceptionist(obj=recep)
            if form.validate_on_submit():
                form.populate_obj(recep)
                db.session.add(recep)
                db.session.commit()
                
                flash('Receptionist updated', 'success')
                
                return redirect(url_for('admin'))
            return render_template("superuser/addDoctor_su.html", form=form)
        else:
            abort(403)
    else:
        redirect(url_for('login'))

@app.route("/admin/recep/disable/<int:id>/", methods = ['GET', 'POST'])
@login_required
def recep_disable(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            recep = Receptionist.query.filter_by(id=id).first()
            recep_user = User.query.filter_by(id=id).first()
            
            if recep_user.active is False or recep.active is False:
                abort(404)
            else:
                recep.active = False
                recep_user.active = False
                
                db.session.add(recep)
                db.session.add(recep_user)
                db.session.commit()
                
                flash('Receptionist disabled', 'success')
                
                return redirect(url_for('admin'))
        else:
            abort(403)
    else:
        redirect(url_for('login'))