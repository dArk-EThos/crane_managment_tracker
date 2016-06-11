from wtforms import Form, StringField


class CalculateForm(Form):
    odometer_reading = StringField('Odometer Reading')