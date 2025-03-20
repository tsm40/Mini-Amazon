from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField

from .models.inventory import Inventory
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('sellerpage', __name__)


@bp.route('/sellerpage', methods=['GET', 'POST'])
def load_page():  
    sid = current_user.firstname
    
    sales = Purchase.get_sales(current_user.id)
    sales = sales[:5 if len(sales) >= 5 else len(sales)]
    labels = [row[0][0] for row in sales]
    values = [row[1] for row in sales]

    return render_template('sellerpage.html', sid=sid, labels=labels, values=values, max=17000)



