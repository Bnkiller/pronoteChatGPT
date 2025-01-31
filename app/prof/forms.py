from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class NoteForm(FlaskForm):
    eleve_id = SelectField("Élève", coerce=int, validators=[DataRequired()])
    matiere_id = SelectField("Matière", coerce=int, validators=[DataRequired()])
    note = FloatField("Note", validators=[DataRequired(), NumberRange(min=0, max=20)])
    coef = FloatField("Coefficient", default=1, validators=[DataRequired(), NumberRange(min=0.1, max=10)])  # Ajout du coef
    submit = SubmitField("Ajouter la note")
    classe_id = SelectField('Classe', coerce=int)  # Ajout du champ classe
