from modulefinder import STORE_NAME
from multiprocessing import synchronize
from turtle import position
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy import exc
import psycopg2

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<user>:<password>@localhost/<appname>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456Yyt@localhost/csce310-app'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)
    
class Store(db.Model): 
 Store_ID = db.Column(db.Integer, primary_key=True)
 Store_Name = db.Column(db.String(128))
 Location = db.Column(db.String(128))
 Order_Relation = db.relationship('Orders', backref='store', lazy=True)
 
class Employee(db.Model):
 Employee_ID = db.Column(db.Integer, primary_key=True)
 Employee_Fname = db.Column(db.String(64))
 Employee_Lname = db.Column(db.String(64))
 Employee_Email = db.Column(db.String(128))
 Employee_Phone = db.Column(db.String(128))
 Position = db.Column(db.String(128))
 Hours_Worked = db.Column(db.Integer)
 Salary = db.Column(db.Float)
 
class Manufacturer(db.Model):
 Manufacturer_ID = db.Column(db.Integer, primary_key=True)
 Manufacturer_Name = db.Column(db.String(128))
 Manufacturer_Email = db.Column(db.String(128))
 Manufacturer_Phone = db.Column(db.String(128))
 Manufacturer_Headquarters = db.Column(db.String(128))
 Manufacturer_Description = db.Column(db.String(128))
 Product_Relation = db.relationship('Product', backref='manufacturer', lazy=True)
 
class Product(db.Model):
 Product_ID = db.Column(db.Integer, primary_key=True)
 Manufacturer_ID = db.Column(db.Integer, db.ForeignKey('manufacturer.Manufacturer_ID')) #foreign ref
 Product_Price = db.Column(db.Float)
 Product_Quantity = db.Column(db.Integer)
 Product_Size = db.Column(db.Integer)
 Product_Type = db.Column(db.String(128))
 Product_Description = db.Column(db.String(128))
 Orders_Relation = db.relationship('Orders', backref='product', lazy=True)
 
class Orders(db.Model):
 Order_ID = db.Column(db.Integer, primary_key=True)
 Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID')) #foreign ref
 Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID')) #foreign ref
 Order_Quantity = db.Column(db.Integer)
 Order_Price = db.Column(db.Float)
 Order_Date = db.Column(db.DateTime)
 Received = db.Column(db.Boolean, default=False, nullable=False)
 
class Staff(db.Model):
 Staff_ID = db.Column(db.Integer, primary_key=True)
 Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID'))
 Employee_ID = db.Column(db.Integer, db.ForeignKey('employee.Employee_ID'))
 Employee_Relation = db.relationship('Employee', backref='staff', lazy=True)

if __name__ == '__main__':
    app.run()

def getManf():
    query = select(Manufacturer)
    result = db.session.execute(query)
    
    manf_list = []
    for manf in result.scalars():
        manf_list.append((manf.Manufacturer_Name, manf.Manufacturer_Email,
                          manf.Manufacturer_Phone, manf.Manufacturer_Headquarters, manf.Manufacturer_Description))
    return manf_list;


@app.route('/')
def home():
    return render_template('home.html')

##### CREATE

@app.route("/createmanf")
def createmanf(feedback_message=None, feedback_type=False):
    return render_template("createManf.html", feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route("/manfcreate", methods=['POST'])
def manfcreate():
    id = request.form["manf_id"]
    name = request.form["manf_name"]
    email = request.form["manf_email"]
    phone = request.form["manf_phone"]
    headquarters = request.form["manf_headquarters"]
    desc = request.form["manf_description"]
    
    try:
        entry = Manufacturer(Manufacturer_ID = id, Manufacturer_Name = name,
                             Manufacturer_Email = email, Manufacturer_Phone = phone,
                             Manufacturer_Headquarters = headquarters, 
                             Manufacturer_Description = desc)
        db.session.add(entry)
        db.session.commit()


    except exc.IntegrityError as err:
        db.session.rollback()
        return createmanf(feedback_message='A Manufacturer named {} already exists. Create a Manufacturer with a different name.'.format(name), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createmanf(feedback_message='Database error: {}'.format(err), feedback_type=False)
    
    return createmanf(feedback_message='Successfully added Manufacturer {}'.format(name), ##### might need to change name
                       feedback_type=True)
    
def get_manf(manfName):
    query = select(Manufacturer).where(Manufacturer.Manufacturer_Name == manfName)
    result = db.session.execute(query)
    manf = result.scalar()
    if manf is None:
        raise('Manufacturer not found')
    return manf

## maby add get_manf_from_id function


##### READ
@app.route("/readmanf")
def readmanf():
    query = select(Manufacturer)
    result = db.session.execute(query)
    
    manf_list = []
    for manf in result.scalars(): ####may need to not capitalize here
        manf_list.append((manf.Manufacturer_ID, manf.Manufacturer_Name, manf.Manufacturer_Headquarters,
                          manf.Manufacturer_Email, manf.Manufacturer_Phone,  manf.Manufacturer_Description))
        
    return render_template("readManf.html", manflist=manf_list)
    

##### UPDATE
@app.route("/updatemanf") #####may needto fix this part
def updatemanf(feedback_message=None, feedback_type=False):
    manf_names = [name for name, _, _, _, _ in getManf()]
    return render_template("updateManf.html",
                           manfnames = manf_names,
                           feedback_message=feedback_message,
                           feedback_type=feedback_type)

@app.route("/manfupdate", methods=['POST'])
def manfupdate():
    manf_name = request.form.get('manfnames')
    
    name = request.form["name"]
    hq = request.form["hq"]
    email = request.form["email"]
    phone= request.form["phone"]
    desc = request.form["desc"]
    
    try:
        obj = db.session.query(Manufacturer).filter(
            Manufacturer.Manufacturer_Name == manf_name).first()
        
        if obj == None:
            msg = 'Manufacturer {} not found.'.format(manf_name)
            return updatemanf(feedback_message=msg, feedback_type=False)
        
        ##may need to capitalize here
        if name != '':
            obj.Manufacturer_Name = name
        if hq != '':
            obj.Manufacturer_Headquarters = hq
        if email != '':
            obj.Manufacturer_Email = email
        if phone != '':
            obj.Manufacturer_Phone = phone
        if desc != '':
            obj.Manufacturer_Description = desc
            
        db.session.commit()
        
    except Exception as err:
        db.session.rollback()
        return updatemanf(feedback_message=err, feedback_type=False)

    return updatemanf(feedback_message='Successfully updated chef {}'.format(manf_name),
                       feedback_type=True)
        
##### DELETE
@app.route("/deletemanf")
def deletemanf(feedback_message=None, feedback_type=False):
    manf_names = [name for name, _, _, _, _ in getManf()]
    return render_template("deleteManf.html", manfnames = manf_names,
                           feedback_type=feedback_message)

@app.route("/manfdelete", methods=['POST'])
def manfdelete():
    if not request.form.get('confirmInput'):
        return deletemanf(feedback_message='Operation canceled. Manufacturer not deleted', feedback_type=False)
    
    manf_name = request.form.get('manfnames')
    
    try:
        obj = db.session.query(Manufacturer).filter(
            Manufacturer.Manufacturer_Name == manf_name).filter().first()
        
        if obj == None:
            msg = 'Manufacturer {} not found.'.format(manf_name)
            return deletemanf(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deletemanf(feedback_message=err, feedback_type=False)
    
    return deletemanf(feedback_message='Successfully deleted Manufacturer {}'.format(manf_name),
                      feedback_type=True)
    
    
    