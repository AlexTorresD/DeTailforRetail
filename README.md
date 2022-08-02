# CSCE 310 - Sample App Python

## Introduction ##

This project provides sample code for the project of CSCE 310 of Summer 2022.
Implemented in Python 3, we use PostgreSQL as our server, SQLAlchemy and Flask as our backend, and HTML as our frontend.

## Requirements ##

* PostgreSQL - 14
* Python 3.10
* SQLAlchemy - 1.4.36
* Flask - 2.1.2
* Flask-SQLAlchemy - v2.5.1


## Installation ##

First, install [PostgreSQL](https://www.postgresql.org/download/) in your machine.

For the remaining dependencies, you may choose to install them independently or via our anaconda environment file.
We provide an environment.yml file to facilitate cloning a anaconda virtual environment that includes all our dependencies.
Make sure you have Anaconda installed. If not, install it via your preferred conda installer. We recommend [MiniConda](https://docs.conda.io/en/latest/miniconda.html).

To clone our provided environment, simply enter the following in an anaconda-enabled terminal:

```
conda env create -f environment.yml
```

Then, you can activate the environment by using:
 
```
conda activate csce310app
```


## Connect to Database and Create Tables ##

Before running the application, you need to deploy tables described in the beginning of the app.py file to our PostgreSQL database server.

To do that, you should first update the database credentials in the beginning of app.py to match your PostgreSQL configuration. The configuration string follows the following pattern:

 `postgresql://<user>:<password>@<hostname>/<databasename>`

 For simplicity, our application follows the default postgres username, and it's executed on localhost, as follows:

 `postgresql://postgres:supersecretpassword@localhost/csce310-app`

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

If you have any issues executing this application, do not hesitate to contact the responsible TA at [pedrofigueiredo@tamu.edu](pedrofigueiredo@tamu.edu), or attend his office hours.
<<<<<<< HEAD
=======
# project-example-python
Repository holding the source code of the example Python project for CSCE 310, Summer 2022.
>>>>>>> Initial commit
=======
>>>>>>> Python Application Upload
