from flask import render_template, url_for, flash, redirect, request, abort
from RIS import app, db, bcrypt
from RIS.forms import (ReportForm, NewPatient, PatientScanForm, UploadScanForm)
from RIS.models import Technician, User, Patient, Doctor, Receptionist, Scan
from flask_login import current_user, login_required
import hashlib
import csv
from RIS.utils import save_picture, save_profile_picture, calculate_age, send_reset_email, send_credentials

#---------------------Doctor Routes for Super User--------------------#

@app.route("/admin/doctor")
@login_required
def doctor_su():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            all_patients_scans = Scan.query.all()
            print(url_for('home'))
            return render_template("superuser/doctor_su.html", p_data=all_patients_scans)
        else:
            abort(403)


@app.route("/admin/doctors/report/<scan_id>", methods=['GET', 'POST'])
@login_required
def report_su(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    scanimage = url_for('static', filename='patients_scans/' + scan.image_file)
    form = ReportForm()
    if form.validate_on_submit():
        scan.report_title = form.title.data
        scan.report_content = form.content.data
        scan.report_summary = form.summary.data
        db.session.commit()
        flash('Your Report has been added', 'success')
        return redirect(url_for('doctor_su'))
    elif request.method == 'GET':
        form.title.data = scan.report_title
        form.content.data = scan.report_content
        form.summary.data = scan.report_summary
    return render_template('superuser/report_su.html', title='View Report',
                           form=form, legend='View Report', scan=scanimage)


@app.route("/admin/doctor/history")
@login_required
def doctor_history_su():
    scans = Scan.query.order_by(Scan.scan_date.desc())
    # scans = Scan.query.all()
    return render_template('superuser/doctor_history_su.html', scans=scans)

#---------------------------------------------------------------------#

#---------------------Technician Routes for Super User--------------------#
@app.route("/admin/technician")
@login_required
def technician_su():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            all_patients_scans = Scan.query.all()
            return render_template("superuser/technician_su.html", p_data=all_patients_scans)
        else:
            abort(403)
    else:
        return render_template('login')


@app.route("/admin/technician/history")
def technician_history_su():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            scans = Scan.query.order_by(Scan.scan_date.desc())
            return render_template('superuser/technician_history_su.html', scans=scans)
        else:
            abort(403)
    else:
        return render_template('login')


@app.route("/admin/technician/scan_img/<int:id>/", methods=['GET', 'POST'])
@login_required
def add_scan_img_su(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
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
            return render_template('superuser/scan_img_su.html', title='Scan Img', scan=scan, form=form)
        else:
            abort(403)
            
#-------------------------------------------------------------------------#

#---------------------Receptionist Routes for Super User--------------------#
@app.route("/admin/recep")
@login_required
def recep_su():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            all_patients_scans = Scan.query.all()
            return render_template("superuser/receptionist_su.html", p_data=all_patients_scans)
        else:
            abort(403)


@app.route("/admin/recep/print/<int:id>")
@login_required
def print_report_su(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            scan = Scan.query.filter_by(id=id).first()
            image = url_for(
                'static', filename='patients_scans/' + scan.image_file)
            return render_template("superuser/print_su.html", scan=scan, image=image)
        else:
            abort(403)


@app.route("/admin/recep/addPatient", methods=['GET', 'POST'])
@login_required
def addPatient_su():
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
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
                return redirect(url_for('patient_scan_su', patient_id=patient.id))
            return render_template("superuser/addPatient_su.html", form=form, legend="Add New Patient")
        else:
            abort(403)


@app.route("/admin/deletePatient/<id>/", methods=['POST', "GET"])
@login_required
def delete_patient_scan_su(id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            scan = Scan.query.get(id)
            db.session.delete(scan)
            db.session.commit()
            flash("Your data has been deleted!", "success")
            return redirect(url_for("recep_su"))
        else:
            abort(403)


@app.route("/admin/patient/<int:id>/")
@login_required
def visit_patient_su(id):
    patient = Patient.query.filter_by(id=id).first()
    patient_data = Scan.query.filter_by(patient=patient).all()
    print(patient_data)
    return render_template("superuser/patient_recep_su.html", p_data=patient_data)


@app.route("/admin/recep/new_scan/<int:patient_id>", methods=['GET', 'POST'])
@login_required
def patient_scan_su(patient_id):
    if current_user.is_authenticated:
        if current_user.email[-5] == 'A':
            patient = Patient.query.get(patient_id)
            form = PatientScanForm()
            
            form.doctor_ssn.choices = [(doctor.id, doctor.name) for doctor in Doctor.query.filter_by(active=True).all()]
            form.technician_ssn.choices = [(tech.id, tech.name) for tech in Technician.query.filter_by(active=True).all()]
            
            if form.validate_on_submit():
                patient = Patient.query.filter_by(ssn=form.ssn.data).first()
                doctor = Doctor.query.filter_by(
                    ssn=form.doctor_ssn.data).first()
                technician = Technician.query.filter_by(
                    ssn=form.technician_ssn.data).first()
                
                # !!!!!!!!!!!!!!!
                receptionist = Receptionist.query.first()
                ###########
                if patient and doctor and technician:
                    scan = Scan(scan_type=form.scan_type.data, fees=form.fees.data, patient=patient, doctor=doctor, technician=technician,
                                receptionist=receptionist)
                    db.session.add(scan)
                    db.session.commit()
                    flash(
                        f'{scan.patient.name} {scan.scan_type} scan has been added, Technician {scan.technician.name} Notified!', 'success')
                    # create email xxxx
                    return redirect(url_for('recep_su'))
                else:
                    flash(
                        'This is new patient please register the patient first', 'danger')
                    return redirect(url_for('addPatient_su'))
            elif request.method == 'GET' and patient:
                form.ssn.data = patient.ssn
            return render_template("superuser/new_scan_su.html", form=form)
        else:
            abort(403)
    else:
        return render_template('login')