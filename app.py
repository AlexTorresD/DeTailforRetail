from multiprocessing import synchronize
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy import exc
import psycopg2

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<user>:<password>@localhost/<appname>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Gotright1@localhost/csce310-app'
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

class ChefInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(64), unique=True)
    addr = db.Column(db.String(128))
    phone = db.Column(db.String(64))


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


if __name__ == '__main__':
    app.run()

def getemployees():
    query = select(Employee)
    result = db.session.execute(query)
    emp_list = []
    for e in result.scalars():
        emp_list.append((e.Employee_ID, e.Employee_Fname, e.Employee_Lname, e.Employee_Email, e.Employee_Phone, e.Position, e.Hours_Worked, e.Salary))
    return emp_list

@app.route("/createemployee")
def createemployee(feedback_message=None, feedback_type=False):
    return render_template("createemployee.html",
            feedback_message=feedback_message, 
            feedback_type=feedback_type)
@app.route("/employeecreate", methods=['POST'])
def employeecreate():
    Employee_Fname = request.form["Employee_Fname"]
    Employee_Lname = request.form["Employee_Lname"]
    Employee_Email = request.form["Employee_Email"]
    Employee_Phone = request.form["Employee_Phone"]
    Position = request.form["Position"]
    Hours_Worked = request.form["Hours_Worked"]
    Salary = request.form["Salary"]
    try:
        entry = Employee(Employee_Fname=Employee_Fname, Employee_Lname=Employee_Lname, 
            Employee_Email=Employee_Email, Employee_Phone=Employee_Phone, Position=Position, 
            Hours_Worked=Hours_Worked, Salary=Salary)
        db.session.add(entry)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return createemployee(feedback_message='An employee with name {} {} already exists. Create an employee with a different name.'.format(Employee_Fname, Employee_Lname), feedback_type=False)
    except Exception as err:
        db.session.rollback()
        return createemployee(feedback_message='Database error: {} '.format(err), feedback_type=False)
    return createemployee(feedback_message='Successfully added employee {} {} '.format(Employee_Fname, Employee_Lname),
                       feedback_type=True)

@app.route("/reademployee")
def reademployee():
    query = select(Employee)
    result = db.session.execute(query)

    emp_list = []
    for e in result.scalars():
        emp_list.append((e.Employee_ID, e.Employee_Fname, e.Employee_Lname, e.Employee_Email, e.Employee_Phone, e.Position, e.Hours_Worked, e.Salary))
    
    return render_template("reademployee.html", empList=emp_list)

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
        if Employee_ID != ' ':
            obj.Employee_ID = Employee_ID
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

    return updateemployee(feedback_message='Successfully updated employee {}'.format(e_ID),
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

    return deleteemployee(feedback_message='Successfully deleted employee {}'.format(employee_ID),
                       feedback_type=True)
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