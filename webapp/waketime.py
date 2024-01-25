from flask import Flask
import dictToObj
import json
import formBuilder

app = Flask(__name__)

@app.route("/")
def form():
    return formBuilder.build_form()
