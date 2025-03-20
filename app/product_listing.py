from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField

from .models.inventory import Inventory
from .models.product import Product
from .models.review import Review

from flask import Blueprint
bp = Blueprint('product_listing', __name__)

class ProductChangeForm(FlaskForm):
    field = SelectField('Filter Type', choices = ["Name", "Price", "Description", "Image", "Category", "Available"])
    value = StringField('Filter Value')
    search = SubmitField('Search')




@bp.route('/product_listing', methods=['GET', 'POST'])
def load_page(): 
    product = Product.get(request.args.get("pid"))

    if( int(current_user.id) == product.creator):

        product_form = ProductChangeForm()

        if product_form.validate_on_submit():
            product = Product.modify(product_form.field.data, product_form.value.data, product.id)    
        return render_template('product_listing.html',
            product = product,
            product_form=product_form)

    else:
        return render_template('productpage.html',
            product = product,
            inventory = Inventory.get_entry_by_pid(product.id),
            review = Review.get_all_by_pid(product.id))

