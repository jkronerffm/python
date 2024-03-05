from flask import Flask, redirect, request, render_template

app = Flask(__name__)
tabs = {
	"Home": { 
		"attr": "home", 
		"href": "/"
	}, 
	"Radio": {
		"attr": "tab1", 
		"href": "/radio"
	}, 
	"Wecker": {
		"attr": "tab2", 
		"href": "/waketime"
	}, "Sound": {
		"attr": "tab3", 
		"href": "/sound"
	},
	"Sonstiges": {
		"attr": "tab4", 
		"href": "/misc"
	}
}

@app.route("/")
def index():
	return render_template('index.html', title='Radio', tabs=tabs, active="home",  header="Radio")

@app.route("/radio")
def doRadio():
	return render_template('radio.html', title='Radio', tabs=tabs, active="tab1", header="Radiosender")
	
@app.route("/waketime")
def doWaketime():
	return render_template("waketime.html", title="Wecker", tabs=tabs, active="tab2", header="Wecker")

@app.route("/sound")
def doSound():
	return render_template("sound.html", title="Sound", tabs=tabs, active="tab3", header="Sound")

@app.route("/misc")
def doMisc():
	return render_template("misc.html", title="Sonstiges", tabs=tabs, active="tab4", header="Sonstiges")
	
if __name__ == "__main__":
	app.run(debug=TRUE, port="7000")
