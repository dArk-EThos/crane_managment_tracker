from app import db, Service, ServiceLog
from sqlalchemy.sql import func
from flask import Markup, escape

# get the services that need to be operated on based upon the entered odometer reading
def get_services(odometer_reading):

    services_and_logs = db.session.query(Service, ServiceLog).outerjoin(ServiceLog).\
                        filter((func.ifnull(ServiceLog.lastupdate_odo, 0) + Service.service_interval) <= Markup.escape(odometer_reading)).\
                        all()

    services = []

    for service, service_log in services_and_logs:

        if service_log is None:
            lastupdate = "No Record"
        else:
            lastupdate = service_log.lastupdate

        services.append(
            {"service_id": service.service_id,
             "service_name": service.service_name,
             "service_operation": service.service_operation,
             "service_interval": service.service_interval,
             "service_lastupdate": lastupdate})

    return services