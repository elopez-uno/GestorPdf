from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FileField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Optional


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    submit = SubmitField('Cambiar contraseña')


class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Nombre completo', validators=[DataRequired(), Length(max=200)])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    role = SelectField('Rol', choices=[('user', 'Usuario'), ('admin', 'Administrador')],
                       validators=[DataRequired()])
    office_id = SelectField('Oficina', coerce=int, validators=[Optional()])
    is_active = BooleanField('Activo')
    submit = SubmitField('Guardar')


class OfficeForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descripción', validators=[Optional()])
    is_active = BooleanField('Activo')
    submit = SubmitField('Guardar')


class TagForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Guardar')


class DocumentForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=300)])
    description = TextAreaField('Descripción', validators=[Optional()])
    tags = StringField('Etiquetas (separadas por coma)', validators=[Optional()])
    file = FileField('Archivo PDF', validators=[DataRequired()])
    office_id = SelectField('Oficina', coerce=int, validators=[Optional()])
    submit = SubmitField('Subir documento')


class DocumentEditForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=300)])
    description = TextAreaField('Descripción', validators=[Optional()])
    tags = StringField('Etiquetas (separadas por coma)', validators=[Optional()])
    office_id = SelectField('Oficina', coerce=int, validators=[Optional()])
    submit = SubmitField('Actualizar')


class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[Optional()])
    tag_id = SelectField('Etiqueta', coerce=int, validators=[Optional()])
    office_id = SelectField('Oficina', coerce=int, validators=[Optional()])
    date_from = StringField('Fecha desde', validators=[Optional()])
    date_to = StringField('Fecha hasta', validators=[Optional()])
    submit = SubmitField('Buscar')
