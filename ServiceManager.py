from sqlalchemy.sql import func
from sqlalchemy.exc import DatabaseError
from flask import Markup, escape
from datetime import datetime

from DatabaseManager import db

class Service(db.Model):
    service_id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_name = db.Column(db.String(45), nullable=False)
    service_operation = db.Column(db.String(255), nullable=False)
    service_interval = db.Column(db.Integer, nullable=False)
    service_capacity_gallons = db.Column(db.Float, nullable=True)
    service_capacity_liters = db.Column(db.Float, nullable=True)
    crane_id = db.Column(db.Integer, db.ForeignKey('crane.crane_id'), nullable=False)
    engine_type = db.Column(db.Enum("upper", "lower"), nullable=False)
    service_logs = db.relationship("ServiceLog", backref='service_log', lazy='dynamic')
    service_audits = db.relationship("ServiceLog", backref='service_audit', lazy='dynamic')

    def __init__(self, name, operation, interval, crane_id, capacity_gallons=None, capacity_liters=None):
        self.service_name = name
        self.service_operation = operation
        self.service_interval = interval
        self.crane_id = crane_id
        self.service_capacity_gallons = capacity_gallons
        self.service_capacity_liters = capacity_liters

    def __repr__(self):
        return 'Service(service_name=%s, service_operation=%s)' % (
            self.service_name, self.service_operation
        )


class ServiceLog(db.Model):
    service_log_id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_log_lastupdate = db.Column(db.DateTime, nullable=False)
    service_log_lastupdate_odo = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)

    def __init__(self, service_log_lastupdate_odo, service_id, service_log_lastupdate=datetime.now()):
        self.service_log_lastupdate_odo = service_log_lastupdate_odo
        self.service_log_lastupdate = service_log_lastupdate
        self.service_id = service_id

    def __repr__(self):
        return 'ServiceLog(lastupdate=%s, lastupdate_odo=%s, service_id=%s)' % (
            self.lastupdate, self.lastupdate_odo, self.service_id
        )

class ServiceAudit(db.Model):
    service_audit_id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_audit_message = db.Column(db.Text, nullable=True)
    service_audit_lastupdate = db.Column(db.DateTime, nullable=False)
    service_audit_lastupdate_odo = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)

    def __init__(self, service_audit_lastupdate_odo, service_id, service_audit_message=""):
        self.service_audit_lastupdate_odo = service_audit_lastupdate_odo
        self.service_audit_lastupdate = datetime.now()
        self.service_id = service_id
        self.service_audit_message = service_audit_message

    def __repr__(self):
        return 'ServiceAudit(lastupdate=%s, lastupdate_odo=%s, service_id=%s)' % (
            self.lastupdate, self.lastupdate_odo, self.service_id
        )


class Crane(db.Model):
    crane_id = db.Column(db.Integer, primary_key=True, nullable=False)
    crane_name = db.Column(db.String(45), nullable=False)
    services = db.relationship("Service", backref='service',
                               lazy='dynamic')

    def __init__(self, crane_name):
        self.crane_name = crane_name

    def __repr__(self):
        return 'Crane(crane_name=%s)' % self.crane_name


def get_services(upper_engine_reading, lower_engine_reading, crane_id):

    services_and_logs_upper = db.session.query(Service, ServiceLog).outerjoin(ServiceLog).\
                    filter((func.ifnull(ServiceLog.service_log_lastupdate_odo, 0) + Service.service_interval) <= Markup.escape(upper_engine_reading)).\
                    filter(Service.crane_id == crane_id).\
                    filter(Service.engine_type == "upper")

    services_and_logs_lower = db.session.query(Service, ServiceLog).outerjoin(ServiceLog).\
                filter((func.ifnull(ServiceLog.service_log_lastupdate_odo, 0) + Service.service_interval) <= Markup.escape(lower_engine_reading)).\
                filter(Service.crane_id == crane_id).\
                filter(Service.engine_type == "lower")

    services_and_logs = services_and_logs_upper.union_all(services_and_logs_lower)

    services = []

    for service, service_log in services_and_logs:

        if service_log is None:
            lastupdate = "No Record"
        else:
            lastupdate = service_log.service_log_lastupdate

        services.append(
            {"service_id": service.service_id,
             "service_name": service.service_name,
             "service_operation": service.service_operation,
             "service_interval": service.service_interval,
             "engine_type": service.engine_type.capitalize(),
             "service_lastupdate": "<no record>" if service_log is None else service_log.service_log_lastupdate.strftime("%B %d, %Y"),
             "service_lastupdate_odo": "<no record>" if service_log is None else service_log.service_log_lastupdate_odo})

    return services

def markServicesComplete(logItems):

    try:
        for logItem in logItems:

            oldLogs = ServiceLog.query.filter_by(service_id=logItem.get('service_id')).all()

            if len(oldLogs) != 0:
                for log in oldLogs:
                    db.session.delete(log)

            new_odometer_reading = logItem.get('odometer_reading')
            service_id = logItem.get('service_id')

            newLog = ServiceLog(new_odometer_reading, service_id)
            newServiceAudit = ServiceAudit(new_odometer_reading, service_id, "Service was marked completed at " + new_odometer_reading + " hours.")

            db.session.add(newLog)
            db.session.add(newServiceAudit)
            db.session.commit()

    except DatabaseError:
        return "ERROR: Could not establish connection with database."
    else:
        "ERROR"

    return "OK"

def changeServices(serviceItems):

    try:
        for serviceItem in serviceItems:

            serviceLog = ServiceLog.query.filter_by(service_id=serviceItem.get('service_id')).order_by(ServiceLog.service_log_lastupdate.desc()).first()
            newServiceAudit = ServiceAudit(serviceItem.get('service_lastupdate_odo'), serviceItem.get('service_id'), "Manual record adjustment.")

            if (serviceLog is None):
                #handle somehow
                pass

            service = Service.query.filter_by(service_id=serviceItem.get('service_id')).order_by(Service.service_id).first()

            if (service is None):
                #handle somehow
                pass

            serviceLog.service_log_lastupdate_odo = serviceItem.get('service_lastupdate_odo')
            service.service_name = serviceItem.get('service_name')
            service.service_operation = serviceItem.get('service_operation')
            service.service_interval = serviceItem.get('service_interval')

            db.session.add(newServiceAudit)
            db.session.commit()

    except DatabaseError:
        return "ERROR: Could not establish connection with database."
    else:
        "ERROR"

    return "OK"

def get_service_logs(crane_id):
    try:

        services_and_logs = db.session.query(Service, ServiceLog).outerjoin(ServiceLog).\
            filter(Service.crane_id == crane_id).\
            order_by(ServiceLog.service_log_lastupdate.desc()).\
            all()

        services = []

        for service, service_log in services_and_logs:

            if service_log is None:
                lastupdate = "No Record"
            else:
                lastupdate = service_log.service_log_lastupdate

            services.append(
                {"service_id": service.service_id,
                 "service_lastupdate": service_log.service_log_lastupdate.ctime() if service_log else "<no record>",
                 "service_lastupdate_odo": service_log.service_log_lastupdate_odo if service_log else "<no record>",
                 "service_name": service.service_name,
                 "service_operation": service.service_operation,
                 "engine_type": service.engine_type.capitalize(),
                 "service_interval": service.service_interval})

        return services

    except DatabaseError:
        return "ERROR: Could not establish connection with database."