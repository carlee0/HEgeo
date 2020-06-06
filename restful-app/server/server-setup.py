# http://flask.pocoo.org/docs/patterns/fileuploads/
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import hegeo
import numpy as np
import io
from contextlib import redirect_stdout
import pickle

UPLOAD_FOLDER = 'files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tasks = [
    {
        "fence": "",
        "id": "",
        "data": {
            "parms": "",
            "coordinates": "",
            "is_left": "",
            "dy": "",
            "is_left_flag": "",
            "dy_flag": "",
            "is_left_dec": None,
            "dy_dec": None,
            "result": "",
            "Done": False
        }
    }
]


he_server = hegeo.Server()
he_server.load_fence('data/sics.json')
vertices = np.floor(np.array(he_server.fence) * 1e8).astype(int)
he_server.fence = vertices


@app.route('/')
def index():
    return '''
        <!doctype html>
        <title>HeGeo</title>
        <h1>Demo for geofencing using homomorphic encription</h1>
        '''


@app.route('/parms', methods=['POST'])
def set_parms():
    data = request.get_data()
    he_server.get_parms().loads(data)
    he_server.set_parms(he_server.get_parms())
    # return redirect(url_for('parameters'))
    return "parms set"


@app.route('/parameters')
def parameters():
    f = io.StringIO()
    with redirect_stdout(f):
        he_server.print_parameters()
    return render_template('parameters.html', parms=f.getvalue())


@app.route('/coordinates', methods=['POST'])
def upload_coordinates():
    data = request.get_data()
    point = he_server.load_c_arr(data)
    is_left_arr, dy_arr = he_server.compute_intermediate(point)
    is_left_flag, is_left_arr = he_server.masking(is_left_arr)
    dy_flag, dy_arr = he_server.masking(dy_arr)
    is_left_string = he_server.save_c_arr(is_left_arr)
    dy_string = he_server.save_c_arr(dy_arr)
    tasks[0]['data']['is_left'] = is_left_string
    tasks[0]['data']['dy'] = dy_string
    tasks[0]['data']['is_left_flag'] = pickle.dumps(is_left_flag)
    tasks[0]['data']['dy_flag'] = pickle.dumps(dy_flag)
    return 'is_left and dy computed'


@app.route('/is_left')
def is_left():
    return tasks[0]['data']['is_left']


@app.route('/dy')
def dy():
    return tasks[0]['data']['dy']


@app.route('/is_left_dec', methods=['POST'])
def is_left_mask():
    tasks[0]['data']['is_left_dec'] = request.get_data()
    return 'received is_left_dec'


@app.route('/dy_dec', methods=['POST'])
def dy_mask():
    tasks[0]['data']['dy_dec'] = request.get_data()
    return 'recieved dy_dec'


@app.route('/result')
def result():
    is_left_dec = pickle.loads(tasks[0]['data']['is_left_dec'])
    dy_dec = pickle.loads(tasks[0]['data']['dy_dec'])
    is_left_flag = pickle.loads(tasks[0]['data']['is_left_flag'])
    dy_flag = pickle.loads(tasks[0]['data']['dy_flag'])

    # Detection includes flag
    # is_left_dec = he_server.demasking(is_left_flag, is_left_dec)
    # dy_dec = he_server.demasking(dy_flag, dy_dec)

    res = he_server.detect_inclusion(is_left_dec, dy_dec, is_left_flag, dy_flag)
    return "Location verified" if res else "Location not verified. Service denied."


if __name__ == '__main__':
    app.run(debug=True)
