from flask import Flask, request, render_template
from forms import CalculateForm
from flask_sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import get_debug_queries

from datetime import datetime

import ServiceManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/scottdb'
db = SQLAlchemy(app)


class Service(db.Model):
    service_id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_name = db.Column(db.String(45), nullable=False)
    service_operation = db.Column(db.String(255), nullable=False)
    service_interval = db.Column(db.Integer, nullable=False)
    service_capacity_gallons = db.Column(db.Float, nullable=True)
    service_capacity_liters = db.Column(db.Float, nullable=True)
    crane_id = db.Column(db.Integer, db.ForeignKey('crane.crane_id'), nullable=False)
    service_logs = db.relationship("ServiceLog", backref='service_log', lazy='dynamic')

    def __init__(self, name, operation, interval, crane_id, capacity_gallons=None, capacity_liters=None):
        self.name = name
        self.operation = operation
        self.interval = interval
        self.crane_id = crane_id
        self.capacity_gallons = capacity_gallons
        self.capacity_liters = capacity_liters

    def __repr__(self):
        return 'Service(name=%s, operation=%s)' % (self.name, self.operation)


class ServiceLog(db.Model):
    service_log_id = db.Column(db.Integer, primary_key=True, nullable=False)
    lastupdate = db.Column(db.DateTime, nullable=False)
    lastupdate_odo = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)

    def __init__(self, lastupdate_odo, service_id, lastupdate=datetime.now()):
        self.lastupdate_odo = lastupdate_odo
        self.lastupdate = lastupdate
        self.service_id = service_id

    def __repr__(self):
        return 'ServiceLog(name=%s, operation=%s)' % (self.name, self.operation)


class Crane(db.Model):
    crane_id = db.Column(db.Integer, primary_key=True, nullable=False)
    crane_name = db.Column(db.String(45), nullable=False)
    services = db.relationship("Service", backref='service',
                               lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Crane(name=%s)' % self.name

@app.route('/', methods=["GET", "POST"])
def calculate_services():
    form = CalculateForm(request.form)

    if request.method == 'POST' and form.validate():
        odometer_reading = request.form['odometer_reading']

        service_operations = ServiceManager.get_services(odometer_reading)

        return render_template("calculateServices.html", form=form, service_operations=service_operations,
                               odometer_reading=odometer_reading)

    else:
        return render_template("calculateServices.html", form=form)

def sql_debug(response):
    queries = list(get_debug_queries())
    query_str = ''
    total_duration = 0.0
    for q in queries:
        total_duration += q.duration
        stmt = str(q.statement % q.parameters).replace('\n', '\n       ')
        query_str += 'Query: {0}\nDuration: {1}ms\n\n'.format(stmt, round(q.duration * 1000, 2))

    print '=' * 80
    print ' SQL Queries - {0} Queries Executed in {1}ms'.format(len(queries), round(total_duration * 1000, 2))
    print '=' * 80
    print query_str.rstrip('\n')
    print '=' * 80 + '\n'

    return response

app.after_request(sql_debug)

if __name__ == '__main__':
    app.run(debug=True)
