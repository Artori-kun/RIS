import pydicom
import os
import numpy as np
from PIL import Image
from RIS import app
    
def convert_series(path):
    names = []
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