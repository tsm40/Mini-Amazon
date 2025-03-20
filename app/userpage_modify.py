from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User

from flask import Blueprint
bp = Blueprint('userpage_modify', __name__)

class ProfileChangeForm(FlaskForm):
    field = SelectField('Filter Type', choices = ["First Name", "Last Name", "Password", "Email", "Address", "Add Balance", "Withdraw Balance"])
    value = StringField('Filter Value', validators=[DataRequired()]) 
    change = SubmitField('Change')


@bp.route('/userpage_modify', methods=['GET', 'POST'])
def load_page():  
    user = User.get(current_user.id)

    profile_form = ProfileChangeForm()
    if profile_form.validate_on_submit():
        value = profile_form.value.data
        if(profile_form.field.data == "Email" and User.email_exists(value)):
            flash("Email Already Exists")
        elif(profile_form.field.data in ["Withdraw Balance", "Add Balance"] and not value.replace('.', '', 1).isdigit()):
            flash("Please input a number")
        elif(profile_form.field.data == "Withdraw Balance" and User.get(current_user.id).balance < float(value)):
            flash("You do not have this much money!")
        else:
            user = User.modify(profile_form.field.data, profile_form.value.data, user.id)
    return render_template('userpage_modify.html',
        user = user,
        profile_form=profile_form)
