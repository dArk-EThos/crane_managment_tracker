from flask import request, render_template
from forms import CalculateForm, ServiceLogForm

from ServiceManager import *
from PageManager import *
from DatabaseManager import app

@app.route('/', methods=["GET", "POST"])
def calculate_services():
    isPost = False
    form = CalculateForm(request.form)
    form.cranes.choices = [(c.crane_id, c.crane_name) for c in Crane.query.all()]

    if request.method == 'POST':
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


@app.route('/service/<service_id>', methods=["GET"])
def service_detail(service_id):

    page_items = getPageItems(service_id)

    return render_template("serviceDetail.html", page_items=page_items)

if __name__ == '__main__':
    app.run(debug=True)