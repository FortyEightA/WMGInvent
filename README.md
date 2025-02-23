# WMG Invent Fleet Manager

This project is a Flask-based web application of the initial implementation of the WMGInvent Fleet Management System, including fleet managment features, user authentication and searching, as well as a data report.


## Features

- Fleet managment
    - Vehicle CRUD
    - Vehicle history 
    - Current status
    - Future plans
    - Overall Tracking
- Search
    - Search on Registration, Make, Model and Year
- Data Dashboard
    - Current fleet status 
    - Fleet history
    - Number of users
- Role based Authentication
    - Dynamic, role-based HTML templates
    - Role-based route protection and CRUD protection



## Tech Stack

**Frontend:** HTML, CSS, Bootstrap, Jinja2, Plotly

**Server:** Flask

**Database:** SQLite


## File Structure
```
WMGInvent/
├── app/ # Form definitions
│ ├── static/ # all static files
│ │ ├── images/ # all images for vehicles
│ │ │ ├── VO60 DFP.jpg # example of vehicle image
│ │ │ ├── etc.
│ │ ├── account.css #css files
│ │ ├── add.css
│ │ ├── base.css
│ │ ├── car.css
│ │ ├── data.css
│ │ ├── fleet.css
│ │ ├── home.css
│ │ ├── login.css
│ │ ├── register.css
│ │ ├── update.css
│ ├── templates/ # all template files
│ │ ├── account.html #template html files
│ │ ├── add.html
│ │ ├── base.html
│ │ ├── car.html
│ │ ├── data.html
│ │ ├── fleet.html
│ │ ├── home.html
│ │ ├── login.html
│ │ ├── register.html
│ │ ├── update.html
│ ├── __init__.py #module file
│ ├── views.py #main views file containing all the service layer logic
├── run.py #app start point
├── test.py #app tests
├── WMGInvent.db #database
├── requirements.txt #requirements for app to run
├── README.md
``` 
## Installation

Ensure you have the following installed:

- SQLite
- Python version 3.12

To install the requirements run:


```bash
  pip install -r requirements.txt
```
    
## Run Locally

To run the app:

```bash
  python app.py
```



## Running Tests

To run tests, run the following command

```bash
  python test.py
```

