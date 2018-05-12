from flask_wtf import Form
from wtforms import validators, PasswordField, StringField, TextAreaField, SelectField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired

class LogInForm(Form):
    username = StringField('username', [DataRequired()])
    password = PasswordField('password', [DataRequired()])

class RegisterForm(Form):
    username = StringField('username', [DataRequired(), validators.Length(min=3, max=16)])
    password = PasswordField('password', [DataRequired(), validators.Length(min=6, max=20)])
    repeatPassword = PasswordField('repeatPassword', [DataRequired(), validators.Length(min=6, max=20)])

class ChangePassForm(Form):
    oldPassword = PasswordField('oldPassword', [DataRequired()])
    newPassword = PasswordField('newPassword', [DataRequired(), validators.Length(min=6, max=20)])
    repeatNewPassword = PasswordField('repeatNewPassword', [DataRequired(), validators.Length(min=6, max=20)])

class AddListForm(Form):
    listTitle = StringField('listTitle', [DataRequired(), validators.Length(min=1, max=30)])
    listDescription = TextAreaField('listDescription')

class EditListForm(Form):
    listTitle = StringField('listTitle', [DataRequired(), validators.Length(min=1, max=30)])
    listDescription = TextAreaField('listDescription')
    booksToAdd = SelectMultipleField('booksToAdd', coerce=int ,choices=[])
    booksToRemove = SelectMultipleField('booksToRemove', coerce=int ,choices=[])

class AddBookForm(Form):
    bookTitle = StringField('bookTitle', [DataRequired(), validators.Length(min=1, max=50)])
    bookRating = RadioField('bookRating', choices=[('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5')])
    addBookToList =  SelectMultipleField('addBookToList', coerce=int ,choices=[])
