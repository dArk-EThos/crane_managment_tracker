from DatabaseManager import db

class Page(db.Model):
    page_id = db.Column(db.Integer, primary_key=True, nullable=False)
    service_id = db.Column(db.Integer, primary_key=True, nullable=False)
    page_items = db.relationship("PageItem", backref='page_item', lazy='dynamic')


class PageItem(db.Model):
    page_item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    page_item_image = db.Column(db.String(255))
    page_item_text = db.Column(db.Text)
    page_id = db.Column(db.Integer, db.ForeignKey('page.page_id'), nullable=False)


def getPageItems(service_id):

    pageItems = db.session.query(PageItem).\
            filter(Page.service_id == service_id).\
            all()

    return pageItems