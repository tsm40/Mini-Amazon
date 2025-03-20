from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, DecimalField

from .models.inventory import Inventory
from .models.purchase import Purchase
from .models.product import Product

from flask import Blueprint
bp = Blueprint('sellerpage_add_product', __name__)

class AddProductForm(FlaskForm):
    name = StringField()
    price = DecimalField()
    category = StringField()
    long_description = StringField()
    image_link = StringField() 
    quantity = IntegerField()
    submit = SubmitField()


@bp.route('/sellerpage_add_product', methods=['GET', 'POST'])
def load_page(): 
    creator = current_user.id
    available = True
    rating = 0

    add_product_form = AddProductForm()

    if add_product_form.validate_on_submit():
        name = add_product_form.name.data
        price = add_product_form.price.data
        category = add_product_form.category.data
        long_description = add_product_form.long_description.data
        image_link = add_product_form.image_link.data
        quantity = add_product_form.quantity.data

        process = add_product(name, price, available, category, 
            long_description, image_link, creator, rating, quantity)
        
        if not process:
            flash('ENTER A UNIQUE PRODUCT NAME')
    
        return redirect(url_for('sellerpage_add_product.load_page'))
    
    return render_template('sellerpage_add_product.html', add_product_form=add_product_form, sid=current_user.firstname)


def add_product(name, price, available, category, long_description, 
    image_link, creator, rating, quantity):
    process_1 = Product.add_product(name, price, available, 
        category, long_description, image_link, creator, rating)
    process_2 = False
    if process_1:       
        process_2 = Inventory.add_product(creator, process_1, quantity)

    return process_1 and process_2

    