from itertools import product
from modulefinder import STORE_NAME
from multiprocessing import synchronize
from turtle import position
from flask import Flask, render_template, request, flash, redirect, url_for
from flask import Flask, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy import exc
import psycopg2
from functools import wraps

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<user>:<password>@localhost/<appname>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/DeTail'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Integer, nullable=True)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min = 4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min = 4, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Login")


class Store(db.Model):  
    Store_ID = db.Column(db.Integer, primary_key=True)
    Store_Name = db.Column(db.String(128))
    Location = db.Column(db.String(128))
    Order_Relation = db.relationship('Orders', backref='store', lazy=True,passive_deletes = True)

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
    Product_Relation = db.relationship('Product', backref='manufacturer', lazy=True,passive_deletes = True)


class Product(db.Model):
    Product_ID = db.Column(db.Integer, primary_key=True)
    Manufacturer_ID = db.Column(db.Integer, db.ForeignKey('manufacturer.Manufacturer_ID', ondelete = 'CASCADE')) #foreign ref
    Product_Price = db.Column(db.Float)
    Product_Quantity = db.Column(db.Integer)
    Product_Size = db.Column(db.Integer)
    Product_Type = db.Column(db.String(128))
    Product_Description = db.Column(db.String(128))
    Orders_Relation = db.relationship('Orders', backref='product', lazy=True,passive_deletes = True)
    
class Orders(db.Model):
    Order_ID = db.Column(db.Integer, primary_key=True)
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID',ondelete = 'CASCADE')) #foreign ref
    Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID',ondelete = 'CASCADE')) #foreign ref
    Order_Quantity = db.Column(db.Integer)
    Order_Price = db.Column(db.Float)
    Order_Date = db.Column(db.DateTime)
    Received = db.Column(db.Boolean, default=False, nullable=False)

class Staff(db.Model):
    Staff_ID = db.Column(db.Integer, primary_key=True)
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID',ondelete = 'CASCADE'))
    Employee_ID = db.Column(db.Integer, db.ForeignKey('employee.Employee_ID',ondelete = 'CASCADE'))
    Employee_Relation = db.relationship('Employee', backref='staff', lazy=True,passive_deletes = True)
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
    return manf_list

def getemployees():
    query = select(Employee)
    result = db.session.execute(query)
    emp_list = []
    for e in result.scalars():
        emp_list.append((e.Employee_ID, e.Employee_Fname, e.Employee_Lname, e.Employee_Email, e.Employee_Phone, e.Position, e.Hours_Worked, e.Salary))
    return emp_list

def getstaff(): #DONE BY ELVIS
    query = select(Staff)
    result = db.session.execute(query)
    staff_list = []
    for staff in result.scalars():
        staff_list.append((staff.Staff_ID, staff.Store_ID, staff.Employee_ID))
    return staff_list

def getstore(): #DONE BY ELVIS
    query = select(Store)
    result = db.session.execute(query)
    store_list = []
    for store in result.scalars():
        store_list.append((store.Store_ID, store.Store_Name, store.Location))
    return store_list
    
def get_manf(manfName):
    query = select(Manufacturer).where(Manufacturer.Manufacturer_Name == manfName)
    result = db.session.execute(query)
    manf = result.scalar()
    if manf is None:
        raise('Manufacturer not found')
    return manf

def getproducts():
    query = select(Product)
    result = db.session.execute(query)

    product_list = []
    for product in result.scalars():
        product_list.append((product.Product_ID, product.Manufacturer_ID, product.Product_Price, product.Product_Quantity, product.Product_Size, product.Product_Type, product.Product_Description))
    return product_list

def getorders():
    query = select(Orders)
    result = db.session.execute(query)

    order_list = []
    for order in result.scalars():
        order_list.append((order.Order_ID, order.Store_ID, order.Product_ID, order.Order_Quantity, order.Order_Price, order.Order_Date, order.Received))
    return order_list

def isValidPhoneNumber(phoneNumber):
    valid_ints = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if len(phoneNumber) == 12:
        for i in range(12):
            if i == 3 or i == 7:
                if phoneNumber[i] != '-':
                    return False
            else:
                if phoneNumber[i] not in valid_ints:
                    return False
    else:
        return False
    return True
    
def isValidEmail(email):
    num_ats = 0
    for i in range (len(email)):
        if email[i] == '@':
            num_ats = num_ats + 1
    if num_ats != 1:
        return False
    else:
        return True   

#CREATE

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
        if id == '' or name == '' or email == '' or phone == '' or headquarters == '' or desc == '':
            return createmanf(feedback_message='You cannot have any empty attributes. Please try again.', feedback_type=False)
        if(isValidPhoneNumber(phone) == False):
            return createmanf(feedback_message='The phone number you entered was not in the correct format. Please try again.', feedback_type=False)
        if(isValidEmail(email) == False):
            return createmanf(feedback_message='The email you entered was not in the correct format. Please try again.', feedback_type=False)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createmanf(feedback_message='The manufacturer you entered had either a duplicate name, email, or phone number. Please try again', feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createmanf(feedback_message='One or more of the attributes entered was of an invalid data type. Please try again.', feedback_type=False)
    
    return createmanf(feedback_message='Successfully added Manufacturer {}'.format(name), ##### might need to change name
                       feedback_type=True)

@app.route("/createemployee")
def createemployee(feedback_message=None, feedback_type=False):
    return render_template("createemployee.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)

@app.route("/employeecreate", methods=['POST'])
def employeecreate():
    Employee_ID = request.form["Employee_ID"]
    Employee_Fname = request.form["Employee_Fname"]
    Employee_Lname = request.form["Employee_Lname"]
    Employee_Email = request.form["Employee_Email"]
    Employee_Phone = request.form["Employee_Phone"]
    Position = request.form["Position"]
    Hours_Worked = request.form["Hours_Worked"]
    Salary = request.form["Salary"]
    try:
        entry = Employee(Employee_ID=Employee_ID, Employee_Fname=Employee_Fname, Employee_Lname=Employee_Lname, 
            Employee_Email=Employee_Email, Employee_Phone=Employee_Phone, Position=Position, 
            Hours_Worked=Hours_Worked, Salary=Salary)
        db.session.add(entry)
        if Employee_ID == '' or Employee_Fname == '' or Employee_Lname == '' or Employee_Email == '' or Employee_Phone == '' or Position == '' or Hours_Worked == '' or Position == '':
            return createemployee(feedback_message='You cannot have any empty attributes. Please try again.', feedback_type=False)
        if isValidPhoneNumber(Employee_Phone) == False:
            return createemployee(feedback_message='The phone number you entered was not in the correct format. Please try again.', feedback_type=False)
        if isValidEmail(Employee_Email) == False:
            return createemployee(feedback_message='The email you entered was not in the correct format. Please try again.', feedback_type=False)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createemployee(feedback_message='The employee you entered had a duplicate ID, email, or phone number. Please try again.', feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createemployee(feedback_message='One or more of the attributes entered was of an invalid data type. Please try again.', feedback_type=False)
    return createemployee(feedback_message='Successfully added employee {} {} '.format(Employee_Fname, Employee_Lname),
                       feedback_type=True)

@app.route("/createstore") 
def createstore(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    return render_template("createstore.html", feedback_message=feedback_message, feedback_type=feedback_type)

@app.route("/storecreate", methods=['POST'])
def storecreate(): #DONE BY ELVIS
    Store_ID = request.form.get("Store_ID"); Store_Name = request.form.get("Store_Name"); Location = request.form.get("Location")
    try:
        entry = Store(Store_ID=Store_ID, Store_Name=Store_Name, Location=Location)
        if Store_ID == '' or Store_Name == '' or Location == '':
            return createstore(feedback_message='You cannot have any empty attributes. Please try again.', feedback_type=False)
        db.session.add(entry); db.session.commit()
    except exc.IntegrityError as ERROR:
        db.session.rollback()
        return createstore(feedback_message='A store with ID ' + Store_ID + "already exists. Please try again.", feedback_type=False)
    except Exception as ERROR:
        db.session.rollback()
        return createstore(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return createstore(feedback_message='Store ' + Store_ID + ' created successfully.', feedback_type=True)
        #create staff and staff create

@app.route("/createstaff")
def createstaff(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    return render_template("createstaff.html", feedback_message=feedback_message, feedback_type=feedback_type)

@app.route("/staffcreate", methods=['POST'])
def staffcreate(): #DONE BY ELVIS
    Staff_ID = request.form.get("Staff_ID"); Store_ID = request.form.get("Store_ID"); Employee_ID = request.form.get("Employee_ID")
    try:
        entry = Staff(Staff_ID=Staff_ID, Store_ID=Store_ID, Employee_ID=Employee_ID)
        if Staff_ID == '' or Store_ID == '' or Employee_ID == '':
            return createstaff(feedback_message='You cannot have any empty attributes. Please try again.', feedback_type=False)
        db.session.add(entry); db.session.commit()
    except exc.IntegrityError as ERROR:
        db.session.rollback()
        return createstaff(feedback_message='Staff ID must be unique, store ID must exist, and employee ID must exist. One or more of the three conditions was violated. Please try again.', feedback_type=False)
    except Exception as ERROR:
        db.session.rollback()
        return createstaff(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return createstaff(feedback_message='Staff ' + Staff_ID + ' created successfully.', feedback_type=True)


@app.route("/createproduct")
def createproduct(feedback_message=None, feedback_type=False):
    return render_template("createproduct.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)

@app.route("/productcreate", methods=['POST'])
def productcreate():
    Product_ID = request.form["Product_ID"]
    Manufacturer_ID = request.form["Manufacturer_ID"]
    Product_Price = request.form["Product_Price"]
    Product_Quantity = request.form["Product_Quantity"]
    Product_Size = request.form["Product_Size"]
    Product_Type = request.form["Product_Type"]
    Product_Description = request.form["Product_Description"]

    try:
        entry = Product(Product_ID = Product_ID, Manufacturer_ID = Manufacturer_ID, Product_Price=Product_Price, Product_Quantity=Product_Quantity, Product_Size=Product_Size, Product_Type=Product_Type, Product_Description=Product_Description)
        db.session.add(entry)
        if Product_ID == '' or Manufacturer_ID == '' or Product_Price == '' or Product_Quantity == '' or Product_Size == '' or Product_Type == '' or Product_Description == '':
            return createproduct(feedback_message='You cannot have any empty attributes. Please try again.', feedback_type=False)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createproduct(feedback_message='Product ID must be unique and manufacturer ID must exist. One or more of the two conditions were violated. Please try again.'.format(Product_ID), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createproduct(feedback_message='One or more attributes entered contained an invalid data type. Please try again.', feedback_type=False)
            

    return createproduct(feedback_message='Successfully added product {}'.format(Product_ID),
                       feedback_type=True)

@app.route("/createorder")
def createorder(feedback_message=None, feedback_type=False):
    return render_template("createorder.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)

@app.route("/ordercreate", methods=['POST'])
def ordercreate():
    Order_ID = request.form["Order_ID"]
    Store_ID = request.form["Store_ID"]
    Product_ID = request.form["Product_ID"]
    Order_Quantity = request.form["Order_Quanity"]
    Order_Price = request.form["Order_Price"]
    Order_Date = request.form["Order_Date"]
    Received = request.form["Received"]

    try:
        entry = Orders(Order_ID=Order_ID, Store_ID=Store_ID, Product_ID=Product_ID, Order_Quantity=Order_Quantity, Order_Price=Order_Price, Order_Date=Order_Date, Received= Received.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
        db.session.add(entry)
        if Order_ID == '' or Store_ID == '' or Product_ID == '' or Order_Quantity == '' or Order_Price == '' or Order_Date == '' or Received == '':
            return createorder(feedback_message='You cannot have any empty attributes. Please try again.', feedback_type=False)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createorder(feedback_message='Order ID must be unique, store ID must exist, and product ID must exist. One or more of the three conditions were violated. Please try again.'.format(Order_ID), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createorder(feedback_message='Database error: {}'.format(err), feedback_type=False)
            

    return createorder(feedback_message='Successfully added order {}'.format(Order_ID),
                       feedback_type=True)

#READ

@app.route("/reademployee")
def reademployee():
    query = select(Employee)
    result = db.session.execute(query)

    emp_list = []
    for e in result.scalars():
        emp_list.append((e.Employee_ID, e.Employee_Fname, e.Employee_Lname, e.Employee_Email, e.Employee_Phone, e.Position, e.Hours_Worked, e.Salary))
    return render_template("reademployee.html", empList=emp_list)

@app.route("/readstaff")
def readstaff(): #DONE BY ELVIS
    query = select(Staff)
    result = db.session.execute(query)
    staff_list = []
    for staff in result.scalars():
        staff_list.append((staff.Staff_ID, staff.Store_ID, staff.Employee_ID))
    return render_template("readstaff.html", staff_list=staff_list)

@app.route("/readstore")
def readstore(): #DONE BY ELVIS
    query = select(Store)
    result = db.session.execute(query)
    store_list = []
    for store in result.scalars():
        store_list.append((store.Store_ID, store.Store_Name, store.Location))
    return render_template("readstore.html", store_list=store_list)

@app.route("/readproduct")
def readproduct():
    query = select(Product)
    result = db.session.execute(query)

    product_list = []
    for product in result.scalars():
        product_list.append((product.Product_ID, product.Manufacturer_ID, product.Product_Price, product.Product_Quantity, product.Product_Size, product.Product_Type, product.Product_Description))
    
    return render_template("readproduct.html", productlist=product_list)

@app.route("/readorder")
def readorder():
    query = select(Orders)
    result = db.session.execute(query)

    order_list = []
    for order in result.scalars():
        order_list.append((order.Order_ID, order.Store_ID, order.Product_ID, order.Order_Quantity, order.Order_Price, order.Order_Date, order.Received))
    
    return render_template("readorder.html", orderlist=order_list)

@app.route("/readmanf")
def readmanf():
    query = select(Manufacturer)
    result = db.session.execute(query)
    
    manf_list = []
    for manf in result.scalars(): ####may need to not capitalize here
        manf_list.append((manf.Manufacturer_ID, manf.Manufacturer_Name, manf.Manufacturer_Headquarters,
                          manf.Manufacturer_Email, manf.Manufacturer_Phone,  manf.Manufacturer_Description))
        
    return render_template("readManf.html", manflist=manf_list)

#Update product
@app.route("/updateproduct")
def updateproduct(feedback_message=None, feedback_type=False):
    product_names = [name for name, _, _, _, _, _, _ in getproducts()]
    return render_template("updateproduct.html", 
                           productnames=product_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/productupdate", methods=['POST'])
def productupdate():
    product_name = request.form.get('productnames')
    Product_ID = request.form["Product_ID"]
    Manufacturer_ID = request.form["Manufacturer_ID"]
    Product_Price = request.form["Product_Price"]
    Product_Quantity = request.form["Product_Quantity"]
    Product_Size = request.form["Product_Size"]
    Product_Type = request.form["Product_Type"]
    Product_Description = request.form["Product_Description"]

    try:
        obj = db.session.query(Product).filter(
            Product.Product_ID==product_name).first()
        
        if obj == None:
            msg = 'Product {} not found.'.format(Product_ID)
            return updateproduct(feedback_message=msg, feedback_type=False)

        if Product_ID != '':
            obj.Product_ID = Product_ID
        if Manufacturer_ID != '':
            obj.Manufacturer_ID = Manufacturer_ID
        if Product_Price != '':
            obj.Product_Price = Product_Price
        if Product_Quantity != '':
            obj.Product_Quantity = Product_Quantity
        if Product_Size != '':
            obj.Product_Size = Product_Size
        if Product_Type != '':
            obj.Product_Type = Product_Type
        if Product_Description != '':
            obj.Product_Description = Product_Description
        
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return updateproduct(feedback_message=err, feedback_type=False)

    return updateproduct(feedback_message='Successfully updated product {}'.format(Product_ID),
                       feedback_type=True)

@app.route("/updateproductid/<int:id>", methods=['GET','POST'])
def updateproductid(id):
    try:
        obj = db.session.query(Product).filter(
            Product.Product_ID == id).first()
        
        Product_ID = request.form["Product_ID"]
        Manufacturer_ID = request.form["Manufacturer_ID"]
        Product_Price = request.form["Product_Price"]
        Product_Quantity = request.form["Product_Quantity"]
        Product_Size = request.form["Product_Size"]
        Product_Type = request.form["Product_Type"]
        Product_Description = request.form["Product_Description"]


        if obj == None:
            msg = 'product {} not found.'.format(id)
            return render_template("updateproductid.html", product = obj, feedback_message=msg, feedback_type=False)
        if Product_ID != '':
            obj.Product_ID = Product_ID
        if Manufacturer_ID != '':
            obj.Manufacturer_ID = Manufacturer_ID
        if Product_Price != '':
            obj.Product_Price = Product_Price
        if Product_Quantity != '':
            obj.Product_Quantity = Product_Quantity
        if Product_Size != '':
            obj.Product_Size = Product_Size
        if Product_Type != '':
            obj.Product_Type = Product_Type
        if Product_Description != '':
            obj.Product_Description = Product_Description
            
        db.session.commit()
        return redirect('/readproduct')

    except Exception as err:
        db.session.rollback()
        return render_template("updateproductid.html", product = obj, feedback_message=err, feedback_type=False)
    
@app.route("/updateorder")
def updateorder(feedback_message=None, feedback_type=False):
    order_names = [name for name, _, _, _, _, _, _ in getorders()]
    return render_template("updateorder.html", 
                           ordernames=order_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/orderupdate", methods=['POST'])
def orderupdate():
    order_name = request.form.get('ordernames')
    Order_ID = request.form["Order_ID"]
    Store_ID = request.form["Store_ID"]
    Product_ID = request.form["Product_ID"]
    Order_Quantity = request.form["Order_Quanity"]
    Order_Price = request.form["Order_Price"]
    Order_Date = request.form["Order_Date"]
    Received = request.form["Received"]

    try:
        obj = db.session.query(Orders).filter(
            Orders.Order_ID==order_name).first()
        
        if obj == None:
            msg = 'Order {} not found.'.format(Order_ID)
            return updateorder(feedback_message=msg, feedback_type=False)

        if Order_ID != '':
            obj.Order_ID = Order_ID
        if Store_ID != '':
            obj.Store_ID = Store_ID
        if Product_ID != '':
            obj.Product_ID = Product_ID
        if Order_Quantity != '':
            obj.Order_Quantity = Order_Quantity
        if Order_Price != '':
            obj.Order_Price = Order_Price
        if Order_Date != '':
            obj.Order_Date = Order_Date
        if Received != '':
            obj.Received = Received.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
        
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return updateorder(feedback_message=err, feedback_type=False)

    return updateorder(feedback_message='Successfully updated order {}'.format(Order_ID),
                       feedback_type=True)

@app.route("/updateorderid/<int:id>", methods=['GET','POST'])
def updateorderid(id):
    try:
        obj = db.session.query(Orders).filter(
            Orders.Order_ID == id).first()

        Order_ID = request.form["Order_ID"]
        Store_ID = request.form["Store_ID"]
        Product_ID = request.form["Product_ID"]
        Order_Quantity = request.form["Order_Quanity"]
        Order_Price = request.form["Order_Price"]
        Order_Date = request.form["Order_Date"]
        Received = request.form["Received"]

        if obj == None:
            msg = 'Order {} not found.'.format(Order_ID)
            return render_template("updateorderid.html", order = obj,feedback_message=msg, feedback_type=False)
        if Order_ID != '':
            obj.Order_ID = Order_ID
        if Store_ID != '':
            obj.Store_ID = Store_ID
        if Product_ID != '':
            obj.Product_ID = Product_ID
        if Order_Quantity != '':
            obj.Order_Quantity = Order_Quantity
        if Order_Price != '':
            obj.Order_Price = Order_Price
        if Order_Date != '':
            obj.Order_Date = Order_Date
        if Received != '':
            obj.Received = Received.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

        db.session.commit()
        return redirect('/readorder')
    except Exception as err:
        db.session.rollback()
        return render_template("updateorderid.html", order = obj,feedback_message=err, feedback_type=False)

@app.route("/updateemployee")
def updateemployee(feedback_message=None, feedback_type=False):
    employee_emails = [name for _, _, _, name, _, _, _, _ in getemployees()]
    return render_template("updateemployee.html", 
                           employeeEmails = employee_emails, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/employeeupdate", methods=['POST'])
def employeeupdate():
    e_email = request.form.get('employeeEmails')
    Employee_Fname = request.form["Employee_Fname"]
    Employee_Lname = request.form["Employee_Lname"]
    Employee_Email = request.form["Employee_Email"]
    Employee_Phone = request.form["Employee_Phone"]
    Position = request.form["Position"]
    Hours_Worked = request.form["Hours_Worked"]
    Salary = request.form["Salary"]

    try:
        obj = db.session.query(Employee).filter(
            Employee.Employee_Email==e_email).first()
        if obj == None:
            msg = 'Employee with email {} not found.'.format(e_email)
            return updateemployee(feedback_message=msg, feedback_type=False)

        if Employee_Email in [name for _, _, _, name, _, _, _, _ in getemployees()]:
            msg = 'The email you entered already exists for another employee. Please try again'
            return updateemployee(feedback_message=msg, feedback_type=False)
        if Employee_Phone in [name for _, _, _, _, name, _, _, _ in getemployees()]:
            msg = 'The phone number you entered already exists for another employee. Please try again'
            return updateemployee(feedback_message=msg, feedback_type=False)

        if Employee_Fname != '':
            obj.Employee_Fname = Employee_Fname
        if Employee_Lname != '':
            obj.Employee_Lname = Employee_Lname
        if Employee_Email != '':
            if isValidEmail(Employee_Email) == False:
                return updateemployee(feedback_message='The email you entered was not in the correct format. Please try again.', feedback_type=False)
            else:
                obj.Employee_Email = Employee_Email
        else:
            obj.Employee_Email = e_email
        if Employee_Phone != '':
            if isValidPhoneNumber(Employee_Phone) == False:
                return updateemployee(feedback_message='The phone number you entered was not in the correct format. Please try again.', feedback_type=False)
            else:
                obj.Employee_Phone = Employee_Phone
        if Position != '':
            obj.Position = Position
        if Hours_Worked != '':
            obj.Hours_Worked = Hours_Worked
        if Salary != '':
            obj.Salary = Salary
        
        db.session.commit()

    except Exception as ERROR:
        db.session.rollback()
        return updateemployee(feedback_message='One or more attributes of invalid data type was entered. Please try again.', feedback_type=False)

    return updateemployee(feedback_message='Successfully updated employee with email {}'.format(e_email),
                       feedback_type=True)

@app.route("/updateemployeeid/<int:id>",methods=['GET','POST'])
def updateemployeeid(id):

    try:
        obj = Employee.query.filter_by(Employee_ID=id).first()

        Employee_ID = request.form["Employee_ID"]
        Employee_Fname = request.form["Employee_Fname"]
        Employee_Lname = request.form["Employee_Lname"]
        Employee_Email = request.form["Employee_Email"]
        Employee_Phone = request.form["Employee_Phone"]
        Position = request.form["Position"]
        Hours_Worked = request.form["Hours_Worked"]
        Salary = request.form["Salary"]

        if obj == None:
            msg = 'Employee {} not found.'.format(id)
            return render_template('updateemployeeid.html', employee = obj, feedback_message=msg, feedback_type=False)
        if Employee_ID != '':
            obj.Employee_ID = Employee_ID
        else:
            obj.Employee_ID = id
        if Employee_Fname != '':
            obj.Employee_Fname = Employee_Fname
        if Employee_Lname != '':
            obj.Employee_Lname = Employee_Lname
        if Employee_Email != '':
            obj.Employee_Email = Employee_Email
        if Employee_Phone != '':
            obj.Employee_Phone = Employee_Phone
        if Position != '':
            obj.Position = Position
        if Hours_Worked != '':
            obj.Hours_Worked = Hours_Worked
        if Salary != '':
            obj.Salary = Salary

        db.session.commit()
        return redirect('/reademployee')
    except Exception as err:
        db.session.rollback()
        return render_template('updateemployeeid.html', employee = obj, feedback=err)


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

        if email in [name for _, _, name, _, _ in getManf()]:
            msg = 'The email you entered already exists for another manufacturer. Please try again'
            return updatemanf(feedback_message=msg, feedback_type=False)
        if phone in [name for _, _, _, name, _ in getManf()]:
            msg = 'The phone number you entered already exists for another manufacturer. Please try again'
            return updatemanf(feedback_message=msg, feedback_type=False)

        ##may need to capitalize here
        if name != '':
            obj.Manufacturer_Name = name
        if hq != '':
            obj.Manufacturer_Headquarters = hq
        if email != '':
            if isValidEmail(email) == False:
                return updatemanf(feedback_message='The email you entered was not in the correct format. Please try again.', feedback_type=False)
            else:
                obj.Manufacturer_Email = email
        if phone != '':
            if isValidEmail(phone) == False:
                return updatemanf(feedback_message='The phone number you entered was not in the correct format. Please try again.', feedback_type=False)
            else:
                obj.Manufacturer_Phone = phone
        if desc != '':
            obj.Manufacturer_Description = desc
            
        db.session.commit()
        
    except Exception as ERROR:
        db.session.rollback()
        return updatemanf(feedback_message='One or more attributes of invalid data type was entered. Please try again.', feedback_type=False)

    return updatemanf(feedback_message='Successfully updated manufacturer {}'.format(manf_name),
                       feedback_type=True)
                       
@app.route("/updatemanfid/<int:id>", methods=['GET','POST'])
def updatemanfid(id):
    try:
        obj = db.session.query(Manufacturer).filter(
            Manufacturer.Manufacturer_ID == id).first()
        
        mid = request.form["id"]
        name = request.form["name"]
        hq = request.form["hq"]
        email = request.form["email"]
        phone= request.form["phone"]
        desc = request.form["desc"]

        if obj == None:
            msg = 'Manufacturer {} not found.'.format(id)
            return updatemanf(feedback_message=msg, feedback_type=False)
        if mid != '':
            obj.Manufacturer_ID = mid
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
        return redirect('/readmanf')

    except Exception as err:
        db.session.rollback()
        return render_template("updatemanfid.html", manf = obj, feedback_message=err, feedback_type=False)
    
#UPDATE STAFF
@app.route("/updatestaff")
def updatestaff(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    staff_names = [name for name ,_, _ in getstaff()]
    #     order_names = [name for name, _, _, _, _, _, _ in getorders()]
    return render_template("updatestaff.html", 
    staffname=staff_names, 
    feedback_message=feedback_message, 
    feedback_type=feedback_type)


@app.route("/staffupdate", methods=['POST'])
def staffupdate(): #DONE BY ELVIS
    staff_name = request.form.get('staffnames')
    Staff_ID = request.form["Staff_ID"]; 
    Store_ID = request.form["Store_ID"]; 
    Employee_ID = request.form["Employee_ID"]
    try:
        obj = db.session.query(Staff).filter(
            Staff.Staff_ID==staff_name).first()
        
        if obj == None:
            return updatestaff(feedback_message='Staff ' + Staff_ID + ' does not exist. Please try again.', feedback_type=False)
        if Store_ID != '':
            obj.Store_ID = Store_ID
        if Employee_ID != '':
            obj.Employee_ID = Employee_ID
        if Staff_ID != '':
            obj.Staff_ID = Staff_ID
        db.session.commit()
    except Exception as ERROR:
        db.session.rollback()
        return updatestaff(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return updatestaff(feedback_message='Staff ' + Staff_ID + ' updated successfully.', feedback_type=True)

@app.route("/updatestaffid/<int:id>", methods=['GET','POST'])
def updatestaffid(id):
    try:
        obj = db.session.query(Staff).filter(
            Staff.Staff_ID == id).first()

        Staff_ID = request.form["Staff_ID"]; 
        Store_ID = request.form["Store_ID"]; 
        Employee_ID = request.form["Employee_ID"]

        if obj == None:
            return render_template("updatestaffid.html",feedback_message='Staff ' + Staff_ID + ' does not exist. Please try again.', feedback_type=False)
        if Store_ID != '':
            obj.Store_ID = Store_ID
        else:
            obj.Store_ID = id
        if Employee_ID != '':
            obj.Employee_ID = Employee_ID
        if Staff_ID != '':
            obj.Staff_ID = Staff_ID

        db.session.commit()
        return redirect('/readstaff')
    except Exception as err:
        db.session.rollback()
        return render_template("updatestaffid.html", staff = obj,feedback_message=err, feedback_type=False)

#UPDATE STORE
@app.route("/updatestore")
def updatestore(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    store_names = [name for name ,_, _ in getstore()]
    return render_template("updatestore.html", 
    storenames=store_names, 
    feedback_message=feedback_message, 
    feedback_type=feedback_type)

@app.route("/storeupdate", methods=['POST'])
def storeupdate(): #DONE BY ELVIS
    store_name = request.form.get('storenames')
    Store_ID = request.form["Store_ID"]
    Store_Name = request.form["Store_Name"]
    Location = request.form["Location"]
    try:
        obj = db.session.query(Store).filter(
            Store.Store_ID==store_name).first()
        if obj == None:
            msg = 'Store {} not found.'.format(store_name)
            return updatestaff(feedback_message=msg, feedback_type=False)
        if Store_ID != '':
            obj.Store_ID = Store_ID
        if Store_Name != '':
            obj.Store_Name = Store_Name
        if Location != '':
            obj.Location = Location
        db.session.commit()
    except Exception as ERROR:
        db.session.rollback()
        return updatestore(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return updatestore(feedback_message='Staff ' + Store_ID + ' updated successfully.', feedback_type=True)

@app.route("/updatestoreid/<int:id>", methods=['GET','POST'])
def updatestoreid(id):
    try:
        obj = db.session.query(Store).filter(
            Store.Store_ID == id).first()

    
        Store_ID = request.form["Store_ID"]
        Store_Name = request.form["Store_Name"]
        Location = request.form["Location"]

        if obj == None:
            msg = 'Store {} not found.'.format(id)
            return render_template("updatestoreid.html", feedback_message=msg, feedback_type=False)
        if Store_ID != '':
            obj.Store_ID = Store_ID
        if Store_Name != '':
            obj.Store_Name = Store_Name
        if Location != '':
            obj.Location = Location

        db.session.commit()
        return redirect('/readstore')
    except Exception as err:
        db.session.rollback()
        return render_template("updatestoreid.html", store = obj,feedback_message=None, feedback_type=False)
#
# DELETE
#

@app.route("/deletestaff")
def deletestaff(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    staff_names = [name for name ,_ , _ in getstaff()]
    return render_template("deletestaff.html", 
    staffnames=staff_names, 
    feedback_message=feedback_message, 
    feedback_type=feedback_type)
@app.route("/staffdelete", methods=['POST'])
def staffdelete():
    if not request.form.get('confirmInput'):
        return deletestaff(feedback_message='Please confirm deletion.', feedback_type=False)
    staff_name = request.form.get("staffnames")
    try:
        obj = db.session.query(Staff).filter(
            Staff.Staff_ID==staff_name).first()
        if obj == None:
            return deletestaff(feedback_message='Staff does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
    except Exception as ERROR:
        db.session.rollback()
        return deletestaff(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return deletestaff(feedback_message='Staff deleted successfully.', feedback_type=True)

@app.route("/deletestaffid/<int:id>", methods=['GET','POST']) #DONE BY ELVIS
def staffdeleteid(id):
    if not request.form.get('confirmInput'):
        return render_template("deletestaffid.html", feedback_message='Please confirm deletion.', feedback_type=False)
    try:
        obj = db.session.query(Staff).filter(
            Staff.Staff_ID==id).first()
        if obj == None:
            return render_template("deletestaffid.html", feedback_message='Staff does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
        return redirect('/readstaff')
    except Exception as ERROR:
        db.session.rollback()
        return render_template("deletestaffid.html", feedback_message='An error occurred. Please try again.', feedback_type=False)

@app.route("/deletestore")
def deletestore(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    store_names = [name for name ,_ , _ in getstore()]
    return render_template("deletestore.html", 
    storenames=store_names, 
    feedback_message=feedback_message, 
    feedback_type=feedback_type)
@app.route("/storedelete", methods=['POST']) #DONE BY ELVIS
def storedelete():
    if not request.form.get('confirmInput'):
        return deletestore(feedback_message='Please confirm deletion.', feedback_type=False)
    store_name = request.form.get("storenames")
    try:
        obj = db.session.query(Store).filter(
            Store.Store_ID==store_name).first()
        if obj == None:
            return deletestore(feedback_message='Store does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
    except Exception as ERROR:
        db.session.rollback()
        return deletestore(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return deletestore(feedback_message='Store deleted successfully.', feedback_type=True)

@app.route("/deletestoreid/<int:id>", methods=['GET','POST']) #DONE BY ELVIS
def storedeleteid(id):
    if not request.form.get('confirmInput'):
        return render_template("deletestoreid.html", feedback_message='Please confirm deletion.', feedback_type=False)
    try:
        obj = db.session.query(Store).filter(
            Store.Store_ID==id).first()
        if obj == None:
            return render_template("deletestoreid.html", feedback_message='Store does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
        return redirect('/readstore')
    except Exception as ERROR:
        db.session.rollback()
        return render_template("deletestoreid.html", feedback_message='An error occurred. Please try again.', feedback_type=False)

@app.route("/deleteproduct")
def deleteproduct(feedback_message=None, feedback_type=False):
    product_names = [name for name, _, _, _, _, _, _ in getproducts()]
    return render_template("deleteproduct.html", 
                           productnames=product_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/productdelete", methods=['POST'])
def productdelete():
    if not request.form.get('confirmInput'):
        return deleteproduct(feedback_message='Operation canceled. Product not deleted.', feedback_type=False)
    
    product_name = request.form.get('productnames')

    try:
        obj = db.session.query(Product).filter(
            Product.Product_ID==product_name).first()
        
        if obj == None:
            msg = 'Product {} not found.'.format(product_name)
            return deleteproduct(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deleteproduct(feedback_message=err, feedback_type=False)

    return deleteproduct(feedback_message='Successfully deleted product {}'.format(product_name),
                       feedback_type=True)

@app.route("/deleteproductid/<int:id>", methods=['GET','POST']) #DONE BY ELVIS
def productdeleteid(id):
    if not request.form.get('confirmInput'):
        return render_template("deleteproductid.html", feedback_message='Please confirm deletion.', feedback_type=False)
    try:
        obj = db.session.query(Product).filter(
            Product.Product_ID==id).first()
        if obj == None:
            return render_template("deleteproductid.html", feedback_message='Product does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
        return redirect('/readproduct')
    except Exception as ERROR:
        db.session.rollback()
        return render_template("deleteproductid.html", feedback_message='An error occurred. Please try again.', feedback_type=False)

@app.route("/deleteorder")
def deleteorder(feedback_message=None, feedback_type=False):
    order_names = [name for name, _, _, _, _, _, _ in getorders()]
    return render_template("deleteorder.html", 
                           ordernames=order_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/orderdelete", methods=['POST'])
def orderdelete():
    if not request.form.get('confirmInput'):
        return deleteorder(feedback_message='Operation canceled. Order not deleted.', feedback_type=False)
    
    order_name = request.form.get('ordernames')

    try:
        obj = db.session.query(Orders).filter(
            Orders.Order_ID==order_name).first()
        
        if obj == None:
            msg = 'Order {} not found.'.format(order_name)
            return deleteorder(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deleteorder(feedback_message=err, feedback_type=False)

    return deleteorder(feedback_message='Successfully deleted order {}'.format(order_name),
                       feedback_type=True)

@app.route("/deleteorderid/<int:id>", methods=['GET','POST']) #DONE BY ELVIS
def orderdeleteid(id):
    if not request.form.get('confirmInput'):
        return render_template("deleteorderid.html", feedback_message='Please confirm deletion.', feedback_type=False)
    try:
        obj = db.session.query(Orders).filter(
            Orders.Order_ID==id).first()
        if obj == None:
            return render_template("deleteorderid.html", feedback_message='Store does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
        return redirect('/readorder')
    except Exception as ERROR:
        db.session.rollback()
        return render_template("deleteorderid.html", feedback_message='An error occurred. Please try again.', feedback_type=False)

@app.route("/deleteemployee")
def deleteemployee(feedback_message=None, feedback_type=False):
    employee_IDs = [name for name, _, _, _, _, _, _, _ in getemployees()]
    return render_template("deleteemployee.html", 
                           employeeIDs=employee_IDs, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/employeedelete", methods=['POST'])
def employeedelete():
    if not request.form.get('confirmInput'):
        return deleteemployee(feedback_message='Operation canceled. Employee not deleted.', feedback_type=False)
    
    employee_ID = request.form.get('employeeIDs')

    try:
        obj = db.session.query(Employee).filter(
            Employee.Employee_ID==employee_ID).first()
        
        if obj == None:
            msg = 'Employee {} not found.'.format(employee_ID)
            return deleteemployee(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deleteemployee(feedback_message=err, feedback_type=False)

    return deleteemployee(feedback_message='Successfully deleted employee with {}'.format(employee_ID),
                       feedback_type=True)

@app.route("/deleteemployeeid/<int:id>", methods=['GET','POST']) #DONE BY ELVIS
def employeedeleteid(id):
    if not request.form.get('confirmInput'):
        return render_template("deleteemployeeid.html", feedback_message='Please confirm deletion.', feedback_type=False)
    try:
        obj = db.session.query(Employee).filter(
            Employee.Employee_ID==id).first()
        if obj == None:
            return render_template("deleteemployeeid.html", feedback_message='Store does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
        return redirect('/reademployee')
    except Exception as ERROR:
        db.session.rollback()
        return render_template("deleteemployeeid.html", feedback_message='An error occurred. Please try again.', feedback_type=False)

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

@app.route("/deletemanfid/<int:id>", methods=['GET','POST']) #DONE BY ELVIS
def manfdeleteid(id):
    if not request.form.get('confirmInput'):
        return render_template("deletemanfid.html", feedback_message='Please confirm deletion.', feedback_type=False)
    try:
        obj = db.session.query(Manufacturer).filter(
            Manufacturer.Manufacturer_Name == id).filter().first()
        if obj == None:
            return render_template("deletemanfid.html", feedback_message='Store does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
        return redirect('/readorder')
    except Exception as ERROR:
        db.session.rollback()

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username_ = form.username.data
        print(username_)
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                if('admin' in username_):
                    return redirect(url_for('dashboard'))
                elif('store' in username_):
                    return redirect(url_for('dashboard2'))
                elif('manufacturer' in username_):
                    return redirect(url_for('dashboard3'))
                
    return render_template('login.html', form = form)

@app.route('/home')
def home():
    return render_template('home.html')
