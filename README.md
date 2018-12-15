# QAns

To run the app you need to have Python3, and the flask library installed.

Navigate to the project's root dir and run:

(for linux:)
````
export FLASK_APP=qans
export FLASK_ENV=development
flask run
````

(fow Windows:)
````
set FLASK_APP=flaskr
set FLASK_ENV=development
flask run
````

(You may run `python -m flask` instead of `flask run` if the latter command isn't found.)

After the local server is running, navigate to `localhost:5000` in a browser to view the app.

Features of the app:
1. A user registration/login system, with permissions for user to just edit/delete their on questions/answers
2. Questions and answers are sorted by timestamp
3. The app uses 0 javascript, all view logic has been implemented through jinja2 templates.
4. A minimaistic, sleek UI using bootstrao CSS.
