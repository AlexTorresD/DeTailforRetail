from modulefinder import STORE_NAME
from multiprocessing import synchronize
from turtle import position
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy import exc
from sqlalchemy import update
import psycopg2

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<user>:<password>@localhost/<appname>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://e-home:hihime45@localhost/csce310-app'
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
    Employee_Phone = db.Column(db.String(128), unique=True)
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
        db.session.commit()


    except exc.IntegrityError as err:
        db.session.rollback()
        return createmanf(feedback_message='A Manufacturer named {} already exists. Create a Manufacturer with a different name.'.format(name), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createmanf(feedback_message='Database error: {}'.format(err), feedback_type=False)
    
    return createmanf(feedback_message='Successfully added Manufacturer {}'.format(name), ##### might need to change name
                       feedback_type=True)

@app.route("/createemployee")
def createemployee(feedback_message=None, feedback_type=False):
    return render_template("createemployee.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)

#create trigger function, whhen we insert on Orders table we will update product quantity in product table
def update_product_quantity(product_id, order_quantity):
    query = update(Product).where(Product.Product_ID == product_id).values(Product_Quantity = Product.Product_Quantity - order_quantity)
    db.session.execute(query)
    db.session.commit()

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
            Employee_Email=Employee_Email,Employee_Phone=Employee_Phone, Position=Position, 
            Hours_Worked=Hours_Worked, Salary=Salary)
        db.session.add(entry)
        db.session.commit()
    except exc.IntegrityError as err:
        print('testingggggg')
        db.session.rollback()
        #if phone number is already in the database, return error message
        return createemployee(feedback_message='An Employee with the ID {} already exists. Create an Employee with a different ID.'.format(Employee_ID), feedback_type=False)
        # if err.orig.diag.constraint_name == 'employee_id_key':
        #     print('Employee ID already exists')
        #     return createemployee(feedback_message='An Employee with ID {} already exists. Create an Employee with a different ID.'.format(Employee_ID), feedback_type=False)
        # if err.orig.diag.constraint_name == 'employee_email_key':
        #     print('Employee Email already exists')
        #     return createemployee(feedback_message='An Employee with email {} already exists. Create an Employee with a different email.'.format(Employee_Email), feedback_type=False)
        # if err.orig.diag.constraint_name == 'employee_phone_key':
        #     print('Employee Phone already exists')
        #     return createemployee(feedback_message='An Employee with phone {} already exists. Create an Employee with a different phone.'.format(Employee_Phone), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createemployee(feedback_message='Database error: {} '.format(err), feedback_type=False)

    # try:
    #     entry2 = Employee(Employee_ID=Employee_ID, Employee_Fname=Employee_Fname, Employee_Lname=Employee_Lname, 
    #         Employee_Email=Employee_Email, Employee_Phone=Employee_Phone, Position=Position, 
    #         Hours_Worked=Hours_Worked, Salary=Salary)
        
    #     db.session.delete(entry)
    #     db.session.add(entry2)
    #     db.session.commit()
    # except exc.IntegrityError as err:
    #     db.session.rollback()
    #     return createemployee(feedback_message='An employee with phone {} {} already exists. Create an employee with a different phone.'.format(Employee_Phone), feedback_type=False)
    # except Exception as err:
    #     db.session.rollback()
    #     return createemployee(feedback_message='Database error: {} '.format(err), feedback_type=False)

            
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
        db.session.add(entry); db.session.commit()
    except exc.IntegrityError as ERROR:
        db.session.rollback()
        return createstore(feedback_message='ID' + Store_ID + "already exists. Please try again.", feedback_type=False)
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
        db.session.add(entry); db.session.commit()
    except exc.IntegrityError as ERROR:
        db.session.rollback()
        return createstaff(feedback_message='ID' + Staff_ID + "already exists. Please try again.", feedback_type=False)
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
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createproduct(feedback_message='A product with ID {} already exists. Create a product with a different ID.'.format(Product_ID), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createproduct(feedback_message='Database error: {}'.format(err), feedback_type=False)
    
    #update_product_quantity(product_id, order_quantity):
    #use update_product_quantity to update the quantity of a product in the database


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
        db.session.commit()
    #error for duplicate phone number
    
    except exc.IntegrityError as err:
        db.session.rollback()
        return createorder(feedback_message='A order with ID {} already exists. Create a order with a different name.'.format(Order_ID), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createorder(feedback_message='Database error: {}'.format(err), feedback_type=False)
    
    # def update_product_quantity(product_id, order_quantity):
    # query = update(Product).where(Product.Product_ID == product_id).values(Product_Quantity = Product.Product_Quantity - order_quantity)
    # db.session.execute(query)
    # db.session.commit()

    product_quan = Product.query.filter_by(Product_ID=Product_ID).first()
    #convert to int
    int_prod = product_quan.Product_Quantity = product_quan.Product_Quantity - int(Order_Quantity)
    if (int_prod < 0):
        db.session.rollback()
        return createorder(feedback_message='Order quantity cannot be negative.', feedback_type=False)

    update_product_quantity(Product_ID, Order_Quantity)

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
@app.route("/updateemployee")
def updateemployee(feedback_message=None, feedback_type=False):
    employee_IDs = [name for name, _, _, _, _, _, _, _ in getemployees()]
    return render_template("updateemployee.html", 
                           employeeIDs = employee_IDs, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/employeeupdate", methods=['POST'])
def employeeupdate():
    e_ID = request.form.get('employeeIDs')
    Employee_ID = request.form["Employee_ID"]
    Employee_Fname = request.form["Employee_Fname"]
    Employee_Lname = request.form["Employee_Lname"]
    Employee_Email = request.form["Employee_Email"]
    Employee_Phone = request.form["Employee_Phone"]
    Position = request.form["Position"]
    Hours_Worked = request.form["Hours_Worked"]
    Salary = request.form["Salary"]

    try:
        obj = db.session.query(Employee).filter(
            Employee.Employee_ID==e_ID).first()
        
        if obj == None:
            msg = 'Employee {} not found.'.format(e_ID)
            return updateemployee(feedback_message=msg, feedback_type=False)
        if Employee_ID != '':
            obj.Employee_ID = Employee_ID
        else:
            obj.Employee_ID = e_ID
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
    except Exception as err:
        db.session.rollback()
        return updateemployee(feedback_message=err, feedback_type=False)

    return updateemployee(feedback_message='Successfully updated employee with ID {}'.format(e_ID),
                       feedback_type=True)

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
@app.route("/staffdelete", methods=['POST']) #DONE BY ELVIS
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

@app.route('/')
def home():
    return render_template('home.html')


