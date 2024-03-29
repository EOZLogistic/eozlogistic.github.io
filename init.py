#sudo service apache2 restart
import sys
import os
from flask import Flask, render_template,request, jsonify,redirect,url_for,jsonify,flash
import mysql.connector as mysql
from werkzeug.utils import secure_filename
import urllib.request
from datetime import datetime
import glob, os
import json
db = mysql.connect(
	host = "localhost",
	user = "root",
	passwd = open("/var/www/html/password.txt", "r").read(),
	database = "logistic"
)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app = Flask(__name__)
@app.route('/parcel')
def parcel():
	cursor = db.cursor(buffered=True)
	cursor.execute('SELECT * from requests;')
	temp=''
	for row in cursor.fetchall():
		temp+='列列'.join(row)+'行行'
	cursor.close()
	return render_template('parcel.html',result=temp)
@app.route('/parcel<id>')
def parcelid(id):
	cursor = db.cursor(buffered=True)
	cursor.execute('SELECT * from requests;')
	temp=''
	for row in cursor.fetchall():
		temp+='列列'.join(row)+'行行'
	cursor.close()
	return render_template('parcel.html',result=temp,id=id)
@app.route('/')
def index():
	f = open("/var/www/html/data.json", "r")
	return render_template('index.html',result=f.read().replace("\n", ""))
@app.route('/api')
def api():
	f = open("/var/www/html/data.json", "r")
	response = jsonify(json.loads(f.read()))
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response
@app.route('/api<id>')
def apiid(id):
	f = open("/var/www/html/data.json", "r")
	response = jsonify(json.loads(f.read())[id])
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response
@app.route('/update',methods=['POST'])
def update():
	with open("/var/www/html/data.json", "w") as text_file:
		text_file.write(request.form['json'])
	return jsonify({'result':'update successfully'})
@app.route('/update<id>')
def updateid(id):
	cursor = db.cursor()
	cursor.execute("UPDATE requests SET status=%s WHERE id=%s",(str(datetime.now()),id))
	db.commit()
	cursor.close()
	return jsonify({'result':'update successfully'})
@app.route('/$upload<id>', methods=['POST'])
def upload_file(id):
	if 'files[]' not in request.files:
		return jsonify({'result':'No file part in the request'})
	files = request.files.getlist('files[]')
	file=files[0]
	if file and allowed_file(file.filename):
		filename=id+'.'+secure_filename(file.filename).rsplit('.', 1)[1].lower()
		file.save(os.path.join(r'/var/www/html/static', filename))
		with open('/var/www/html/data.json', 'r+') as f:
			data = json.load(f)
			data[id]['Image'] =  filename
			f.seek(0)
			json.dump(data, f, indent=4)
			f.truncate()
		return jsonify({'result':filename})
	else:
		return jsonify({'result':'File type is not allowed'})
@app.route('/insert<id>')
def insert(id):
	cursor = db.cursor()
	cursor.execute("INSERT INTO requests (id,date,status) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE date=VALUES(date),status=VALUES(status);",(id,str(datetime.now()),''))
	db.commit()
	cursor.close()
	return redirect(url_for('parcel'))
if __name__ == "__main__":
	app.run()