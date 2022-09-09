from __future__ import print_function
from flask import render_template, url_for, flash, redirect, request, abort, json
from RIS import app, db, bcrypt, mail
from RIS.forms import (LoginForm, ReportForm, NewDoctor, ResetPasswordForm, NewPatient,
                       PatientScanForm, UploadScanForm, NewReceptionist, NewTechnician)
from RIS.models import Technician, User, Patient, Doctor, Receptionist, Scan
from flask_login import login_user, current_user, logout_user, login_required
import hashlib
import csv


from RIS.utils import save_picture, save_profile_picture, calculate_age, send_reset_email, send_credentials
# ---------------------------- Start Util Functions ------------------------------------#
#                   In this Section are the helper utility functions
# --------------------------------------------------------------------------------------#






# -------------------------- End Util Functions-----------------------------------------#

# ---------------------------- Start Util Routes ---------------------------------------#
#                   In this Section are the helper utility routes
# --------------------------------------------------------------------------------------#


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            return redirect(url_for('admin'))
        elif current_user.email[-5] == 'D':
            return redirect(url_for('home'))
        elif current_user.email[-5] == 'R':
            return redirect(url_for('recep'))
        elif current_user.email[-5] == 'T':
            return redirect(url_for('technician'))
        elif current_user.email[-5] == 'P':
            return redirect(url_for('patient_profile'))
    form = LoginForm()
    if form.validate_on_submit():
        with open('passwords.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                if bcrypt.check_password_hash(line[0], form.password.data):
                    user = User.query.filter_by(email=form.email.data).first()
                    if form.email.data[-5] == 'D':
                        email = Doctor.query.filter_by(
                            id=form.password.data).first()
                    elif form.email.data[-5] == 'R':
                        email = Receptionist.query.filter_by(
                            id=form.password.data).first()
                    elif form.email.data[-5] == 'T':
                        email = Technician.query.filter_by(
                            id=form.password.data).first()
                    elif form.email.data[-5] == 'P':
                        email = Patient.query.filter_by(
                            id=form.password.data).first()
                    else:
                        raise('Email is not valid')
                    send_reset_email(user, email.email)
                    flash(
                        'An email has been sent with instructions to reset your password', 'info')
                    return redirect(url_for('login'))
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.email[-5] == 'A':
                return redirect(url_for('admin'))
            elif current_user.email[-5] == 'D':
                return redirect(url_for('home'))
            elif current_user.email[-5] == 'R':
                return redirect(url_for('recep'))
            elif current_user.email[-5] == 'T':
                return redirect(url_for('technician'))
            elif current_user.email[-5] == 'P':
                return redirect(url_for('patient_profile'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

# -------------------------- End Util Routes ---------------------------------------------#

# ------------------------- Start Landing Page Routes -----------------------------------#
#                   In this Section are routes of the end user
# --------------------------------------------------------------------------------------#


@app.route("/")
def root():
    return redirect(url_for('login'))

# ------------------------- End Landing Page Route --------------------------------------#


# ---------------------------- Start Doctor Routes --------------------------------------#
#                   In this Section are routes of the doctors
# ---------------------------------------------------------------------------------------#
@app.route("/doctor")
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'D':
            all_patients_scans = Scan.query.filter_by(
                doctor=current_user).all()
            print(url_for('home'))
            return render_template("doctor.html", p_data=all_patients_scans)
        else:
            abort(403)


@app.route("/doctors/report/<scan_id>", methods=['GET', 'POST'])
@login_required
def Report(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    scanimage = url_for('static', filename='patients_scans/' + scan.image_file)
    form = ReportForm()
    if form.validate_on_submit():
        scan.report_title = form.title.data
        scan.report_content = form.content.data
        scan.report_summary = form.summary.data
        db.session.commit()
        flash('Your Report has been added', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = scan.report_title
        form.content.data = scan.report_content
        form.summary.data = scan.report_summary
    return render_template('report.html', title='View Report',
                           form=form, legend='View Report', scan=scanimage)


@app.route("/doctor/history")
@login_required
def doctor_history():
    scans = Scan.query.filter_by(doctor=current_user)\
        .order_by(Scan.scan_date.desc())
    # scans = Scan.query.all()
    return render_template('doctor_history.html', scans=scans)

# ---------------------------- End Doctor Routes ----------------------------------------#


# ---------------------------- Start Admin Routes --------------------------------------#
#                   In this Section are routes of the admin
# ---------------------------------------------------------------------------------------#

@app.route("/admin")
@login_required
def admin():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            doctors = Doctor.query.all()
            receptionists = Receptionist.query.all()
            technicians = Technician.query.all()
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
            return render_template('superruser/addReceptionist_su.html', title='Add Receptionist', form=form)
        else:
            abort(403)


@app.route("/admin/addTechnician", methods=['GET', 'POST'])
@login_required
def addTechnician():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            form = NewTechnician()
            if form.validate_on_submit():
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

# ---------------------------- End Admin Routes ----------------------------------------#


# ---------------------------- Start Receptionist Routes --------------------------------#
#                   In this Section are routes of the receptionists
# ---------------------------------------------------------------------------------------#

@app.route("/recep")
@login_required
def recep():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'R':
            all_patients_scans = Scan.query.all()
            return render_template("receptionist.html", p_data=all_patients_scans)
        else:
            abort(403)


@app.route("/print/<int:id>")
@login_required
def print_report(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'R':
            scan = Scan.query.filter_by(id=id).first()
            image = url_for(
                'static', filename='patients_scans/' + scan.image_file)
            return render_template("print.html", scan=scan, image=image)
        else:
            abort(403)


@app.route("/recep/addPatient", methods=['GET', 'POST'])
@login_required
def addPatient():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'R':
            form = NewPatient()
            if form.validate_on_submit():
                password = int(hashlib.sha1(
                    form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
                mail = f'{password}@P.com'
                hashed_password = bcrypt.generate_password_hash(
                    str(password)).decode('utf-8')
                age = calculate_age(form.dob.data)
                patient = Patient(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
                                  dob=form.dob.data, gender=form.gender.data, address=form.address.data, age=age)
                user = User(id=password, username=form.name.data,
                            email=mail, password=hashed_password)
                db.session.add(patient)
                db.session.add(user)
                db.session.commit()
                send_credentials(form.email.data, mail,
                                 password, form.name.data)
                with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([hashed_password])
                flash(
                    f'Patient has been created mail={mail}, password={password}', 'success')
                return redirect(url_for('patient_scan', patient_id=patient.id))
            return render_template("addPatient.html", form=form, legend="Add New Patient")
        else:
            abort(403)


@app.route("/delete/<id>/", methods=['POST', "GET"])
@login_required
def delete_patient_scan(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'R':
            scan = Scan.query.get(id)
            db.session.delete(scan)
            db.session.commit()
            flash("Your data has been deleted!", "success")
            return redirect(url_for("recep"))
        else:
            abort(403)


@app.route("/patient/<int:id>/")
@login_required
def visit_patient(id):
    patient = Patient.query.filter_by(id=id).first()
    patient_data = Scan.query.filter_by(patient=patient).all()
    print(patient_data)
    return render_template("patient_recep.html", p_data=patient_data)


@app.route("/recep/new_scan/<int:patient_id>", methods=['GET', 'POST'])
@login_required
def patient_scan(patient_id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'R':
            patient = Patient.query.get(patient_id)
            form = PatientScanForm()
            if form.validate_on_submit():
                patient = Patient.query.filter_by(ssn=form.ssn.data).first()
                doctor = Doctor.query.filter_by(
                    ssn=form.doctor_ssn.data).first()
                technician = Technician.query.filter_by(
                    ssn=form.technician_ssn.data).first()
                receptionist = Receptionist.query.filter_by(
                    id=current_user.id).first()
                if patient and doctor and technician:
                    scan = Scan(scan_type=form.scan_type.data, fees=form.fees.data, patient=patient, doctor=doctor, technician=technician,
                                receptionist=receptionist)
                    db.session.add(scan)
                    db.session.commit()
                    flash(
                        f'{scan.patient.name} {scan.scan_type} scan has been added, Technician {scan.technician.name} Notified!', 'success')
                    # create email xxxx
                    return redirect(url_for('recep'))
                else:
                    flash(
                        'This is new patient please register the patient first', 'danger')
                    return redirect(url_for('addPatient'))
            elif request.method == 'GET' and patient:
                form.ssn.data = patient.ssn
            return render_template("new_scan.html", form=form)
        else:
            abort(403)
    else:
        return render_template('login')

# ---------------------------- End Receptionist Routes ----------------------------------#


# ---------------------------- Start Technician Routes ----------------------------------#
#                   In this Section are routes of the technician
# ---------------------------------------------------------------------------------------#

@app.route("/technician")
@login_required
def technician():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            all_patients_scans = Scan.query.filter_by(technician=current_user)
            return render_template("technician.html", p_data=all_patients_scans)
        else:
            abort(403)
    else:
        return render_template('login')


@app.route("/tech/history")
def technician_history():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            scans = Scan.query.filter_by(
                technician=current_user).order_by(Scan.scan_date.desc())
            return render_template('technician_history.html', scans=scans)
        else:
            abort(403)
    else:
        return render_template('login')


@app.route("/Technician/scan_img/<int:id>/", methods=['GET', 'POST'])
@login_required
def add_scan_img(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            scan = Scan.query.filter_by(id=id).first()
            form = UploadScanForm()
            if form.validate_on_submit():
                if form.pictures.data:
                    
                    profile_pic = form.pictures.data[int(len(form.pictures.data) / 2)]
                    profile_pic = save_profile_picture(profile_pic)
                    scan.image_file = profile_pic.replace('.dcm', '.jpg')
                    
                    for picture in form.pictures.data:
                        save_picture(picture)
                        # scan.image_file = picture_file
                db.session.commit()
                flash(
                    f'{scan.patient.name} {scan.scan_type} Scan has been uploaded! Doctor {scan.doctor.name} notified', 'success')
                return redirect(url_for('technician'))
            #  image_file = url_for('static', filename='patients_scans/'+ scan.image_file)
            return render_template('scan_img.html', title='Scan Img', scan=scan, form=form)
        else:
            abort(403)

# ---------------------------- End Technician Routes ------------------------------------#


# ---------------------------- Start Patient Routes -------------------------------------#
#                   In this Section are routes of the patient
# ---------------------------------------------------------------------------------------#

@app.route("/patient")
@login_required
def patient_profile():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'P':
            all_patients_scans = Scan.query.filter_by(patient=current_user)
            patient_name = Patient.query.filter_by(id=current_user.id).first()
            return render_template("patient_profile.html", p_data=all_patients_scans, name=patient_name.name)
        else:
            abort(403)

# ---------------------------- End Patient Routes ------------------------------------#


# ---------------------------- Start Custom Error Pages Routes ------------------------#
#                   In this Section are routes of the patient
# -------------------------------------------------------------------------------------#

@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500

# ---------------------------- End Custom Error Pages Routes --------------------------#
