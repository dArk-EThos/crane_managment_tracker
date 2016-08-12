from DatabaseManager import db, app
from sqlalchemy.exc import DatabaseError
from sqlalchemy import func
from flask import json
from ServiceManager import get_service, Service
from sqlalchemy import and_
import os
from werkzeug.utils import secure_filename

class Page(db.Model):
    page_id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_id = db.Column(db.Integer, primary_key=True, nullable=False)
    page_items = db.relationship("PageItem", backref='page_item', lazy='dynamic')

    def __init__(self, service_id):
        self.service_id = service_id


class PageItem(db.Model):
    page_item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    page_item_image = db.Column(db.String(255))
    page_item_text = db.Column(db.Text)
    page_id = db.Column(db.Integer, db.ForeignKey('page.page_id'), nullable=False)
    page_order = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, page_item_image, page_item_text):
        self.page_item_image = page_item_image
        self.page_item_text = page_item_text

def getPageItems(service_id):

    page = getPageByServiceId(service_id)

    pageItems = db.session.query(PageItem).\
    filter(PageItem.page_id == page.page_id).\
    order_by(PageItem.page_order).\
    all()

    return pageItems

# multiple services can be associated with a single page
def getPageByServiceId(service_id):
    page = db.session.query(Page).\
    filter(Page.service_id == service_id).\
    first()

    if (page is None):
        #find other services that might fit the criteria
        service = get_service(service_id)

        services = db.session.query(Service).\
        filter(and_(Service.service_name == service.service_name, Service.engine_type == service.engine_type)).\
        all()

        for potentialService in services:
            potentialPage = db.session.query(Page).\
            filter(Page.service_id == potentialService.service_id).\
            first()

            if potentialPage is not None:
                page = potentialPage
                break


    if (page is None):
        newPage = Page(service_id)
        db.session.add(newPage)
        db.session.flush()
        return newPage

    return page

def getPageItemHighestOrder():
    order = db.session.query(func.max(PageItem.page_order).label("max_page_order")).one().max_page_order

    if order is None:
        return 0
    else:
        return order

def addPageItem(form, filename, service_id):
    try:
        newPageItem = PageItem(filename, form['text'].data)
        newPageItem.page_id = getPageByServiceId(service_id).page_id
        newPageItem.page_order = getPageItemHighestOrder() + 1

        db.session.add(newPageItem)
        db.session.commit()

    except DatabaseError as e:
        return "Database Error: " + repr(e)
    except Exception as e:
        return repr(e)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def allowed_extension(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS