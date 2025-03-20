from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField

from .models.inventory import Inventory
from .models.product import Product

from flask import Blueprint
bp = Blueprint('sellerpage_inventory', __name__)

class InventoryForm(FlaskForm):
    pid = IntegerField('')
    modify_stock = IntegerField('New Quantity')
    confirm = SubmitField('Update')


@bp.route('/sellerpage_inventory', methods=['GET', 'POST'])
def load_page(): 
    sellers_products = Inventory.get_by_uid(current_user.id)
    sid = current_user.firstname
    names = [Product.get_name(x.pid)[0] for x in sellers_products]

    inventory_form = InventoryForm()

    if inventory_form.validate_on_submit():
        update_inventory(inventory_form)
        return redirect(url_for('sellerpage_inventory.load_page'))
    
    return render_template('sellerpage_inventory.html', sellers_products=sellers_products, 
        inventory_form=inventory_form, sid=sid, names=names, len=len(sellers_products))

def update_inventory(inventory_form):
    new_quantity = int(inventory_form.modify_stock.data)
    uid = current_user.id
    pid = int(inventory_form.pid.data)


    if (new_quantity == 0):
        Inventory.delete(uid, pid)
    else:
        Inventory.update(new_quantity, uid, pid)
