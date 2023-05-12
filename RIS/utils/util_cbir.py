import os
from RIS import app
from pyorthanc import Orthanc
from PIL import Image
import numpy as np
from RIS.cbir_model.build import build_model
from RIS.cbir_model.config import get_config
import torch
import cv2 as cv
import operator
import io

orthanc = Orthanc('http://localhost:8042')
# orthanc.setup_credentials('salim', 'salim')

# orthanc.setup_credentials(os.environ.get('ORTHANC_USERNAME'), os.environ.get('ORTHANC_PWD'))

CBIR_ROOT = os.path.join(app.root_path, 'cbir_feature')
CONFIG = get_config()

def get_pretrained_model(config):

    model = build_model(config)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    print(
        f"==============> Resuming form {config.MODEL.RESUME}....................")
    if config.MODEL.RESUME.startswith('https'):
        checkpoint = torch.hub.load_state_dict_from_url(
            config.MODEL.RESUME, map_location='cpu', check_hash=True)
    else:
        checkpoint = torch.load(config.MODEL.RESUME, map_location='cpu')

    model.load_state_dict(checkpoint['model'], strict=False)
    print(f"=> loaded successfully '{config.MODEL.RESUME}'")

    del checkpoint
    torch.cuda.empty_cache()

    model.eval()
    return model

MODEL = get_pretrained_model(config=CONFIG)

# retrieve instance image from orthanc
# using SOPInstanceID
# return numpy array of type int16
def get_instance_image(sop_instance_id):
    instance_id = ''
    instance_lookup = orthanc.post_tools_lookup(sop_instance_id)
    
    try:
        for i in instance_lookup:
            if i["Type"] == "Instance":
                instance_id = i["ID"]
    except Exception as e:
        print(e)
        return 500    
    # instance not found        
    if instance_id == '':
        return 404
    
    instance_img = orthanc.get_instances_id_image_uint8(instance_id)
    instance_img = np.array(Image.open(io.BytesIO(instance_img)), np.uint8)
    
    return instance_img, instance_id

def cos_similarity(x, y):
    similarity = np.dot(x, y.T) / (np.linalg.norm(x) * np.linalg.norm(y))
    return similarity.flatten()[0]

def extract_feat(config, model, img):
    """
    Extract feature of input image by `model`.
    """
    device = torch.device("cpu")

    # print(f"Resizing...{img.shape}")
    img = cv.resize(img, (config.DATA.IMG_SIZE, config.DATA.IMG_SIZE))
    # print(img.shape)
    # img = img.reshape((224, 224, 1))
    # print(img.shape)
    
    # print("Transposing")
    img = img.transpose(2, 0, 1)
    
    # print("New axis")
    img = img[np.newaxis]
    img = img.astype(dtype=np.float32)

    # print("torch")
    img = torch.from_numpy(img)
    # print(img)
    img.to(device)

    with torch.no_grad():
        # print("model")
        output = model(img)
    # feat = output.cpu().numpy()
    return output

def retrieve(feat, series_id, threshold=0.85):
    similarities = {}
    
    for root, studies, series in os.walk(CBIR_ROOT):
        for serie in series:
            if serie.endswith(".npz") and serie.replace(".npz",  "") is not series_id:
                serie_path = os.path.join(root, serie)
                
                # read series npz file
                npz_data = np.load(serie_path)
                
                ## using cosine similarity to compare
                n = len(npz_data['ID'])
                for i in range(n):
                    cos_sim = cos_similarity(npz_data['FEATURE'][i], feat)
                    if cos_sim >= threshold:
                        cos_sim = np.float64(cos_sim)
                        cos_sim = "{:.3f}".format(cos_sim)
                        similarities[npz_data['ID'][i]] = cos_sim
    similarities = dict(sorted(similarities.items(), key=operator.itemgetter(1), reverse=True))
    return similarities

def cbir_search(sop_instance_id, x0, y0, x1, y1):
    img, instance_id = get_instance_image(sop_instance_id)
    img = np.stack((img,)*3, axis=-1)
    
    if img.any() == 404 or img.any() == 500:
        return img
    
    series_uid = orthanc.get_instances_id_series(instance_id)
    series_uid = series_uid["MainDicomTags"]["SeriesInstanceUID"]
    
    if None not in {x0, y0, x1, y1}:
        img = img[int(y0): int(y1), int(x0): int(x1)]
    # else:
    #     img = img.reshape(img.shape[0], img.shape[1],)
    
    feature = extract_feat(CONFIG, MODEL, img)
    feature = feature.cpu().numpy()
    
    similarities = retrieve(feature, series_uid)
    
    return similarities

def register_img(series_uid):
    feature = []
    id = []
    
    try:
        ## find series orthanc id
        series_lookup = orthanc.post_tools_lookup(series_uid)
    
        if len(series_lookup) == 0:
            return 404
        
        for series in series_lookup:
            if series["Type"] == "Series":
                series_id = series["ID"]
        
        ## find parent study uid
        parent_study = orthanc.get_series_id_study(series_id)
        parent_study = parent_study["MainDicomTags"]["StudyInstanceUID"]
        if not os.path.exists(os.path.join(app.root_path, f"cbir_feature/{parent_study}")):
            os.mkdir(os.path.join(app.root_path, f"cbir_feature/{parent_study}"))
        
        ## find all instances and extract feature
        series_instances = orthanc.get_series_id_instances(series_id)
        for instance in series_instances:
            instance_id = instance["ID"]
            
            print(f"\tInstance: {instance_id}")
            instance_img = orthanc.get_instances_id_image_uint8(instance_id)
            instance_img = np.array(Image.open(io.BytesIO(instance_img)), np.uint8)
            # print(instance_img.shape)
            instance_img = np.stack((instance_img,)*3, axis=-1)
            # print(instance_img.shape)
            
            # print(f"Extracting {instance_img.shape}")
            # instance_img = instance_img.reshape(instance_img.shape[0], instance_img.shape[1], 1)
            instance_feature = extract_feat(CONFIG, MODEL, instance_img)
            # print("extracted")
            
            feature.append(instance_feature)
            id.append(instance["MainDicomTags"]["SOPInstanceUID"])
            # print("appended")
    except Exception as e:
        print(e)
        # print(instance["ID"])
        # return 500
        pass
    
    feature = torch.vstack(feature).cpu().numpy()
    id = np.array(id)
    # print("\tready to savez")
        
    npz_path = os.path.join(app.root_path, f"cbir_feature/{parent_study}/{series_uid}.npz")
    np.savez(npz_path, FEATURE=feature, ID=id)
    print(f"\tSaved at {npz_path}")
        
    