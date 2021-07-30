from flask import Flask,render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import ssl 
import pymysql as sql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass

app = Flask(__name__)
app.secret_key = "eifjijfpijpojijiji980200uuehohfooij0939"

def db_connect():
    db = sql.connect(host="localhost", port=3306, database="flask_project", user="root",password="")
    cursor = db.cursor()
    return db, cursor

def read_data():
    book = pd.read_csv("E:\Grras_Data\Data_Science\Project\Flask_Project\Komal_Work\Books100.csv")
    book.drop("Unnamed: 0", axis=1, inplace=True)
    return book 

@app.route("/")
def index():
    book = read_data()
    aut = []
    gen = []
    for i in book['author']:
        aut.extend(i.split(","))
    aut = pd.Series(aut).unique()
    book['genre'] = book['genre'].fillna('')
    for i in book['genre']:
        gen.extend(i.split(","))
    gen = pd.Series(gen).unique()
    tit = list(book['title'].unique())
    return render_template('index.html', aut=aut, gen=gen, tit=tit)


@app.route("/aftersubmit/", methods=['GET', 'POST'])
def aftersubmit():
    if request.method == "GET":
        return redirect(url_for("index"))
        #return render_template("form.html")
    else:
        email = request.form.get("email")
        author = request.form.get("author")
        genre = request.form.get("genre")
        title = request.form.get("title")
        data = read_data()
        temp = data.copy()
        print(author, genre, title)
        temp['genre'] = temp['genre'].fillna('')
        temp['title'] = temp['title'].fillna('')
        #temp['title'] = temp['title'].apply(lambda x: "".join(x.split()))
        if author:
            temp = temp[temp['author'].apply(lambda x:True if author in x else False)]
        if genre:
            temp = temp[temp['genre'].apply(lambda x:True if genre in x else False)]
        if title:
            temp = temp[temp['title'] == title]
            #temp = temp[temp['title'].apply(lambda x:True if title in x else False)]
        temp = temp[['author','title','desc','genre','rating','img','link']]
        #return f"{temp}"
        #return temp.to_html()
        #return render_template(temp.to_html())
        # temp1 = temp.to_dict()
        # for i in temp1.items():
        #     for key,val in i[1].items():
        #         print(i[0], "-->",val)
        temp2 = temp.T.to_dict('list')
        l = []
        for i in temp2.keys():
            l.append(dict(zip(temp.columns,temp2[i])))
        k = pd.Series(l).to_dict()
        # for i in l:
        #     print(i)
        db, cursor = db_connect()
        cmd = f"insert into users (Email) values('{email}')"
        cursor.execute(cmd)
        db.commit()
        cmd = f"select * from users where email='{email}'"
        cursor.execute(cmd)
        if cursor.fetchone():
            msg = MIMEMultipart()
            msg['To'] = email
            msg['From'] = "komalverma0506@gmail.com"
            msg['Subject'] = "Mail Regarding Searched Book with ReadersParadise"

            mail = "komalverma0506@gmail.com"
            password = "Komhul270506!"

            html = temp.to_html()

            h = MIMEText(html, "html")
            # p is a object of MIMEText which will define the type of the data you are sending and 
            # the data you are sending

            msg.attach(h)  # add p in body part

            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(mail, password)
                    server.sendmail(mail, email, msg.as_string())
            except Exception as err:
                return ("Error --> ", err)
            else:
                msg1 = "Message Regarding Your Searched Book has been Successfully Send...Please check your mail"
        #return (temp.to_html(), msg1)
        #return temp
        #return temp.to_dict()
        return render_template("result.html", data=k)




app.run(debug=True)
