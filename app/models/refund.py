from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, SelectField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

class RefundRequestForm(FlaskForm):
    oid = IntegerField('')
    sid = IntegerField('')
    reason = StringField('Reason for Refund', validators=[DataRequired()])
    value = DecimalField('')
    request = SubmitField('Request a Refund')

class Refund:
    
    def __init__(self, id, oid, uid, sid, reason, value, status):
        self.id = id
        self.oid = oid
        self.uid = uid
        self.sid = sid
        self.reason = reason
        self.value = value
        self.status = status

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Refunds
WHERE id = :id
''',
                              id=id)
        return Refund(*(rows[0])) if rows else None  

    @staticmethod
    def get_by_sid(sid):
        rows = app.db.execute("""
            SELECT *
            FROM Refunds
            WHERE sid = :sid
            """,
            sid=sid)
        return [Refund(*row) for row in rows]

    @staticmethod
    def get_by_uid(uid):
        rows = app.db.execute("""
            SELECT *
            FROM Refunds
            WHERE uid = :uid
            """,
            uid=uid)
        return [Refund(*row) for row in rows]

    def check_by_oid(oid):
        rows = app.db.execute("""
            SELECT *
            FROM Refunds
            WHERE oid = :oid
            """,
            oid=oid)
        if len(rows) > 0:
            return [Refund(*row) for row in rows][0]
        return None

    @staticmethod
    def new_refund_request(oid, uid, sid, reason, value): # ask if when modify table does csv need to be modify as well
        rows = app.db.execute("""
            INSERT INTO Refunds(id, oid, uid, sid, reason, value, status)
            VALUES(:id, :oid, :uid, :sid, :reason, :value, :status)
            RETURNING id
            """,
            id= app.db.execute("""
            SELECT MAX(id)
            FROM Refunds
            """)[0][0] + 1,
            oid=oid, uid=uid, sid=sid, reason=reason, value=value,
            status=False
            )
        id = rows[0][0]
        return Refund.get(id)

    @staticmethod
    def accept_request(id, uid, value, sid):
        rows = app.db.execute("""
                UPDATE Refunds
                SET status = :status
                WHERE id = :id 
            """, status=True, id=id)
        rows = app.db.execute("""
                UPDATE Users
                SET balance = balance + :value
                WHERE id = :id 
            """, value=value, id=uid)
        rows = app.db.execute("""
                UPDATE Users
                SET balance = balance - :value
                WHERE id = :id 
            """, value=value, id=sid)
    