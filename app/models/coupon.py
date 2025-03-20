from flask import current_app as app


class Coupon:
    
    def __init__(self, id, discount, users):
        self.id = id
        self.discount = discount
        self.users = users

    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT *
        FROM Coupons
        WHERE id = :id''', id=id)

        return [Coupon(*row) for row in rows]

    @staticmethod
    def get_discount(id):
        discount = app.db.execute('''
        SELECT discount
        FROM Coupons
        WHERE id = :id''', id=id)[0][0]

        return discount

    
    @staticmethod
    def has_used(uid, id):
        rows = app.db.execute('''
        SELECT users
        FROM Coupons
        WHERE id = :id''', id=id)
        users_used = rows[0][0].split(',') if rows else []
        
        return str(uid) in users_used
    

    @staticmethod
    def add_user(id, uid):
        users = app.db.execute('''
        SELECT users
        FROM Coupons
        WHERE id = :id''', id=id)

        if users:
            new_users = users[0][0] + "," + str(uid)

            app.db.execute('''
            UPDATE Coupons
            SET users = :new_users
            WHERE id = :id''', id=id, new_users=new_users)