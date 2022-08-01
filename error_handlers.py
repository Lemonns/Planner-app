from flask import render_template, request
from main import app

@app.errorhandler(401)
def unauthorized():
    return render_template("unauthorized_error.html")