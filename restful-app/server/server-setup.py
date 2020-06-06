# http://flask.pocoo.org/docs/patterns/fileuploads/
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import hegeo
from geofencing import Fence
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
            "is_left_mask": "",
            "dy_mask": "",
            "result": "",
            "Done": False
        }
    }
]


he_server = hegeo.Server()
fence = Fence()
fence.set_vertices_from_file('data/sics.json')
vertices = np.floor(np.array(fence.vertices) * 1e8).astype(int)
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
    # TODO: Need to change the flow of setting parms with string
    he_server._set_parms(he_server.get_parms())
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
    is_left_string = he_server.save_c_arr(is_left_arr)
    dy_string = he_server.save_c_arr(dy_arr)
    tasks[0]['data']['is_left'] = is_left_string
    tasks[0]['data']['dy'] = dy_string
    return 'is_left and dy computed'


@app.route('/is_left')
def is_left():
    return tasks[0]['data']['is_left']


@app.route('/dy')
def dy():
    return tasks[0]['data']['dy']


@app.route('/is_left_mask', methods=['POST'])
def is_left_mask():
    tasks[0]['data']['is_left_mask'] = request.get_data()
    return 'received is_left_mask'


@app.route('/dy_mask', methods=['POST'])
def dy_mask():
    tasks[0]['data']['dy_mask'] = request.get_data()
    return 'recieved dy_mask'


@app.route('/result')
def result():
    is_left_mask_arr = pickle.loads(tasks[0]['data']['is_left_mask'])
    dy_mask_arr = pickle.loads(tasks[0]['data']['dy_mask'])
    res = he_server.detect_inclusion(is_left_mask_arr, dy_mask_arr)
    return "Location verified" if res else "Location not verified. Service denied."


if __name__ == '__main__':
    app.run(debug=True)
