from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login
from .review import Review


class User(UserMixin):
    def __init__(self, id, email, address, password, firstname, lastname, balance, seller):
        self.id = str(id)
        self.email = email
        self.address = address
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.seller = seller
        self.reviews = Review.get_all_by_pid(id)
        self.rating = sum([x.rating for x in self.reviews]) / len(self.reviews) if self.reviews else 0


    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
            SELECT id, email, address, password, firstname, lastname, balance, seller
            FROM Users
            WHERE email = :email
            """,
            email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][3], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0]))


    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
            SELECT email
            FROM Users
            WHERE email = :email
            """,
            email=email)
        return len(rows) > 0


    @staticmethod
    def register(email, address, password, firstname, lastname, balance, seller):
        try:
            rows = app.db.execute("""
                INSERT INTO Users(id, email, address, password, firstname, lastname, balance, seller)
                VALUES(:id, :email, :address, :password, :firstname, :lastname, :balance, :seller)
                RETURNING id
                """,
                id= app.db.execute("""
                SELECT COUNT(*) as num
                FROM Users
                """)[0][0],
                email=email,
                address=address,
                password=generate_password_hash(password),
                firstname=firstname, 
                lastname=lastname,
                balance=balance,
                seller=seller
                )
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            return None


    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
            SELECT id, email, address, password, firstname, lastname, balance, seller
            FROM Users
            WHERE id = :id
            """,
            id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def get_name(id):
        rows = app.db.execute("""
            SELECT firstname, lastname
            FROM Users
            WHERE id = :id
            """,
            id=id)
        return " ".join(rows[0])

    @staticmethod
    def get_address(id):
        rows = app.db.execute('''
        SELECT address
        FROM Users
        WHERE id = :id''', id=id)

        return str(rows[0][0])

    
    @staticmethod
    def modify_balance(uid, amount):
        app.db.execute('''
        UPDATE Users
        SET balance = balance + :amount
        WHERE id = :uid''', amount=amount, uid=uid)

    @staticmethod
    def modify(query, val, id):
        if query == "First Name":
            app.db.execute('''
                UPDATE Users
                SET firstname = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Last Name":
            app.db.execute('''
                UPDATE Users
                SET lastname = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Password":
            app.db.execute('''
                UPDATE Users
                SET password = :val
                WHERE id = :id''',
                val = generate_password_hash(val),
                id = id)
        elif query == "Email":
            app.db.execute('''
                UPDATE Users
                SET email = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Address":
            app.db.execute('''
                UPDATE Users
                SET address = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Withdraw Balance":
            app.db.execute('''
                UPDATE Users
                SET balance = :val
                WHERE id = :id''',
                val = str(float(User.get(id).balance) - float(val)),
                id = id)
        elif query == "Add Balance":
            app.db.execute('''
            UPDATE Users
            SET balance = :val
            WHERE id = :id''',
            val = str(float(User.get(id).balance) + float(val)),
            id = id)
                
        
        rows = app.db.execute('''
                SELECT id, email, address, password, firstname, lastname, balance, seller
                FROM Users
                WHERE id = :id''',
                id = id)
        return User(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_rating(uid):
        user = User.get(uid)
        review = Review.get_all_by_sid(uid)
        return "No Reviews" if not user.seller or len(review) == 0 else sum([x.rating for x in review]) / len(review)
