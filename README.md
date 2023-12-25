# Grocery_Store_Project
A website for ordering Groceries online.

For running this application -
- First create a python virtual evironment.
python -m venv venvironment     # run this command in windows command prompt

- Then download the required packages from requirements.txt file.
pip install -r requirements.txt    # run this command in windows command prompt

- After downloads run the app.py file which lets your application to run. 
python app.py     # run this command in windows command prompt


Application folder contains -
- controllers.py (defines controllers)
- database.py (defines db object)
- models.py (defines database models)
- api.py (defines APIs), 
- config.py (defines configuration), 
- forms.py (defines forms), 
- validation.py (defines validation classes for api’s), 
- login_manager.py (init login_manager object) files.
All the required files are imported in app.py which render html templates from templates folder and css from static folder.

Technologies Used-
-	Backend: Python, Flask
- Database: SQLite3
-	Frontend: HTML, CSS, Bootstrap
-	Flask Extensions: Flask-SQLAlchemy, Flask-WTF, Flask-Bcrypt
-	RESTAPI: Flask-RESTful
-	Authentication: Flask-Login, Flask_httpauth
