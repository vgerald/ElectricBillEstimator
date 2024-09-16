import os
from pprint import pprint
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import datetime

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))
print("basedir", basedir)

# Setup Flask app
app = Flask(__name__)
print("flask app", app)

# Setup database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'reading.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("flask app with DB config", app.config)
db = SQLAlchemy(app)
app.app_context().push()

db.Model.metadata.reflect(bind=db.engine)

db.Model.metadata.tables['bill']

print("db details", db.session, db.Model.metadata.tables['bill'], db.Model)


# Setup database classes
class CustomerReading(db.Model):
    __table__ = db.Model.metadata.tables['customerreading']


class Bill(db.Model):
    __table__ = db.Model.metadata.tables['bill']



@app.route("/bills/")
def bills():
    print("Inside the bills method ******")
    bills = Bill.query.all()
    print(bills)
    print("After the db query and before rendering the html template. *****************")
    return render_template('bills.html', bills=bills)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/bills/<int:bill_id>/')
def bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return render_template('bill.html', bill=bill)


@app.route('/bills/addBill/', methods=('GET', 'POST'))
def addBill():
    if request.method == 'POST':
        id = int(request.form['id'])
        pprint(request.form)
        bill_date = datetime.datetime.strptime(request.form['bill_date'], '%Y-%m-%d')
        bill_reading = int(request.form['bill_reading'])
        meter_date = datetime.datetime.strptime(request.form['meter_date'], '%Y-%m-%d')
        meter_reading = int(request.form['meter_reading'])
        # estimated_reading = int(request.form['estimated_reading'])
        # estimated_bill = float(request.form['estimated_bill'])

        bill = Bill()
        bill.id = id
        bill.bill_date = bill_date
        bill.bill_reading = bill_reading
        bill.meter_date = meter_date
        bill.meter_reading = meter_reading
        # bill.estimated_reading = estimated_reading
        # bill.estimated_bill = estimated_bill

        db.session.add(bill)
        db.session.commit()

        return redirect(url_for('bills'))

    max_id = db.session.query(func.max(Bill.id)).scalar()
    next_id = max_id + 1

    return render_template('addBill.html', next_id=next_id)


@app.route('/bills/<int:bill_id>/edit/', methods=('GET', 'POST'))
def edit(bill_id):
    bill = Bill.query.get_or_404(bill_id)

    if request.method == 'POST':
        id = int(request.form['id'])
        pprint(request.form)
        bill_date = datetime.datetime.strptime(request.form['bill_date'], '%Y-%m-%d')
        bill_reading = int(request.form['bill_reading'])
        meter_date = datetime.datetime.strptime(request.form['meter_date'], '%Y-%m-%d')
        meter_reading = int(request.form['meter_reading'])
        estimated_reading = int(request.form['estimated_reading'])
        estimated_bill = float(request.form['estimated_bill'])

        bill.id = id
        bill.bill_date = bill_date
        bill.bill_reading = bill_reading
        bill.meter_date = meter_date
        bill.meter_reading = meter_reading
        bill.estimated_reading = estimated_reading
        bill.estimated_bill = estimated_bill

        db.session.add(bill)
        db.session.commit()

        return redirect(url_for('bills'))

    return render_template('edit.html', bill=bill)


@app.route('/bills/<int:bill_id>/delete/')
def delete(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    db.session.delete(bill)
    db.session.commit()
    return redirect(url_for('bills'))

#
#  https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application


#  flask --debug run --host=0.0.0.0
