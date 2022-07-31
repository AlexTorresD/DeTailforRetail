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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/DeTail'
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
    Customer_Email = db.Column(db.String(128))
    Customer_Phone = db.Column(db.String(128))
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

#Create Product
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
    except exc.IntegrityError as err:
        db.session.rollback()
        return createorder(feedback_message='A order with ID {} already exists. Create a order with a different name.'.format(Order_ID), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createorder(feedback_message='Database error: {}'.format(err), feedback_type=False)
            

    return createorder(feedback_message='Successfully added order {}'.format(Order_ID),
                       feedback_type=True)

#Read 
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
    
#Delete
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

@app.route('/')
def home():
    return render_template('home.html')