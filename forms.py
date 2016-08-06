from wtforms import Form, StringField, SelectField


class CalculateForm(Form):
    upper_engine_reading = StringField('Upper Engine Hours')
    lower_engine_reading = StringField('Lower Engine Hours')
    cranes = SelectField('Select Crane', coerce=int)


class ServiceLogForm(Form):
    cranes = SelectField('Select Crane', coerce=int)