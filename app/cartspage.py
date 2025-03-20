from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime

from .models.inventory import Inventory
from .models.cart import Cart
from .models.product import Product
from .models.user import User

from flask import Blueprint
bp = Blueprint('cartspage', __name__)


class ModifyQuantityForm(FlaskForm):
    id = IntegerField('')
    new_quantity = IntegerField()
    submit = SubmitField('Update')


@bp.route('/cartspage', methods=['GET', 'POST'])
def load_page():
    modify_quantity_form = ModifyQuantityForm()

    cart = Cart.get_all_by_uid(current_user.id)        
    prices = Cart.get_prices(cart)
    prices = [prices[x] * cart[x].quantity for x in range(len(prices))]
    names = [[Product.get_name(cart[x].pid)[0], User.get_name(cart[x].sid)] for x in range(len(prices))]
    if modify_quantity_form.validate_on_submit():
        id = modify_quantity_form.id.data
        new_quantity = modify_quantity_form.new_quantity.data

        if new_quantity == 0:
            Cart.delete(id)
        else:
            Cart.modify_quantity(id, new_quantity)

        return redirect(url_for('cartspage.load_page'))

    return render_template('cartspage.html', cart=cart, modify_quantity_form=modify_quantity_form, 
        prices=prices, num_items=len(cart), names=names, total=sum(prices))


@bp.route('/cartspage_checkout', methods=['GET', 'POST'])
def checkout():
    cart = Cart.get_all_by_uid(current_user.id)
    prices = Cart.get_prices(cart)
    prices = [prices[x] * cart[x].quantity for x in range(len(prices))]
    total =  sum(prices)
    if total > current_user.balance: 
       flash('Not enough funds. Deposit more or remove items.')
       return redirect(url_for('cartspage.load_page'))

    for item in cart:
        stock = Inventory.get_quantity(item.sid, item.pid)
        if (stock < item.quantity):
            flash('Not enough stock, can only checkout ' + str(stock) + 
                ' items. Please modify quantity to that amount.')
            return redirect(url_for('cartspage.load_page'))

    # redirect to checkout
    return redirect(url_for('checkoutpage.load_page'))


        