from flask import Flask, render_template, flash, send_file  # import flask and their classes
from flask_wtf import FlaskForm  # flask form for uploading zip files
from flask_wtf.file import FileAllowed, FileRequired  # allowed files
from wtforms import FileField  # file field for uploading files
import patoolib  # for extracting archive files
import shutil  # removing files from pwd
from werkzeug.utils import secure_filename  # get file name
import os  # os related operations
import json  # jsonify lists

app = Flask(__name__)  # initialize flask app
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'  # secret key for authentication
global extracted_path, folder_path


class UploadForm(FlaskForm):  # class for fileField form
    file = FileField(label="Select file : ",
                     validators=[FileAllowed(['zip', 'rar']), FileRequired()])  # validators only allow zip files


def extract_zip(file_name):  # extract zip method
    child_dir_path = os.path.join("extracted_files", file_name)  # prepare path for sub folder
    try:
        shutil.rmtree(child_dir_path)  # removing files from sub-folder
    except OSError:
        os.makedirs(child_dir_path)  # If folder was not their then it created.

    try:
        patoolib.extract_archive(os.path.join('ZipFiles/', file_name), outdir=child_dir_path)  # extract file
        os.remove(os.path.join('ZipFiles/', file_name))  # remove copied zip or rar file
    except Exception as error:  # exception if zip or rar is corrupt
        flash("Your ZIP or RAR files is Corrupted.", category='danger')
        print("Exception : {}".format(error))
    return child_dir_path


@app.route("/", methods=['GET', 'POST'])  # index route
@app.route('/upload', methods=['GET', 'POST'])  # upload route
def upload_route():  # method for uploading zip file
    global extracted_path
    form = UploadForm()  # initialize form object
    if form.validate_on_submit():  # if data is valid then process further
        zip_file = form.file.data  # get file in zip_file var
        file_name = secure_filename(form.file.data.filename)  # get filename
        os.makedirs('ZipFiles', exist_ok=True)  # make ZipFile directory for storing zip or rar files temporary
        zip_file.save(os.path.join('ZipFiles/', file_name))  # save file
        extracted_path = extract_zip(file_name)  # extract zip file
        file_names = []  # prepare list
        for file in os.walk(extracted_path):  # check for directory
            if not file[-1]:  # if it contains directory then last index are empty.
                pass
            else:
                file_names.append(file[-1])  # filenames located in last index
        return render_template("shownZipFiles.html", files=file_names, json_file_names=json.dumps(file_names))
    else:
        # if file are not validate then print flash message
        flash("Please, Select only ZIP or RAR files.", category='danger')
    return render_template("uploadZip.html", form=form)  # call "uploadZip.html" with form


@app.route("/<file_name>", methods=['GET', 'POST'])  # route for downloading file
def download_file(file_name):  # method for download file
    global extracted_path, folder_path

    for file in os.walk(extracted_path):  # walk through all files
        if file_name in file[-1]:  # check file is presented in list or not
            folder_path = file[0]  # store path of file in folder_path

    file_path = folder_path + "/" + file_name  # file path, where file is located
    return send_file(file_path, as_attachment=True)  # send_file() send content to client pc.


if __name__ == '__main__':  # init main
    app.run('0.0.0.0', debug=True)  # run app in debug mode
