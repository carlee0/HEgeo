# http://flask.pocoo.org/docs/patterns/fileuploads/
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
import hegeo
from geofencing import Fence
import numpy as np
import os
import io
from contextlib import redirect_stdout

UPLOAD_FOLDER = 'files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# tasks = [
#     {
#         "fence": "",
#         "coordinates": {
#             "coords": "Ciphertext_coords",
#             "coords_size": "size_array_coords"
#         }
#     }
# ]
interm_results = {
    'is_left': None,
    'dy': None
}

he_server = hegeo.Server()
fence = Fence()
fence.set_vertices_from_file('data/sics.json')
vertices = np.floor(np.array(fence.vertices) * 1e8).astype(int)
he_server.fence = vertices


@app.route('/set_parms', methods=['GET', 'POST'])
def set_parms():
    if request.method == 'POST':
        file_path = save_file(request.files['file'])
        he_server.load_parms(file_path)
        return redirect(url_for('parameters'))
    return '''
        <!doctype html>
        <title>Set parameters</title>
        <h1>Upload the parameter file</h1>
        <form action="" method=post enctype=multipart/form-data>
        <p>Add the parameter file  <input type=file name=file>
            <input type=submit value=Upload>
        </form>
        '''


@app.route('/parameters')
def parameters():
    f = io.StringIO()
    with redirect_stdout(f):
        he_server.print_parameters()
    return render_template('parameters.html', parms=f.getvalue())


@app.route('/coordinates', methods=['GET', 'POST'])
def upload_coordinates():
    if request.method == 'POST':
        keys = ['point_size', 'point']
        file_names = []
        for k in keys:
            file_path = save_file(request.files[k])
            file_names.append(file_path)
        point = he_server.load_cipher_array(file_names[0], file_names[1])
        is_left, dy = he_server.compute_intermediate(point)
        interm_results['is_left'] = is_left
        interm_results['dy'] = dy
        he_server.save_cipher_array(is_left,
                                    os.path.join(app.config['UPLOAD_FOLDER'], 'is_left_size'),
                                    os.path.join(app.config['UPLOAD_FOLDER'], 'is_left'))
        he_server.save_cipher_array(dy,
                                    os.path.join(app.config['UPLOAD_FOLDER'], 'dy_size'),
                                    os.path.join(app.config['UPLOAD_FOLDER'], 'dy'))

        return 'is_left and dy computed'

    return '''
    <!doctype html>
    <title>Upload Ciphertext files for the points</title>
    <h1>Upload Ciphertext files for the points</h1>
    <form action="" method=post enctype=multipart/form-data>
    <p>Add the point_size file  <input type=file name=point_size>
        <input type=submit value=Upload>
    <p>Add the dy_size file  <input type=file name=dy_size>
        <input type=submit value=Upload>
    </form>
    '''


@app.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/results', methods=['GET', 'POST'])
def upload_results():
    if request.method == 'POST':
        keys = ['is_left_mask', 'dy_mask']
        file_names = []
        for k in keys:
            file_path = save_file(request.files[k])
            file_names.append(file_path)
        is_left_mask = he_server.load_array(os.path.join(app.config['UPLOAD_FOLDER'],
                                                         'is_left_mask'))
        dy_mask = he_server.load_array(os.path.join(app.config['UPLOAD_FOLDER'],
                                                    'dy_mask'))
        result = he_server.detect_inclusion(is_left_mask, dy_mask)
        return "Location verified" if result else "Location not verified. Service denied."


def save_file(file):
    # TODO: mkdir if not exist
    print('---- Received file "%s"' % file.filename)
    file_name = secure_filename(file.filename)
    folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, file_name)
    file.save(file_path)
    print('---- Save file to: ', file_path)
    return file_path


if __name__ == '__main__':
    app.run(debug=True)
