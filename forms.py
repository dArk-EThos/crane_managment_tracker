from wtforms import Form, StringField, SelectField, FileField, TextAreaField, PasswordField, validators


class CalculateForm(Form):
    upper_engine_reading = StringField('Upper Engine Hours', validators=[validators.Regexp('^-?[0-9]*$', message="Must enter a number")])
    lower_engine_reading = StringField('Lower Engine Hours', validators=[validators.Regexp('^-?[0-9]*$', message="Must enter a number")])
    cranes = SelectField('Select Crane', coerce=int, validators=[validators.DataRequired()])


class ServiceLogForm(Form):
    cranes = SelectField('Select Crane', coerce=int, validators=[validators.DataRequired()])


class PageItemForm(Form):
    image_upload = FileField()
    text = TextAreaField('Text')
    password = PasswordField('Passcode')
