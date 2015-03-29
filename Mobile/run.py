#!flask/bin/python
from app import app
from app.models import *
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin, BaseView, expose

class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

admin = Admin(app)
admin.add_view(ModelView(Customer, db.session))
admin.add_view(ModelView(Cooperative, db.session))
admin.add_view(ModelView(Transaction, db.session))
admin.add_view(ModelView(Loans, db.session))
app.run(debug=True,host='0.0.0.0')
