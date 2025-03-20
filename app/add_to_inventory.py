from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField

from .models.inventory import Inventory
from .models.purchase import Purchase
from .models.product import Product

from flask import Blueprint
bp = Blueprint('add_to_inventory', __name__)

class AddToInventoryForm(FlaskForm):
    quantity = IntegerField()
    submit = SubmitField('Add To Inventory')


@bp.route('/add_to_inventory', methods=['GET', 'POST'])
def load_page():
    pid = int(request.args.get("pid"))
    add_to_inventory_form = AddToInventoryForm()
    if add_to_inventory_form.validate_on_submit():
        Inventory.add_product(current_user.id, pid, 
            add_to_inventory_form.quantity.data)
        return redirect(url_for('productpage.load_product') + '?pid=' + str(pid)) 
    
    return render_template('add_to_inventory.html', add_to_inventory_form=add_to_inventory_form)
    