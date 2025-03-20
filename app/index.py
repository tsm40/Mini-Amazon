from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, BooleanField
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('index', __name__)

class FilterForm(FlaskForm):
    filter = SelectField('Filter Type', choices = ["Category", "Search For", "Rating"])
    value = StringField('Filter Value')
    sort = SelectField('Filter Type', choices = ["None", "Price", "Name", "Rating"])
    order = SelectField('Filter Order', choices = ["High to Low", "Low to High"])
    search = SubmitField('Search')

@bp.route('/', methods=['GET', 'POST'])
def index():
    # get all available products for sale:
    products = Product.get_all(True)
    # get top selling product:
    topselling = Product.get_topselling()
    print(topselling[0])
    # render the page by adding information to the index.html file

    filter_form = FilterForm()

    if filter_form.validate_on_submit():
        products = Product.get_query(filter_form.filter.data, filter_form.value.data) if filter_form.value.data else Product.get_all(True)
        if filter_form.sort.data == "Price":
            products.sort(key = lambda x : x.price, reverse = filter_form.order.data == "High to Low")
        elif filter_form.sort.data == "Name":
            products.sort(key = lambda x : x.name, reverse = filter_form.order.data == "High to Low")
        if filter_form.filter.data == "Rating" and filter_form.value.data != "":
            products = [x for x in products if x.rating == (float(filter_form.value.data) if filter_form.value.data.isdigit() else filter_form.value.data)]
        if filter_form.sort.data == "Rating":
            products.sort(key = lambda x : x.rating if isinstance(x.rating,float) else 0, reverse = filter_form.order.data == "High to Low")
    return render_template('index.html',
                    avail_products=products,
                    top_product=topselling[0],
                    times_sold=topselling[1],
                    filter_form=filter_form)

