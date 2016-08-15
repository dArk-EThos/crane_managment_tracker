from flask import request, render_template
from werkzeug.utils import secure_filename
import os

from ServiceManager import *
from PageManager import *
from DatabaseManager import app
from forms import CalculateForm, ServiceLogForm, PageItemForm

@app.route('/', methods=["GET", "POST"])
def calculate_services():
    isPost = False
    form = CalculateForm(request.form)
    form.cranes.choices = [(c.crane_id, c.crane_name) for c in Crane.query.all()]

    if request.method == 'POST' and form.validate():
        isPost = True
        upper_engine_reading = request.form['upper_engine_reading']
        lower_engine_reading = request.form['lower_engine_reading']
        crane_id = request.form['cranes']

        service_operations = get_services(upper_engine_reading, lower_engine_reading, crane_id)

        return render_template("calculateServices.html", form=form, isPost=isPost, service_operations=service_operations,
                               upper_engine_reading=upper_engine_reading, lower_engine_reading=lower_engine_reading)

    else:
        return render_template("calculateServices.html", form=form, isPost=isPost)

@app.route('/service/update', methods=["POST"])
def update_services():
    content = request.json
    result = markServicesComplete(content)

    return result

@app.route('/service/adminUpdate', methods=["POST"])
def admin_update_services():
    content = request.json
    result = changeServices(content)

    return result

@app.route('/services', methods=["GET", "POST"])
def list_service_logs():
    isPost = False
    form = ServiceLogForm(request.form)
    form.cranes.choices = [(c.crane_id, c.crane_name) for c in Crane.query.all()]

    if request.method == 'POST' and form.validate():

        isPost = True

        crane_id = request.form['cranes']

        service_logs = get_service_logs(crane_id)

        return render_template("servicelogs.html", form=form, isPost=isPost, service_logs=service_logs)

    else:
        return render_template("servicelogs.html", form=form, isPost=isPost)


@app.route('/service/<service_id>', methods=["GET", "POST"])
def service_detail(service_id):

    form = PageItemForm(request.form)

    if request.method == "POST" and form.validate() and form["password"].data == "scott":
        file = request.files['image_upload']
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        filename = secure_filename(file.filename)

        if (allowed_extension(filename)):
            file.save(os.path.join(APP_ROOT, 'static/img', filename))
            addPageItem(form, filename, service_id)
        else:
            raise TypeError("Invalid File Extension.")

    page_items = getPageItems(service_id)
    service = get_service(service_id)

    return render_template("serviceDetail.html", form=form, page_items=page_items, service_name=service.service_name, service_id=service_id)

@app.route('/sql', methods=["GET"])
def sql():

    from filereader import readfile

    lines = readfile()

    return render_template("file.html", lines=lines)


if __name__ == '__main__':
    app.run(debug=True)

