from flask import Flask
import dictToObj
import json
import formBuilder

app = Flask(__name__)

@app.route("/grid")
def grid(computer):
    return formBuilder.build_grid(computer)

@app.route("/set_active")
def set_active(name):
    data = formBuilder.getData()
    
