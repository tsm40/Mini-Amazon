from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from datetime import datetime

from .models.user import User
from .models.purchase import Purchase
from .models.product import Product
from .models.review import Review, ReviewAddForm, ReviewChangeForm
from .models.vote import Vote, VoteForm


from flask import Blueprint
bp = Blueprint('users', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    seller = BooleanField('Seller')
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(
            form.email.data,
            form.address.data,
            form.password.data,
            form.firstname.data,
            form.lastname.data,
            0,
            form.seller.data
            ):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

class ReviewInfo:
    def __init__(self, review):
        self.review = review
        self.reviewer_name = User.get_name(self.review.uid)
        self.reviewed_name = User.get_name(self.review.rid) if self.review.is_seller else Product.get_name(self.review.rid)[0]

class PurchaseInfo:
    def __init__(self, purchase):
        self.purchase = purchase
        self.product_name = Product.get_name(self.purchase.pid)[0]
        self.seller_name = User.get_name(self.purchase.sid)
        self.price = Product.get_price(self.purchase.pid, self.purchase.sid) * self.purchase.quantity

class FilterForm(FlaskForm):
    sort = SelectField('Filter Type', choices = ["None", "Rating", "Time"])
    # sort_purchase = SelectField('Filter Type Purchase', choices = ["None", "Time", "Price", "Product Name", "Seller Name"])
    order = SelectField('Filter Order', choices = ["High to Low", "Low to High"])
    search = SubmitField('Sort')

class FilterFormPurchase(FlaskForm):
    sort = SelectField('Filter Type Purchase', choices = ["None", "Time", "Price", "Product Name", "Seller Name"])
    order = SelectField('Filter Order', choices = ["High to Low", "Low to High"])
    search = SubmitField('Sort')

@bp.route('/userpage/', methods=['GET', 'POST'])
def userpage():
    user = User.get(request.args.get("uid"))
    user_review = Review.get_by_uid_rid(current_user.id, user.id, True) if current_user.is_authenticated else None
    has_bought = Purchase.has_uid_bought_from_sid(current_user.id, user.id) if current_user.is_authenticated else None

    review_add_form = ReviewAddForm()
    filter_form_for = FilterForm()
    filter_form_by = FilterForm()
    filter_form_purchases = FilterFormPurchase()
    vote_form = VoteForm()

    if (vote_form.downvote.data or vote_form.upvote.data) and vote_form.validate():
        user_vote = Vote.get_by_uid_rid(current_user.id, vote_form.rid.data) if current_user.is_authenticated else None
        if vote_form.upvote.data:
            if user_vote == 1:
                Vote.modify(current_user.id, vote_form.rid.data, 'Remove')
            elif user_vote == -1:
                    Vote.modify(current_user.id, vote_form.rid.data, 'Upvote')
            else:
                Vote.submit_new_vote(current_user.id, vote_form.rid.data, 'Upvote')
        elif vote_form.downvote.data:
            if user_vote == -1:
                Vote.modify(current_user.id, vote_form.rid.data, 'Remove')
            elif user_vote == 1:
                    Vote.modify(current_user.id, vote_form.rid.data, 'Downvote')
            else:
                Vote.submit_new_vote(current_user.id, vote_form.rid.data, 'Downvote')
        return redirect(url_for('users.userpage')  + '?uid=' + str(user.id))

    if review_add_form.submit_review.data and review_add_form.validate():
        if not user_review and review_add_form.rating.data in Review.acceptable_ratings:
                Review.submit_new_review(review_add_form.rating.data,review_add_form.content.data, datetime.now(), current_user.id, user.id, True)
        return redirect(url_for('users.userpage')  + '?uid=' + str(user.id))

    reviews_for = Review.get_all_by_sid(request.args.get("uid"))
    reviews_by = Review.get_all_by_uid(user.id)
    purchases = Purchase.get_all_by_uid(current_user.id) if current_user.is_authenticated else None

    vote_status = {}
    for rev in reviews_for:  # calculate user's vote status for each review
        vote_status[rev.id] = Vote.get_by_uid_rid(current_user.id, rev.id)

    if filter_form_for.validate_on_submit():
        if filter_form_for.sort.data == "Rating":
            reviews_for = sorted(reviews_for, key = lambda x : x.rating, reverse = filter_form_for.order.data == "High to Low")
        elif filter_form_for.sort.data == "Time":
            reviews_for = sorted(reviews_for, key = lambda x : x.review_time, reverse = filter_form_for.order.data == "High to Low")
        
    if filter_form_by.validate_on_submit():
        if filter_form_by.sort.data == "Rating":
            reviews_by.sort(key = lambda x : x.rating, reverse = filter_form_by.order.data == "High to Low")
        elif filter_form_by.sort.data == "Time":
            reviews_by.sort(key = lambda x : x.review_time, reverse = filter_form_by.order.data == "High to Low")


    if filter_form_purchases.validate_on_submit():
        if filter_form_purchases.sort.data == "Time":
            purchases.sort(key = lambda x : x.time_purchased, reverse = filter_form_purchases.order.data == "High to Low")
        elif filter_form_purchases.sort.data == "Price":
            purchases.sort(key = lambda x : Product.get_price(x.pid, x.sid) * x.quantity, reverse = filter_form_purchases.order.data == "High to Low")
        elif filter_form_purchases.sort.data == "Product Name":
            purchases.sort(key = lambda x : Product.get_name(x.pid), reverse = filter_form_purchases.order.data == "High to Low")
        elif filter_form_purchases.sort.data == "Seller Name":
            purchases.sort(key = lambda x : User.get_name(x.sid), reverse = filter_form_purchases.order.data == "High to Low")

    purchase_history = [PurchaseInfo(x) for x in purchases] if current_user.is_authenticated else None
    reviews_for_info = [ReviewInfo(x) for x in reviews_for]
    reviews_by_info = [ReviewInfo(x) for x in reviews_by]
    average = User.get_rating(user.id)

    return render_template('userpage.html',
        user = user,
        reviews_for_info = reviews_for_info,
        reviews_by_info = reviews_by_info,
        purchase_history = purchase_history,
        average = average,
        user_review = user_review,
        vote_status = vote_status,
        review_add_form = review_add_form,
        filter_form_for = filter_form_for,
        filter_form_by = filter_form_by,
        filter_form_purchases = filter_form_purchases,
        has_bought=has_bought,
        vote_form=vote_form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

