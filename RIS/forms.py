from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, MultipleFileField, SelectField
from wtforms.fields.core import IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from RIS.models import User, Technician, Scan
from wtforms.fields.html5 import DateField, DateTimeLocalField
from flask_wtf.file import FileField, FileAllowed
# import wtforms


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# class ReportForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired(), Length(max=100)])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     summary = StringField('Summary', validators=[DataRequired()])
#     submit = SubmitField('Submit')

# class NewDoctor(FlaskForm):
#     name = StringField('Doctor Name',
#                            validators=[DataRequired(), Length(min=2, max=20)])
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#     ssn = StringField('SSN', validators=[DataRequired()])
#     dob = DateField('Birthday', validators=[DataRequired()])
#     speciality = StringField('Speciality', validators=[DataRequired(), Length(min=5, max=30)])
#     salary = IntegerField('Salary', validators=[DataRequired()])
#     submit = SubmitField('Add New Doctor')

#     def validate_ssn(self, ssn):
#         ssn = Doctor.query.filter_by(ssn=ssn.data).first()
#         if ssn:
#             raise ValidationError("This ssn already exists.")
        
#     def validate_email(self, email) :
#         email = Doctor.query.filter_by(email = email.data).first()
#         if  email :
#             raise ValidationError("This Email already exists. Try a different one")

# class NewReceptionist(FlaskForm):
#     name = StringField('Receptionist Name',
#                            validators=[DataRequired(), Length(min=2, max=20)])
#     email = StringField('Receptionist Email',
#                         validators=[DataRequired(), Email()])
#     ssn = StringField('Receptionist SSN', validators=[DataRequired()])
#     dob = DateField('Receptionist Birthday', validators=[DataRequired()])
#     salary = IntegerField('Receptionist Salary', validators=[DataRequired()])
#     gender = SelectField('Receptionist Gender', choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
#     address = StringField('Receptionist Address', validators=[DataRequired(), Length(min=3, max=100)])
#     submit = SubmitField('Add New Reciptionist')

#     def validate_ssn(self, ssn):
#         ssn = Receptionist.query.filter_by(ssn=ssn.data).first()
#         if ssn:
#             raise ValidationError("This ssn already exists")
        
#     def validate_email(self, email) :
#         email = Receptionist.query.filter_by(email = email.data).first()
#         if  email :
#             raise ValidationError("This Email already exists. try a different one")

class NewTechnician(FlaskForm):
    username = StringField('Technician Username', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Technician Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Technician Email', validators=[DataRequired(), Email()])
    ssn = StringField('Technician SSN', validators=[DataRequired()])
    dob = DateField('Technician Birthday', validators=[DataRequired()])
    gender = SelectField('Technician Gender', choices=[("Male", "Male"), ("Female", "Female")])
    submit = SubmitField('Add New Technician')

    def validate_ssn(self, ssn):
        ssn = Technician.query.filter_by(ssn=ssn.data).first()
        if ssn:
            raise ValidationError("This ssn already exists")
    
    def validate_username(self, username):
        username = User.query.filter_by(username=username.data).first()
        if username:
            raise ValidationError("Username already exists")
        
        
    # def validate_email(self, email) :
    #     email = Technician.query.filter_by(email = email.data).first()
    #     if  email :
    #         raise ValidationError("This Email already exists. try a different one")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# class NewPatient(FlaskForm):
#     name = StringField("Patient Name", validators = [DataRequired(), Length(min=3, max=50)])
#     ssn = StringField("Patient SSN", validators = [DataRequired(), Length (min=14, max=14)])
#     email = StringField('Patient Email', validators=[DataRequired(), Email()])
#     dob = DateField("Patient Birthday", validators = [DataRequired()])
#     gender = StringField("Patient Gender", [DataRequired(), Length(min=4, max=6)])
#     address = TextAreaField("Patient Address", validators = [DataRequired(), Length(max=200)])
#     submit = SubmitField("Add Patient")    

#     def validate_ssn(self, ssn):
#         ssn = Patient.query.filter_by(ssn=ssn.data).first()
#         if ssn:
#             raise ValidationError("this is patient is already exist")
        
#     def validate_email(self, email) :
#         email = Patient.query.filter_by(email = email.data).first()
#         if  email :
#             raise ValidationError("that email is exist for other patient! please try another email")

class AddScanForm(FlaskForm):
    patient_ssn = StringField("SSN", validators=[DataRequired(), Length(min=12, max=12)])
    patient_name = StringField("Patient Name", validators = [DataRequired(), Length(min=1, max=50)])
    patient_dob = DateField("Patient DoB", validators = [DataRequired()])
    patient_gender = SelectField("Patient Gender", choices=[("Male", "Male"), ("Female", "Female")])
    
    record_id = StringField("Record Id", validators=[DataRequired(), Length(min=8, max=8)])
    form_id = StringField("Form Id", validators=[DataRequired(), Length(min=8, max=8)])
    date_taken = DateField("Date Taken", validators = [DataRequired()])
    organ = SelectField("Organ", choices=[("Sọ mặt", "Sọ mặt"), ("Mặt hàm", "Mặt hàm")])
    thickness = DecimalField("Thickness", validators=[DataRequired()])
    conclusion = StringField("Conclusion", validators=[DataRequired()])
    contrast_injection = SelectField(
        "Contrast Injection", 
        choices=[(True, "Có"), (False, "Không")], 
        validators=[InputRequired()],
        coerce=bool)
    
    # scan_type = StringField("Scan Type", [DataRequired(), Length (min=2, max=50)])
    # fees = StringField("Fees", [DataRequired()])
    # technician_ssn = SelectField("Technician SSN", choices=[], validators=[DataRequired() , Length (min=3, max=100)])
    # doctor_ssn = SelectField("Doctor SSN", choices=[], validators=[DataRequired(), Length (min=3 , max=100 )])
    
    dicom_series = MultipleFileField('Choose Scan to Upload', validators=[FileAllowed(['dcm'])])
    
    submit = SubmitField("Submit")
    
    # def validate_patient_ssn(self, patient_ssn):
    #     if len(patient_ssn.data) != 14:
    #         raise ValidationError("Patient SSN Number must have 12 characters")
        
    # def validate_record_id(self, record_id):
    #     if len(record_id.data) != 8:
    #         raise ValidationError("Record ID must have 8 characters")
        
    # def validate_form_id(self, form_id):
    #     if len(form_id.data) != 8:
    #         raise ValidationError("Form ID must have 8 characters")

    # def validate_technician_ssn(self, ssn):
    #     ssn = Technician.query.filter_by(ssn=ssn.data, active=True).first()
    #     if not ssn:
    #         raise ValidationError("The technician does not exist or active")
        
    # def validate_doctor_ssn(self, ssn):
    #     ssn = Doctor.query.filter_by(ssn=ssn.data, active=True).first()
    #     if not ssn:
    #         raise ValidationError("The doctor does not exist or active")

class UpdateScanForm(FlaskForm):
    patient_ssn = StringField("SSN", validators=[DataRequired(), Length(min=12, max=12)])
    patient_name = StringField("Patient Name", validators = [DataRequired(), Length(min=1, max=50)])
    patient_dob = DateField("Patient DoB", validators = [DataRequired()])
    patient_gender = SelectField("Patient Gender", choices=[("Male", "Male"), ("Female", "Female")])
    
    record_id = StringField("Record Id", validators=[DataRequired(), Length(min=8, max=8)])
    form_id = StringField("Form Id", validators=[DataRequired(), Length(min=8, max=8)])
    date_taken = DateField("Date Taken", validators = [DataRequired()])
    organ = SelectField("Organ", choices=[("Sọ mặt", "Sọ mặt"), ("Mặt hàm", "Mặt hàm")])
    thickness = DecimalField("Thickness", validators=[DataRequired()])
    conclusion = StringField("Conclusion", validators=[DataRequired()])
    contrast_injection = SelectField(
        "Contrast Injection", 
        choices=[(True, "Có"), (False, "Không")], 
        validators=[InputRequired()],
        coerce=bool)
    
    dicom_series = MultipleFileField('Choose Scan to Upload', validators=[FileAllowed(['dcm'])])
    
    submit = SubmitField("Update")
    
    current = Scan()
    
    def populate_obj(self, obj):
        self.current = obj
        super().populate_obj(obj)

# class UploadScanForm(FlaskForm):
#     pictures = MultipleFileField('Choose Scan to Upload', validators=[FileAllowed(['dcm'])])
#     # picture = FileField('Update profile picture', validators=[FileAllowed(['dcm'])])
#     submit = SubmitField('Upload Patient Scan')
    
# class UpdateDoctor(FlaskForm):
#     name = StringField('Doctor Name',
#                            validators=[DataRequired(), Length(min=2, max=20)])
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#     ssn = StringField('SSN', validators=[DataRequired()])
#     dob = DateField('Birthday', validators=[DataRequired()])
#     speciality = StringField('Speciality', validators=[DataRequired(), Length(min=5, max=30)])
#     salary = IntegerField('Salary', validators=[DataRequired()])
#     submit = SubmitField('Update Doctor Information')

#     current = Doctor()
    
#     def populate_obj(self, obj):
#         self.current = obj
#         super().populate_obj(obj)
    
#     def validate_ssn(self, ssn):
#         ssn = Doctor.query.filter_by(ssn=ssn.data, active=True).first()
#         if ssn and ssn is not self.current:
#             raise ValidationError("This ssn already exists")
        
#     def validate_email(self, email) :
#         email = Doctor.query.filter_by(email = email.data, active=True).first()
#         if  email and email is not self.current:
#             raise ValidationError("This Email already exists. try a different one")
        
# class UpdateReceptionist(FlaskForm):
#     name = StringField('Receptionist Name',
#                            validators=[DataRequired(), Length(min=2, max=20)])
#     email = StringField('Receptionist Email',
#                         validators=[DataRequired(), Email()])
#     ssn = StringField('Receptionist SSN', validators=[DataRequired()])
#     dob = DateField('Receptionist Birthday', validators=[DataRequired()])
#     salary = IntegerField('Receptionist Salary', validators=[DataRequired()])
#     gender = SelectField('Receptionist Gender', choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
#     address = StringField('Receptionist Address', validators=[DataRequired(), Length(min=3, max=100)])
#     submit = SubmitField('Update Receptionist Information')

#     current = Receptionist()
    
#     def populate_obj(self, obj):
#         self.current = obj
#         super().populate_obj(obj)
    
#     def validate_ssn(self, ssn):
#         ssn = Receptionist.query.filter_by(ssn=ssn.data, active=True).first()
#         if ssn and ssn is not self.current:
#             raise ValidationError("This ssn already exists")
        
#     def validate_email(self, email) :
#         email = Receptionist.query.filter_by(email = email.data, active=True).first()
#         if  email and email is not self.current:
#             raise ValidationError("This Email already exists. try a different one")
        
class UpdateTechnician(FlaskForm):
    username = StringField('Technician Username', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Technician Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Technician Email', validators=[DataRequired(), Email()])
    ssn = StringField('Technician SSN', validators=[DataRequired()])
    dob = DateField('Technician DoB', validators=[DataRequired()])
    # salary = IntegerField('Technician Salary', validators=[DataRequired()])
    gender = SelectField('Technician Gender', choices=[("Male", "Male"), ("Female", "Female")])
    # address = StringField('Technician Address', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Update Technician Information')

    current = Technician()
    
    def populate_obj(self, obj):
        self.current = obj
        super().populate_obj(obj)
    
    # def validate_ssn(self, ssn):
    #     ssn = Technician.query.filter_by(ssn=ssn.data, active=True).first()
    #     if ssn and ssn is not self.current:
    #         raise ValidationError("This ssn already exists")
        
    # def validate_email(self, email) :
    #     email = Technician.query.filter_by(email = email.data, active=True).first()
    #     if  email and email is not self.current:
    #         raise ValidationError("This Email already exists. try a different one")