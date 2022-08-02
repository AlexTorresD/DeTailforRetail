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


'''
class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dname = db.Column(db.String(64), unique=True)
    ddetail = db.Column(db.String(128))


class Cooks(db.Model):
    chefid = db.Column(db.Integer, db.ForeignKey('chef_info.id', ondelete='CASCADE'),
        nullable=False, primary_key=True)
    dishid = db.Column(db.Integer, db.ForeignKey('dish.id', ondelete='CASCADE'),
        nullable=False, primary_key=True)
    
    chef = db.relationship('ChefInfo',
        backref=db.backref('dishes', lazy=True, passive_deletes=True))
    dish = db.relationship('Dish',
        backref=db.backref('chefs', lazy=True, passive_deletes=True))
    
class ChefInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(64), unique=True)
    addr = db.Column(db.String(128))
    phone = db.Column(db.String(64))
    

'''
    
class Employee(db.Model):
    Employee_ID = db.Column(db.Integer, primary_key=True)
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID')) #add foreign key
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
    product_Relation = db.relationship('product', backref='manufacturer', lazy=True)

class Product(db.Model):
    Product_ID = db.Column(db.Integer, primary_key=True)
    Manufacturer_ID = db.Column(db.Integer, db.ForeignKey('manufacturer.Manufacturer_ID')) #foreign ref
    Product_Price = db.Column(db.Float)
    Product_Quantity = db.Column(db.Integer)
    Product_Size = db.Column(db.Integer)
    Product_Type = db.Column(db.String(128))
    Product_Description = db.Column(db.String(128))
    ordes_Relation = db.relationship('orders', backref='product', lazy=True)

class Orders(db.Model):
    Order_ID = db.Column(db.Integer, primary_key=True)
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID')) #foreign ref
    Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID')) #foreign ref
    Order_Quantity = db.Column(db.Integer)
    Order_Price = db.Column(db.Float)
    Order_Date = db.Column(db.DateTime)
    Received = db.Column(db.Boolean)


class Store(db.Model): #DONE BY ELVIS
    Store_ID = db.Column(db.Integer, primary_key=True) #primary key #store id 
    Store_Name = db.Column(db.String(128)) #store name
    Location = db.Column(db.String(128))   #store location

    product_Relation = db.relationship('product', backref='store', lazy=True) #?

#DONE BY ELVIS
class Staff(db.Model): #DONE BY ELVIS
    Staff_ID = db.Column(db.Integer, primary_key=True) # primary key #staff id
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID')) #foriegn key 
    Employee_ID = db.Column(db.Integer, db.ForeignKey('employee.Employee_ID')) #foriegn key

    Employee_Relation = db.relationship('Employee', backref='staff', lazy=True) #?


if __name__ == '__main__':
    app.run()

#***
    #***
        #***   
#------------------------------------------------------ START OF ELVIS'S CODE #DONE BY ELVIS
        #***
    #***
#***

    #START GET------------------------------------------------------#DONE BY ELVIS 
        #getallstaff() 
def getstaff(): #DONE BY ELVIS
    query = select(Staff)
    result = db.session.execute(query)
    staff_list = []
    for Staff in result.scalars():
        staff_list.append(Staff.Staff_ID, Staff.Store_ID, Staff.Employee_ID)
    return staff_list
        #getstores()   
def getstore(): #DONE BY ELVIS
    query = select(Store)
    result = db.session.execute(query)
    store_list = []
    for Store in result.scalars():
        store_list.append(Store.Store_ID, Store.Store_Name, Store.Location)
    return store_list
    #END GET------------------------------------------------------START OF GET SCHEME #DONE BY ELVIS 

    #START CREATE------------------------------------------------------#DONE BY ELVIS    
        #create store and store create
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
    #END CREATE------------------------------------------------------#DONE BY ELVIS    


#START READ--------------------------------------------------------#DONE BY ELVIS

@app.route("/readstaff")
def readstaff(): #DONE BY ELVIS
    query = select(Staff)
    result = db.session.execute(query)
    staff_list = []
    for Staff in result.scalars():
        staff_list.append(Staff.Staff_ID, Staff.Store_ID, Staff.Employee_ID)
    return render_template("readstaff.html", staff_list=staff_list)

@app.route("/readstore")
def readstore(): #DONE BY ELVIS
    query = select(Store)
    result = db.session.execute(query)
    store_list = []
    for Store in result.scalars():
        store_list.append(Store.Store_ID, Store.Store_Name, Store.Location)
    return render_template("readstore.html", store_list=store_list)

#END READ--------------------------------------------------------#DONE BY ELVIS

#START UPDATE--------------------------------------------------------#DONE BY ELVIS

@app.route("/updatestaff")
def updatestaff(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    staff_name = [name for name ,_, _ in getstaff()]
    #     order_names = [name for name, _, _, _, _, _, _ in getorders()]
    return render_template("updatestaff.html", staff_name=staff_name, feedback_message=feedback_message, feedback_type=feedback_type)


@app.route("/staffupdate", methods=['POST'])
def staffupdate(): #DONE BY ELVIS
    Staff_ID = request.form.get("Staff_ID"); Store_ID = request.form.get("Store_ID"); Employee_ID = request.form.get("Employee_ID")
    try:
        obj = Staff.query.filter_by(Staff_ID=Staff_ID).first()
        if obj == '':
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

@app.route("/updatestore")
def updatestore(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    store_name = [name for name ,_, _ in getstore()]
    return render_template("updatestore.html", store_name=store_name, feedback_message=feedback_message, feedback_type=feedback_type)
@app.route("/storeupdate", methods=['POST'])
def storeupdate(): #DONE BY ELVIS
    Store_ID = request.form.get("Store_ID"); Store_Name = request.form.get("Store_Name"); Location = request.form.get("Location")
    try:
        obj = Store.query.filter_by(Store_ID=Store_ID).first()
        if obj == '':
            return updatestore(feedback_message='Store ' + Store_ID + ' does not exist. Please try again.', feedback_type=False)
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
    return updatestore(feedback_message='Store ' + Store_ID + ' updated successfully.', feedback_type=True)

#END UPDATE--------------------------------------------------------#DONE BY ELVIS

#START DELETE--------------------------------------------------------#DONE BY ELVIS

@app.route("/deletestaff")
def deletestaff(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    staff_name = [name for name ,_, _ in getstaff()]
    return render_template("deletestaff.html", staff_name=staff_name, feedback_message=feedback_message, feedback_type=feedback_type)
@app.route("/staffdelete", methods=['POST']) #DONE BY ELVIS
def staffdelete():
    if not request.form.get('confirmInput'):
        return deletestaff(feedback_message='Please confirm deletion.', feedback_type=False)
    Staff_ID = request.form.get("Staff_ID")
    try:
        obj = Staff.query.filter_by(Staff_ID=Staff_ID).first()
        if obj == '':
            return deletestaff(feedback_message='Staff ' + Staff_ID + ' does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
    except Exception as ERROR:
        db.session.rollback()
        return deletestaff(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return deletestaff(feedback_message='Staff ' + Staff_ID + ' deleted successfully.', feedback_type=True)
@app.route("/deletestore")
def deletestore(feedback_message=None, feedback_type=False): #DONE BY ELVIS
    store_name = [name for name ,_, _ in getstore()]
    return render_template("deletestore.html", store_name=store_name, feedback_message=feedback_message, feedback_type=feedback_type)
@app.route("/storedelete", methods=['POST']) #DONE BY ELVIS
def storestore():
    if not request.form.get('confirmInput'):
        return deletestore(feedback_message='Please confirm deletion.', feedback_type=False)
    Store_ID = request.form.get("Store_ID")
    try:
        obj = Store.query.filter_by(Store_ID=Store_ID).first()
        if obj == '':
            return deletestore(feedback_message='Store ' + Store_ID + ' does not exist. Please try again.', feedback_type=False)
        db.session.delete(obj)
        db.session.commit()
    except Exception as ERROR:
        db.session.rollback()
        return deletestore(feedback_message='An error occurred. Please try again.', feedback_type=False)
    return deletestore(feedback_message='Store ' + Store_ID + ' deleted successfully.', feedback_type=True)

#END DELETE--------------------------------------------------------#DONE BY ELVIS


#***
    #***
        #***
#------------------------------------------------------ END OF ELVIS'S CODE #DONE BY ELVIS
        #***
    #***
#***


# def getorders():
#     query = select(Orders)
#     result = db.session.execute(query)

#     order_list = []
#     for order in result.scalars():
#         order_list.append((order.Order_ID, order.Store_ID, order.Product_ID, order.Order_Quantity, order.Order_Price, order.Order_Date, order.Received))
#     return order_list

# @app.route("/createorder")
# def createorder(feedback_message=None, feedback_type=False):
#     return render_template("createorder.html",
#             feedback_message=feedback_message, 
#             feedback_type=feedback_type)

# @app.route("/ordercreate", methods=['POST'])
# def ordercreate():
#     Order_ID = request.form["Order_ID"]
#     Store_ID = request.form["Store_ID"]
#     Product_ID = request.form["Product_ID"]
#     Order_Quantity = request.form["Order_Quanity"]
#     Order_Price = request.form["Order_Price"]
#     Order_Date = request.form["Order_Date"]
#     Received = request.form["Received"]

#     try:
#         entry = Orders(Order_ID=Order_ID, Store_ID=Store_ID, Product_ID=Product_ID, Order_Quantity=Order_Quantity, Order_Price=Order_Price, Order_Date=Order_Date, Received=True)
#         db.session.add(entry)
#         db.session.commit()
#     except exc.IntegrityError as err:
#         db.session.rollback()
#         return createorder(feedback_message='A order with ID {} already exists. Create a order with a different name.'.format(Order_ID), feedback_type=False)
#     except Exception as err:
#         db.session.rollback()
#         return createorder(feedback_message='Database error: {}'.format(err), feedback_type=False)
            

#     return createorder(feedback_message='Successfully added order {}'.format(Order_ID),
#                        feedback_type=True)

# @app.route("/readorder")
# def readorder():
#     query = select(Orders)
#     result = db.session.execute(query)

#     order_list = []
#     for order in result.scalars():
#         order_list.append((order.Order_ID, order.Store_ID, order.Product_ID, order.Order_Quantity, order.Order_Price, order.Order_Date, order.Received))
    
#     return render_template("readorder.html", orderlist=order_list)

# @app.route("/updateorder")
# def updateorder(feedback_message=None, feedback_type=False):
#     order_names = [name for name, _, _, _, _, _, _ in getorders()]
#     return render_template("updateorder.html", 
#                            ordernames=order_names, 
#                            feedback_message=feedback_message, 
#                            feedback_type=feedback_type)

# @app.route("/orderupdate", methods=['POST'])
# def orderupdate():
#     order_name = request.form.get('ordernames')
#     Order_ID = request.form["Order_ID"]
#     Store_ID = request.form["Store_ID"]
#     Product_ID = request.form["Product_ID"]
#     Order_Quantity = request.form["Order_Quanity"]
#     Order_Price = request.form["Order_Price"]
#     Order_Date = request.form["Order_Date"]
#     Received = request.form["Received"]

#     try:
#         obj = db.session.query(Orders).filter(
#             Orders.Order_ID==order_name).first()
        
#         if obj == None:
#             msg = 'Order {} not found.'.format(Order_ID)
#             return updateorder(feedback_message=msg, feedback_type=False)

#         if Order_ID != '':
#             obj.Order_ID = Order_ID
#         if Store_ID != '':
#             obj.Store_ID = Store_ID
#         if Product_ID != '':
#             obj.Product_ID = Product_ID
#         if Order_Quantity != '':
#             obj.Order_Quantity = Order_Quantity
#         if Order_Price != '':
#             obj.Order_Price = Order_Price
#         if Order_Date != '':
#             obj.Order_Date = Order_Date
#         if Received != '':
#             obj.Received = Received
        
#         db.session.commit()
#     except Exception as err:
#         db.session.rollback()
#         return updateorder(feedback_message=err, feedback_type=False)

#     return updateorder(feedback_message='Successfully updated order {}'.format(Order_ID),
#                        feedback_type=True)

# @app.route("/deleteorder")
# def deleteorder(feedback_message=None, feedback_type=False):
#     order_names = [name for name, _, _, _, _, _, _ in getorders()]
#     return render_template("deleteorder.html", 
#                            ordernames=order_names, 
#                            feedback_message=feedback_message, 
#                            feedback_type=feedback_type)

# @app.route("/orderdelete", methods=['POST'])
# def orderdelete():
#     if not request.form.get('confirmInput'):
#         return deleteorder(feedback_message='Operation canceled. Order not deleted.', feedback_type=False)
    
#     order_name = request.form.get('ordernames')

#     try:
#         obj = db.session.query(Orders).filter(
#             Orders.Order_ID==order_name).first()
        
#         if obj == None:
#             msg = 'Order {} not found.'.format(order_name)
#             return deleteorder(feedback_message=msg, feedback_type=False)
        
#         db.session.delete(obj)
#         db.session.commit()
#     except Exception as err:
#         db.session.rollback()
#         return deleteorder(feedback_message=err, feedback_type=False)

#     return deleteorder(feedback_message='Successfully deleted order {}'.format(order_name),
#  
# 
#                      feedback_type=True)



'''
def getchefs():
    query = select(ChefInfo)
    result = db.session.execute(query)

    chef_list = []
    for chef in result.scalars():
        chef_list.append((chef.cname, chef.addr, chef.phone))
    return chef_list



def getdishes():
    query = select(Dish)
    result = db.session.execute(query)

    dish_list = []
    for dish in result.scalars():
        dish_list.append((dish.dname, dish.ddetail))
    return dish_list






def getcooks():
    query = select(Cooks)
    result = db.session.execute(query)

    cookslist = []
    for cooks in result.scalars():
        chef_id = cooks.chefid
        dish_id = cooks.dishid

        chef = get_chef_fromid(chef_id)
        dish = get_dish_fromid(dish_id)

        cookslist += [(chef.cname, dish.dname)]


    return cookslist






@app.route('/')
def home():
    return render_template('home.html')


##### CREATE 

@app.route("/createchef")
def createchef(feedback_message=None, feedback_type=False):
    return render_template("createchef.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)

@app.route("/chefcreate", methods=['POST'])
def chefcreate():
    cname = request.form["cname"]
    addr = request.form["addr"]
    phone = request.form["phone"]

    try:
        entry = ChefInfo(cname=cname, addr=addr, phone=phone)
        db.session.add(entry)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createchef(feedback_message='A chef named {} already exists. Create a chef with a different name.'.format(cname), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createchef(feedback_message='Database error: {}'.format(err), feedback_type=False)
            

    return createchef(feedback_message='Successfully added chef {}'.format(cname),
                       feedback_type=True)

@app.route("/createdish")
def createdish(feedback_message=None, feedback_type=False):
    return render_template("createdish.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)

@app.route("/dishcreate", methods=['POST'])
def dishcreate():
    dname = request.form["dname"]
    ddetail = request.form["ddetail"]

    try:
        entry = Dish(dname=dname, ddetail=ddetail)
        db.session.add(entry)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createdish(feedback_message='A dish named {} already exists. Create a dish with a different name.'.format(dname), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createdish(feedback_message='Database error: {}'.format(err), feedback_type=False)

    return createdish(feedback_message='Successfully added dish {}'.format(dname),
                       feedback_type=True)


@app.route("/createcooks")
def createcooks(feedback_message=None, feedback_type=False):
    chef_names = [name for name, _, _ in getchefs()]
    dish_names = [name for name, _ in getdishes()]
    return render_template("createcooks.html", 
                           chefnames=chef_names, 
                           dishnames=dish_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)


def get_chef(chefname):
    query = select(ChefInfo).where(ChefInfo.cname==chefname)
    result = db.session.execute(query)
    chef = result.scalar()
    if chef is None:
        raise('Chef not found')
    return chef

def get_dish(dishname):
    query = select(Dish).where(Dish.dname==dishname)
    result = db.session.execute(query)
    dish = result.scalar()
    if dish is None:
        raise('Dish not found')
    return dish

def get_chef_fromid(chefid):
    query = select(ChefInfo).where(ChefInfo.id==chefid)
    result = db.session.execute(query)
    chef = result.scalar()
    if chef is None:
        raise('Chef not found')
    return chef

def get_dish_fromid(dishid):
    query = select(Dish).where(Dish.id==dishid)
    result = db.session.execute(query)
    dish = result.scalar()
    if dish is None:
        raise('Dish not found')
    return dish


@app.route("/cookscreate", methods=['POST'])
def cookscreate():
    chef_name = request.form.get('chefnames')
    dish_name = request.form.get('dishnames')

    try:
        chef = get_chef(chef_name)
        dish = get_dish(dish_name)
        entry = Cooks(chef=chef, dish=dish)
        db.session.add(entry)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return createcooks(feedback_message=err, feedback_type=False)

    return createcooks(feedback_message='Successfully added cooks relationship between {} and {}'.format(chef_name, dish_name),
                       feedback_type=True)

##### READ

@app.route("/readchef")
def readchef():
    query = select(ChefInfo)
    result = db.session.execute(query)

    chef_list = []
    for chef in result.scalars():
        chef_list.append((chef.cname, chef.addr, chef.phone))
    
    return render_template("readchef.html", cheflist=chef_list)

@app.route("/readdish")
def readdish():
    dish_list = getdishes()
    return render_template("readdish.html", dishlist=dish_list)

@app.route("/readcooks")
def readcooks():
    cooks_list = getcooks()
    return render_template("readcooks.html", cookslist=cooks_list)


##### UPDATE 

@app.route("/updatechef")
def updatechef(feedback_message=None, feedback_type=False):
    chef_names = [name for name, _, _ in getchefs()]
    return render_template("updatechef.html", 
                           chefnames=chef_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/chefupdate", methods=['POST'])
def chefupdate():
    chef_name = request.form.get('chefnames')
    cname = request.form["cname"]
    addr = request.form["addr"]
    phone = request.form["phone"]

    try:
        obj = db.session.query(ChefInfo).filter(
            ChefInfo.cname==chef_name).first()
        
        if obj == None:
            msg = 'Chef {} not found.'.format(chef_name)
            return updatechef(feedback_message=msg, feedback_type=False)

        if cname != '':
            obj.cname = cname
        if addr != '':
            obj.addr = addr
        if phone != '':
            obj.phone = phone
        
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return updatechef(feedback_message=err, feedback_type=False)

    return updatechef(feedback_message='Successfully updated chef {}'.format(chef_name),
                       feedback_type=True)


@app.route("/updatedish")
def updatedish(feedback_message=None, feedback_type=False):
    dish_names = [name for name, _, in getdishes()]
    return render_template("updatedish.html", 
                           dishnames=dish_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/dishupdate", methods=['POST'])
def dishupdate():
    dish_name = request.form.get('dishnames')
    dname = request.form["dname"]
    ddetail = request.form["ddetail"]

    try:
        obj = db.session.query(Dish).filter(
            Dish.dname==dish_name).first()
        
        if obj == None:
            msg = 'Dish {} not found.'.format(dish_name)
            return updatedish(feedback_message=msg, feedback_type=False)
        
        if dname != '':
            obj.dname = dname
        if ddetail != '':
            obj.ddetail = ddetail
        
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return updatedish(feedback_message=err, feedback_type=False)

    return updatedish(feedback_message='Successfully updated dish {}'.format(dish_name),
                       feedback_type=True)


@app.route("/updatecooks")
def updatecooks(feedback_message=None, feedback_type=False):
    chef_names = [name for name, _, _ in getchefs()]
    dish_names = [name for name, _ in getdishes()]
    return render_template("updatecooks.html", 
                           chefnames=chef_names, 
                           dishnames=dish_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/cooksupdate", methods=['POST'])
def cooksupdate():
    chef_name1 = request.form.get('chefnames1')
    dish_name1 = request.form.get('dishnames1')

    chef_name2 = request.form.get('chefnames2')
    dish_name2 = request.form.get('dishnames2')

    try:
        
        chef1 = get_chef(chef_name1)
        dish1 = get_dish(dish_name1)

        obj = db.session.query(Cooks).filter(
            Cooks.chefid==chef1.id, 
            Cooks.dishid==dish1.id).first()
        
        if obj == None:
            msg = 'Cooks relationship between {} and {} not found.'.format(chef_name1, dish_name1)
            return updatecooks(feedback_message=msg, feedback_type=False)
        
        chef2 = get_chef(chef_name2)
        dish2 = get_dish(dish_name2)

        obj.chefid = chef2.id
        obj.dishid = dish2.id

        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return updatecooks(feedback_message=err, feedback_type=False)

    return updatecooks(feedback_message='Successfully updated cooks relationship from ({} and {}) to ({} and {})'.format(chef_name1, dish_name1, chef_name2, dish_name2),
                       feedback_type=True)


#### DELETE

@app.route("/deletechef")
def deletechef(feedback_message=None, feedback_type=False):
    chef_names = [name for name, _, _ in getchefs()]
    return render_template("deletechef.html", 
                           chefnames=chef_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/chefdelete", methods=['POST'])
def chefdelete():
    if not request.form.get('confirmInput'):
        return deletechef(feedback_message='Operation canceled. Chef not deleted.', feedback_type=False)
    
    chef_name = request.form.get('chefnames')

    try:
        obj = db.session.query(ChefInfo).filter(
            ChefInfo.cname==chef_name).first()
        
        if obj == None:
            msg = 'Chef {} not found.'.format(chef_name)
            return deletechef(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deletechef(feedback_message=err, feedback_type=False)

    return deletechef(feedback_message='Successfully deleted chef {}'.format(chef_name),
                       feedback_type=True)


@app.route("/deletedish")
def deletedish(feedback_message=None, feedback_type=False):
    dish_names = [name for name, _ in getdishes()]
    return render_template("deletedish.html", 
                           dishnames=dish_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type) 

@app.route("/dishdelete", methods=['POST'])
def dishdelete():
    if not request.form.get('confirmInput'):
        return deletedish(feedback_message='Operation canceled. Dish not deleted.', feedback_type=False)
    
    dish_name = request.form.get('dishnames')

    try:
        obj = db.session.query(Dish).filter(
            Dish.dname==dish_name).first()
        
        if obj == None:
            msg = 'Dish {} not found.'.format(dish_name)
            return deletedish(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deletedish(feedback_message=err, feedback_type=False)

    return deletedish(feedback_message='Successfully deleted dish {}'.format(dish_name),
                       feedback_type=True)


@app.route("/deletecooks")
def deletecooks(feedback_message=None, feedback_type=False):
    chef_names = [name for name, _, _ in getchefs()]
    dish_names = [name for name, _ in getdishes()]
    return render_template("deletecooks.html", 
                           chefnames=chef_names, 
                           dishnames=dish_names, 
                           feedback_message=feedback_message, 
                           feedback_type=feedback_type)

@app.route("/cooksdelete", methods=['POST'])
def cooksdelete():
    chef_name = request.form.get('chefnames')
    dish_name = request.form.get('dishnames')

    try:
        chef = db.session.query(ChefInfo).filter(
            ChefInfo.cname==chef_name).first()
        dish = db.session.query(Dish).filter(
            Dish.dname==dish_name).first()

        obj = db.session.query(Cooks).filter(
            Cooks.chef==chef, 
            Cooks.dish==dish).first()
        
        if obj == None:
            msg = 'Cooks relationship between {} and {} not found.'.format(chef_name, dish_name)
            return deletecooks(feedback_message=msg, feedback_type=False)
        
        db.session.delete(obj)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return deletecooks(feedback_message=err, feedback_type=False)

    return deletecooks(feedback_message='Successfully deleted cooks relationship between {} and {}'.format(chef_name, dish_name),
                       feedback_type=True)
'''
