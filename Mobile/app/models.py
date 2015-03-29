from app import db

class Customer(db.Model):
    __tablename__ = 'Customer'
    sno = db.Column(db.Integer, primary_key = True, autoincrement=True)
    chineseID = db.Column(db.String(18),unique=True)
    cid = db.Column(db.String(20))
    pin = db.Column(db.String(6))
    phoneNumber = db.Column(db.String(11))
    location = db.Column(db.String(100))
    maxThreshold = db.Column(db.Integer)
    voiceURL = db.Column(db.String(1000))

    def accountAmount(self):
        amount = 0
        try:
            tran = Transaction.query.filter_by(
                customer_id=self.chineseID).all()
            for i in tran :
                amount = amount + i.amount
            return amount
        except Exception as e :
            print e
            return 0

class Cooperative(db.Model):
    __tablename__ = 'Cooperative'    
    sno = db.Column(db.Integer, primary_key = True, autoincrement=True)
    cid = db.Column(db.String(20),unique=True)
    amount = db.Column(db.Integer)

class Transaction(db.Model):
    __tablename__ = 'transaction'    
    sno = db.Column(db.Integer, primary_key = True, autoincrement=True)
    type_of_trans = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    customer_id = db.Column(db.String(18)) #references chinese ID 
    date = db.Column(db.Date)

class Loans(db.Model):
    __tablename__ = "loans"
    sno = db.Column(db.Integer, primary_key = True, autoincrement=True)
    approval = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    customer_id = db.Column(db.String(18)) #references Chinese ID 
    date = db.Column(db.Date)


