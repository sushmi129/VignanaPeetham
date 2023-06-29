from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from flask import  g
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from base64 import b64encode
from datetime import timedelta

app = Flask(__name__, static_url_path='/static', static_folder='static')

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'Vignan_ShPbV_801')

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

def add_entry(name, classNum, FatherName, MotherName, Address, Mobile, AdharNum):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        x = (name, classNum, FatherName, MotherName, Address, Mobile, AdharNum)
        insert = """INSERT INTO Admission (STUDENT, CLASS, FATHER, MOTHER, ADDRESS, NUMBER, AADHAR) VALUES (?,?,?,?,?,?,?);"""
        c.execute(insert, x)
    finally:
        con.commit()
        c.close()
        con.close()

def get_entry():
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        records = c.execute("SELECT * FROM Admission ORDER BY CLASS, STUDENT;").fetchall()
        columns = ["Name of the Student", 'Class', 'Name of the Father', 'Name of the Mother', 'Address', 'Mobile Number', 'Aadhar Number']
    finally:
        con.commit()
        c.close()
        con.close()
    return records, columns

def search_entry(id):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        sql_select_query = "select * from Admission where AADHAR = ? ORDER BY CLASS, STUDENT;"
        c.execute(sql_select_query, (id,))
        record = c.fetchall()
    finally:
        c.close()
        con.close()
    return record

def update_entry(name, classNum, FatherName, MotherName, Address, Mobile, AadharChanged, AadharNum):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        x = name, classNum, FatherName, MotherName, Address, Mobile, AadharChanged, AadharNum
        update = "UPDATE Admission SET STUDENT = ?, CLASS = ?, FATHER = ?, MOTHER = ?, ADDRESS = ? ,NUMBER  = ?, AADHAR = ? WHERE AADHAR = ?;"
        c.execute(update, x)
    finally:
        con.commit()
        c.close()
        con.close()

def delete_entry(aadhar):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        delete = "DELETE FROM Admission WHERE AADHAR = ?;"
        c.execute(delete, (aadhar,))
    finally:
        con.commit()
        c.close()
        con.close()

def get_image(tableName):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        records = c.execute("SELECT * FROM " + "T" + str(tableName)).fetchall()
        images = []
        for record in records:
            x = b64encode(record[1])
            images.append([record[0], x.decode("UTF-8")])
    finally:
        con.commit()
        c.close()
        con.close()
    return images
       
def get_events():
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        records = c.execute("SELECT * FROM Gallery ORDER BY ID desc").fetchall()
    finally:
        con.commit()
        c.close()
        con.close()
    return records

class event_login:
    login = False
    def user_in(self):
        self.login = True
    def user_out(self):
        self.login = False
    def get_user(self):
        return self.login
elogin = event_login()

@app.route('/')
@app.route('/home')
def home():
    return render_template("Home.html")

@app.route('/about')
def about():
    return render_template("AboutUs.html")

@app.route('/management')
def management():
    return render_template("Management.html")

@app.route('/gallery')
def gallery():
    events = get_events()
    galleryContent = []
    for event in events:
        images = get_image(event[0])
        galleryContent.append([event[0], event[1], images])
    return render_template("Gallery.html", login=elogin.get_user(), galleryContent=galleryContent)

@app.route('/donations')
def donations():
    return render_template("Donations.html")

@app.route('/admissions')
def admissions():
    if elogin.get_user():
        records, columns = get_entry()
        return render_template("Admissions.html", columns=columns, records=records, login=True)
    return render_template('Admissions.html', login=False)

@app.route('/contact')
def contact():
    return render_template("Home.html", scroll = 'sec-9fc1')

@app.route('/developers')
def developers():
    return render_template("Developers.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    database = {'UserName': 'PassWord'}
    if request.method == 'POST':
        name1 = request.form['uname']
        pwd = request.form['psw']
        if name1 in database:
            if database[name1] != pwd:
                return render_template('Admissions.html', info='Invalid Password')
            else:
                user = User(name1)
                login_user(user)
                elogin.user_in()
                return redirect(url_for('admissions'))
        else:
            return render_template('Admissions.html', info='Invalid User')
    return render_template('Admissions.html')

@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        classNum = request.form['class']
        FatherName = request.form['fatherName']
        MotherName = request.form['motherName']
        Address = request.form['Address']
        Mobile = request.form['Mobile']
        AadharNum = request.form['aadhar']
        if len(AadharNum) != 12:
            flash("Invalid Aadhar Number")
        else:
            add_entry(name, classNum, FatherName, MotherName, Address, Mobile, AadharNum)
        return redirect(url_for("admissions"))
    return render_template("AdADD.html")

@app.route("/search", methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        num = request.form['aadhar']
        record = search_entry(num)
        if len(record) == 0:
            return render_template("AdSearch.html", notFound=True)
        else:
            return render_template("AdSearch.html", found=True, records=record)
    return render_template("AdSearch.html")

@app.route("/edit/<int:aadhar>", methods=['POST', 'GET'])
@login_required
def edit(aadhar):
    if request.method == 'POST':
        name = request.form['name']
        classNum = request.form['class']
        FatherName = request.form['fatherName']
        MotherName = request.form['motherName']
        Address = request.form['Address']
        Mobile = request.form['Mobile']
        AadharChanged = request.form['aadharChanged']
        update_entry(name, classNum, FatherName, MotherName, Address, Mobile, AadharChanged, AadharNum=aadhar)
        return redirect(url_for("admissions"))
    return render_template("AdEdit.html", record=search_entry(aadhar))

@app.route("/delete/<int:aadhar>", methods=['POST', 'GET'])
@login_required
def delete(aadhar):
    delete_entry(aadhar)
    return redirect(url_for("admissions"))

@app.route("/addImage/<IDT>", methods=['POST', 'GET'])
@login_required
def addImage(IDT):
    if request.method == 'POST':
        img = request.files['img']
        img = img.read()
        con = sqlite3.connect("Vignan.db")
        c = con.cursor()
        try:
            insert = """INSERT INTO """ + "T" + str(IDT) + """ (IMAGE) VALUES (?);"""
            c.execute(insert, (img,))
        finally:
            con.commit()
            c.close()
            con.close()
        return redirect(url_for('gallery'))
    return render_template("AddImage.html", IDT=IDT)
    
@app.route("/create", methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        con = sqlite3.connect("Vignan.db")
        c = con.cursor()
        try:
            insert = """INSERT INTO Gallery (Name) VALUES (?);"""
            c.execute(insert, (name,))
            idEvent = c.execute("SELECT MAX(ID) FROM Gallery").fetchall()
            c.execute("""CREATE TABLE '""" + "T" + str(idEvent[0][0]) + """' ("ID"	INTEGER, "IMAGE"	BLOB NOT NULL, PRIMARY KEY("ID" AUTOINCREMENT))""")
        finally:
            con.commit()
            c.close()
            con.close()
        return redirect(url_for('gallery'))
    return render_template("createEvent.html")

@app.route("/delImage/<IDT>/<imgDel>", methods=['POST', 'GET'])
@login_required
def delImage(IDT, imgDel):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        delete = "DELETE FROM " + "T" + str(IDT) + " WHERE ID = ?;"
        c.execute(delete, (imgDel,))
    finally:
        con.commit()
        c.close()
        con.close()
    return redirect(url_for("gallery"))

@app.route("/delImage/<IDT>", methods=['POST', 'GET'])
@login_required
def delEvent(IDT):
    con = sqlite3.connect("Vignan.db")
    c = con.cursor()
    try:
        delete = "Drop Table " + "T" + str(IDT) + " ;"
        c.execute(delete)
        delete = "DELETE FROM Gallery WHERE ID = ?;"
        c.execute(delete, (IDT,))
    finally:
        con.commit()
        c.close()
        con.close()
    return redirect(url_for("gallery"))

@app.route('/logout')
def logout():
    logout_user()
    elogin.user_out()
    return redirect(url_for('admissions'))

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True
    g.user = current_user

if __name__ == '__main__':
    app.run(debug=True)
