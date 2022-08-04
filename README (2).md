# Retail For Detail Readme

## Introduction ##

This project provides a solution to franchises that conduct frequent business to business transactions. Our app allows them to keep information about their manufacturers, employees, stores, and orders. Additionally stores can keep track of their product inventory, manage employee salary, etc. We used python 3 along with PostgreSQL as our server. For the backend, we used SQLAlchemy and Flask. For the Frontend we used HTML. 

## Requirements ##

* PostgreSQL - 14
* Python 3.10.4
* SQLAlchemy - 1.4.36
* Flask - 2.0.1
* Flask-SQLAlchemy - v2.5.1
* Git

## Installation ##

First, install [PostgreSQL](https://www.postgresql.org/download/) in your machine.

For the remaining dependencies, you may choose to install them independently or via our anaconda environment file.
We provide an environment.yml file to facilitate cloning a anaconda virtual environment that includes all our dependencies.
Make sure you have Anaconda installed. If not, install it via your preferred conda installer. We recommend [MiniConda](https://docs.conda.io/en/latest/miniconda.html).

To clone our repository, simply enter

```
git clone 
```

To clone our provided environment, simply enter the following in an anaconda-enabled terminal:

```
conda env create -f environment.yml
```

Then, you can activate the environment by using:
 
```
conda activate detailforretail
```


## Connect to Database and Create Tables ##

Before running the application, you need to deploy tables described in the beginning of the app.py file to our PostgreSQL database server.

To do that, you should first update the database credentials in the beginning of app.py to match your PostgreSQL configuration. The configuration string follows the following pattern:

 `postgresql://<user>:<password>@<hostname>/<databasename>`

 For simplicity, our application follows the default postgres username, and it's executed on localhost, as follows:

 `postgresql://[insertDBusername]:[insertDBpassword]@localhost/[DatabaseName]`

 With updated credentials, you can now deploy the tables.
 Navigate to the root directory of our application, and open a Python console in your preferred terminal by typing:

```
cd /path/to/app
python
```


Then, import the SQLAlchemy database object, and create all tables defined in app.py:

```python
from app import db
db.create_all()
```

You can verify that all tables were created by querying a database client with user interface such as PgAdmin or DBeaver.

## Execute Application ##

To run our web application, simply run the command

```
flask run
```

in your preferred terminal. The flask application should start automatically. It can be accessed on a browser via the link [http://localhost:5000](http://localhost:5000).


## Support

If you have any issues executing this application, please do not hesitate to contact the development team members, Josh Yang (Yingte.Yang@tamu.edu), Priyanka Rao (pbr27@tamu.edu), Alex Torres (robincrass@tamu.edu), Elvis Hedary(elvis@tamu.edu),  Or Sami Amin (samiamin@tamu.edu).
