import pydicom
import os
import numpy as np
from PIL import Image
from RIS import app, mail
import secrets
from pyorthanc import Orthanc
from datetime import date
from flask_mail import Message
from flask import url_for
import pydicom

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def send_credentials(email, credentials_mail, credentials_pass, credentials_name):
    msg = Message('SBME Login Credentials',
                  sender='noreply@demo.com',
                  recipients=[email])
    msg.body = f'''Welcome {credentials_name}.
This is RIS
Your Account Credentials are
Username:{credentials_mail}
Password:{credentials_pass}
You have to reset your password with the first login
'''
    mail.send(msg)


def send_reset_email(user, email):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[email])
    msg.body = f'''To reset your password, visit the following link
{url_for('reset_token', token=token, _external=True)}
    
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
    
def convert_series(path):
    names = []
    dirnames = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext in ['.dcm']:
                names.append(filename)
    
    return names, dirnames[0]

def convert_dcm_jpg(path):
    name = path.split('/')[-1]
    name = name.replace('.dcm', '')
    
    im = pydicom.dcmread(path)

    im = im.pixel_array.astype(float)

    rescaled_image = (np.maximum(im,0)/im.max())*255 # float pixels
    final_image = np.uint8(rescaled_image) # integers pixels

    final_image = Image.fromarray(final_image)
    
    final_image.save(os.path.join(app.root_path, 'static/patients_scans/' + name + '.jpg'))

    # return final_image
    
def import_dcm(dcm_path):
    orthanc = Orthanc('http://localhost:8042')
    orthanc.setup_credentials('salim', 'salim')  # If needed
    
    # orthanc.setup_credentials(os.environ.get('ORTHANC_USERNAME'),
    #                           os.environ.get('ORTHANC_PWD'))
    
    with open(dcm_path, 'rb') as file_handler:
        orthanc.post_instances(file_handler.read())

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # save dcm to temp
    picture_path = os.path.join(
        app.root_path, 'static/temps', picture_fn)
    print(picture_path)
    form_picture.save(picture_path)
    
    # convert to jpg and store at patients_scans
    convert_dcm_jpg(picture_path)
    os.remove(picture_path)
    # try:
    #     import_dcm(picture_path)
    #     print('imported')
    # except Exception as e:
    #     print(e)
    return picture_fn

def save_picture(form_pictures):
    pictures_uids = []
    session_uid = secrets.token_hex(10)
    
    ## create temp directory for session
    session_path = os.path.join(app.root_path, 'static/temps/', session_uid)
    os.mkdir(session_path)
    
    ## save all dicom in temp directory
    for form_picture in form_pictures:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_uid = random_hex + f_ext
        
        pictures_uids.append(picture_uid)
        
        # save dicom to temp
        picture_path = os.path.join(session_path, picture_uid)
        # print(picture_path)
        form_picture.save(picture_path)
    
    ## extract series uid
    series_uid = extract_series_uid(session_path)
    if series_uid == 0:
        raise ValueError("Not a series!!")
    
    ## extract profile image
    profile_picture_uid = pictures_uids[int(len(pictures_uids) / 2)]
    
    # convert and save profile picturre
    convert_dcm_jpg(os.path.join(session_path, profile_picture_uid))
    
    ## import all dicom files
    try:
        for dicom in os.listdir(session_path):
            import_dcm(os.path.join(session_path, dicom))
            print(f"imported {dicom}")
        
        ## delete everything after import complete
        os.rmdir(session_path)
    except Exception as e:
        print(e)
    return series_uid, profile_picture_uid.replace('.dcm', '.jpg')
    # return picture_fn
    
def encrypt_id(form):
    p1 = f"{int(form.thickness.data)}.{int((form.thickness.data - int(form.thickness.data)) * 1000)}"
    p2 = p3 = 'ERROR'
    if form.organ.data == "Sọ mặt":
        p2 = f"SM.{form.record_id.data}"
    elif form.organ.data == "Mặt hàm":
        p2 = f"MH.{form.record_id.data}"
        
    if form.patient_gender.data == "Male":
        p3 = f"{form.patient_dob.data.year}.M.{form.date_taken.data.strftime('%d%m%Y')}"
    elif form.patient_gender.data == "Female":
        p3 = f"{form.patient_dob.data.year}.F.{form.date_taken.data.strftime('%d%m%Y')}"
    
    return f"{p1}.{p2}.{p3}"

def extract_series_uid(dicom_path):
    series_uid = ''
    counter = 0
    
    dicoms = [os.path.join(dicom_path, d) for d in os.listdir(dicom_path)]
    for d_path in dicoms:
        dicom = pydicom.dcmread(d_path, force=True)
        if hasattr(dicom, "SliceLocation") and dicom.SliceLocation:
            if series_uid != str(dicom.SeriesInstanceUID):
                series_uid = str(dicom.SeriesInstanceUID)
                counter = counter + 1
    if counter > 1:
        return 0
    else:
        return series_uid
        