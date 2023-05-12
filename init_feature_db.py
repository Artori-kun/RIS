import os
from pyorthanc import Orthanc
from RIS.utils import util_cbir

orthanc = Orthanc('http://localhost:8042')
orthanc.setup_credentials('salim', 'salim')

# orthanc.setup_credentials(os.environ.get('ORTHANC_USERNAME'), os.environ.get('ORTHANC_PWD'))

all_series = orthanc.get_series()
for series in all_series:
    print(f"Series: {series}")
    series_info = orthanc.get_series_id(series)
    
    series_uid = series_info["MainDicomTags"]["SeriesInstanceUID"]
    
    register = util_cbir.register_img(series_uid)
    
    if register == 404:
        print(f"404 ??!! {series_uid}")
        continue
    elif register == 500:
        print("500")
        break

print("Complete registering orthanc database")
orthanc.close()