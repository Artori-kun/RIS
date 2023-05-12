from __future__ import print_function
from flask import render_template, url_for, flash, redirect, request, abort
from RIS import app, db, bcrypt
from RIS.forms import (LoginForm, ResetPasswordForm, AddScanForm, UpdateScanForm)
from RIS.models import Technician, User, Scan
from flask_login import login_user, current_user, logout_user, login_required
import hashlib
import csv


import RIS.utils.utils as utils
import RIS.utils.util_cbir as util_cbir

# ---------------------------- Start Util Routes ---------------------------------------#
#                   In this Section are the helper utility routes
# --------------------------------------------------------------------------------------#


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            return redirect(url_for('admin'))
        elif current_user.email[-5] == 'T':
            return redirect(url_for('technician'))
    form = LoginForm()
    if form.validate_on_submit():
        with open('passwords.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                if bcrypt.check_password_hash(line[0], form.password.data):
                    user = User.query.filter_by(email=form.email.data).first()
                    if user.active is False:
                        raise("This user is disabled. Please contact administrator for details.")
                    elif form.email.data[-5] == 'T':
                        email = Technician.query.filter_by(
                            id=form.password.data).first()
                    else:
                        raise('Email is not valid')
                    utils.send_reset_email(user, email.email)
                    flash(
                        'An email has been sent with instructions to reset your password', 'info')
                    return redirect(url_for('login'))
        user = User.query.filter_by(email=form.email.data).first()
        if user.active is False:
            flash('This user is disabled. Please contact administrator for details.')
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.email[-5] == 'A':
                return redirect(url_for('admin'))
            elif current_user.email[-5] == 'T':
                return redirect(url_for('technician'))
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
# @app.route("/doctor")
# @login_required
# def home():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'D':
#             all_patients_scans = Scan.query.filter_by(
#                 doctor=current_user).all()
#             print(url_for('home'))
#             return render_template("doctor.html", p_data=all_patients_scans)
#         else:
#             abort(403)


# @app.route("/doctors/report/<scan_id>", methods=['GET', 'POST'])
# @login_required
# def Report(scan_id):
#     scan = Scan.query.get_or_404(scan_id)
#     scanimage = url_for('static', filename='patients_scans/' + scan.image_file)
#     form = ReportForm()
#     if form.validate_on_submit():
#         scan.report_title = form.title.data
#         scan.report_content = form.content.data
#         scan.report_summary = form.summary.data
#         db.session.commit()
#         flash('Your Report has been added', 'success')
#         return redirect(url_for('home'))
#     elif request.method == 'GET':
#         form.title.data = scan.report_title
#         form.content.data = scan.report_content
#         form.summary.data = scan.report_summary
#     return render_template('report.html', title='View Report',
#                            form=form, legend='View Report', scan=scanimage)


# @app.route("/doctor/history")
# @login_required
# def doctor_history():
#     scans = Scan.query.filter_by(doctor=current_user)\
#         .order_by(Scan.scan_date.desc())
#     # scans = Scan.query.all()
#     return render_template('doctor_history.html', scans=scans)

# ---------------------------- End Doctor Routes ----------------------------------------#


# ---------------------------- Start Receptionist Routes --------------------------------#
#                   In this Section are routes of the receptionists
# ---------------------------------------------------------------------------------------#

# @app.route("/recep")
# @login_required
# def recep():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'R':
#             all_patients_scans = Scan.query.all()
#             return render_template("receptionist.html", p_data=all_patients_scans)
#         else:
#             abort(403)


# @app.route("/print/<int:id>")
# @login_required
# def print_report(id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'R':
#             scan = Scan.query.filter_by(id=id).first()
#             image = url_for(
#                 'static', filename='patients_scans/' + scan.image_file)
#             return render_template("print.html", scan=scan, image=image)
#         else:
#             abort(403)


# @app.route("/recep/addPatient", methods=['GET', 'POST'])
# @login_required
# def addPatient():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'R':
#             form = NewPatient()
#             if form.validate_on_submit():
#                 password = int(hashlib.sha1(
#                     form.ssn.data.encode()).hexdigest(), 16) % (10 ** 8)
#                 mail = f'{password}@P.com'
#                 hashed_password = bcrypt.generate_password_hash(
#                     str(password)).decode('utf-8')
#                 age = calculate_age(form.dob.data)
#                 patient = Patient(id=password, name=form.name.data, ssn=form.ssn.data, email=form.email.data,
#                                   dob=form.dob.data, gender=form.gender.data, address=form.address.data, age=age)
#                 user = User(id=password, username=form.name.data,
#                             email=mail, password=hashed_password)
#                 db.session.add(patient)
#                 db.session.add(user)
#                 db.session.commit()
#                 send_credentials(form.email.data, mail,
#                                  password, form.name.data)
#                 with open("passwords.csv", 'a+', encoding='utf-8', newline='') as csv_file:
#                     csv_writer = csv.writer(csv_file)
#                     csv_writer.writerow([hashed_password])
#                 flash(
#                     f'Patient has been created mail={mail}, password={password}', 'success')
#                 return redirect(url_for('patient_scan', patient_id=patient.id))
#             return render_template("addPatient.html", form=form, legend="Add New Patient")
#         else:
#             abort(403)


# @app.route("/delete/<id>/", methods=['POST', "GET"])
# @login_required
# def delete_patient_scan(id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'R':
#             scan = Scan.query.get(id)
#             db.session.delete(scan)
#             db.session.commit()
#             flash("Your data has been deleted!", "success")
#             return redirect(url_for("recep"))
#         else:
#             abort(403)


# @app.route("/patient/<int:id>/")
# @login_required
# def visit_patient(id):
#     patient = Patient.query.filter_by(id=id).first()
#     patient_data = Scan.query.filter_by(patient=patient).all()
#     print(patient_data)
#     return render_template("patient_recep.html", p_data=patient_data)


# @app.route("/recep/new_scan/<int:patient_id>", methods=['GET', 'POST'])
# @login_required
# def patient_scan(patient_id):
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'R':
#             patient = Patient.query.get(patient_id)
#             form = PatientScanForm()
#             if form.validate_on_submit():
#                 patient = Patient.query.filter_by(ssn=form.ssn.data).first()
#                 doctor = Doctor.query.filter_by(
#                     ssn=form.doctor_ssn.data).first()
#                 technician = Technician.query.filter_by(
#                     ssn=form.technician_ssn.data).first()
#                 receptionist = Receptionist.query.filter_by(
#                     id=current_user.id).first()
#                 if patient and doctor and technician:
#                     scan = Scan(scan_type=form.scan_type.data, fees=form.fees.data, patient=patient, doctor=doctor, technician=technician,
#                                 receptionist=receptionist)
#                     db.session.add(scan)
#                     db.session.commit()
#                     flash(
#                         f'{scan.patient.name} {scan.scan_type} scan has been added, Technician {scan.technician.name} Notified!', 'success')
#                     # create email xxxx
#                     return redirect(url_for('recep'))
#                 else:
#                     flash(
#                         'This is new patient please register the patient first', 'danger')
#                     return redirect(url_for('addPatient'))
#             elif request.method == 'GET' and patient:
#                 form.ssn.data = patient.ssn
#             return render_template("new_scan.html", form=form)
#         else:
#             abort(403)
#     else:
#         return render_template('login')

# ---------------------------- End Receptionist Routes ----------------------------------#


# ---------------------------- Start Technician Routes ----------------------------------#
#                   In this Section are routes of the technician
# ---------------------------------------------------------------------------------------#

@app.route("/technician")
@login_required
def technician():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            all_patients_scans = Scan.query.filter_by(technician_id=current_user.id).all()
            return render_template("technician.html", scans=all_patients_scans)
        else:
            abort(403)
    else:
        return render_template('login')


# @app.route("/tech/history")
# def technician_history():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'T':
#             scans = Scan.query.filter_by(
#                 technician=current_user).order_by(Scan.scan_date.desc())
#             return render_template('technician_history.html', scans=scans)
#         else:
#             abort(403)
#     else:
#         return render_template('login')


@app.route("/technician/add_scan/", methods=['GET', 'POST'])
@login_required
def add_scan():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            # technician = Technician.query.filter_by(id=current_user.id).first()
            form = AddScanForm()
            
            series_uid = 'UNKNOWN'
            profile_image = 'default.jpg'
            scan = Scan()
            scan.series_id = series_uid
            scan.profile_image = profile_image
            
            if form.validate_on_submit():
                ## generate (not so) encrypted ID
                encrypt_id = utils.encrypt_id(form=form)
            
                if form.dicom_series.data:
                    try:
                        series_uid, profile_image = utils.save_picture(form.dicom_series.data)
                    except Exception as e:
                        if type(e) is ValueError:
                            flash("The dicom files you have chosen do not belong to a single dicom series", 'danger')
                            return redirect(url_for('add_scan'))
                
                scan.patient_name = form.patient_name.data
                scan.patient_ssn = form.patient_ssn.data
                scan.patient_gender = form.patient_gender.data
                scan.patient_dob = form.patient_dob.data
                scan.record_id = form.record_id.data
                scan.form_id = form.form_id.data
                scan.date_taken = form.date_taken.data
                scan.organ = form.organ.data
                scan.thickness = form.thickness.data
                scan.encrypt_id = encrypt_id
                scan.conclusion = form.conclusion.data
                scan.contrast_injection = form.contrast_injection.data
                scan.series_id = series_uid
                scan.profile_image = profile_image
                scan.technician_id = current_user.id
                
                db.session.add(scan)
                db.session.commit()
                flash(f'Scan has been uploaded!', 'success')
                
                util_cbir.register_img(scan.series_id)
                
                return redirect(url_for('technician'))
            #  image_file = url_for('static', filename='patients_scans/'+ scan.image_file)
            return render_template('new_scan.html', title='New Scan', scan=scan, form=form)
        else:
            abort(403)
    else:
        redirect(url_for('login'))

@app.route("/technician/update_scan/<int:scan_id>", methods=['GET', 'POST'])
def scan_update(scan_id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            scan = Scan.query.filter_by(id=scan_id).first()
            
            if scan == None:
                abort(404)
            
            form = UpdateScanForm(obj=scan)
            if form.validate_on_submit():
                form.populate_obj(scan)
                
                encrypt_id = utils.encrypt_id(form=form)
                scan.encrypt_id = encrypt_id
            
                if form.dicom_series.data:
                    try:
                        series_uid, profile_image = utils.save_picture(form.dicom_series.data)
                        scan.series_uid = series_uid
                        scan.profile_image = profile_image
                    except Exception as e:
                        print(e)
                        # if type(e) is ValueError:
                        flash("The dicom files you have chosen do not belong to a single dicom series", 'danger')
                        return redirect(url_for('scan_update', scan_id=scan_id))

                db.session.commit()
                flash(f'Scan has been updated!', 'success')
                
                util_cbir.register_img(scan.series_id)
                
                return redirect(url_for('technician'))
            return render_template("new_scan.html", title="Update Scan",scan=scan, form=form)
        else:
            abort(403)
    else:
        redirect(url_for('login'))
    

@app.route("/technician/delete_scan/<int:scan_id>", methods=['GET', 'POST'])
def scan_delete(scan_id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'T':
            scan = Scan.query.get(scan_id)
            
            db.session.delete(scan)
            db.session.commit()
            
            flash("Your scan has been deleted!", "success")
            return redirect(url_for('technician'))
        else:
            abort(403)
    return redirect(url_for('technician'))
# ---------------------------- End Technician Routes ------------------------------------#


# ---------------------------- Start Patient Routes -------------------------------------#
#                   In this Section are routes of the patient
# ---------------------------------------------------------------------------------------#

# @app.route("/patient")
# @login_required
# def patient_profile():
#     if current_user.is_authenticated:
#         if current_user.email[-5] == 'P':
#             all_patients_scans = Scan.query.filter_by(patient=current_user)
#             patient_name = Patient.query.filter_by(id=current_user.id).first()
#             return render_template("patient_profile.html", p_data=all_patients_scans, name=patient_name.name)
#         else:
#             abort(403)

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
