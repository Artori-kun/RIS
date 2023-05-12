from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from RIS import app
from RIS.utils import util_cbir
# import jsonify

## route for cbir api

## api parameters
## x0, x1, y0, y1: ROI coordinate
## instance_id: dicom instance ID
@app.route("/api/cbir/<sop_instance_uid>", methods=['GET'])
def api_cbir(sop_instance_uid):
    # sop_instance_uid = request.args.get('sop_uid')
    # print("It's here")
    try:
        x0 = request.form["x0"]
        y0 = request.form["y0"]
        x1 = request.form["x1"]
        y1 = request.form["y1"]
    except Exception as e:
        print(e)
        x0 = y0 = x1 = y1 = None
    
    cbir_result = util_cbir.cbir_search(sop_instance_id=sop_instance_uid,
                          x0=x0,
                          y0=y0,
                          x1=x1,
                          y1=y1)
    
    print(type(cbir_result))
    
    return jsonify(cbir_result)

