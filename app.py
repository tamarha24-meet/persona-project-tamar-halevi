from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

config = {
  "apiKey": "AIzaSyC8MDWHfYE65SHfsHVhXviZwC75gW5t4zA",
  "authDomain": "personal-project-8010d.firebaseapp.com",
  "projectId": "personal-project-8010d",
  "storageBucket": "personal-project-8010d.appspot.com",
  "messagingSenderId": "817024080116",
  "appId": "1:817024080116:web:257c25d4c8e84b653726a1",
  "databaseURL" : "https://personal-project-8010d-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'





@app.route('/')
def home():
	user = auth.current_user

	if user == None:
		username = ""
		loged_in = False
	else:
		UID = login_session['user']['localId']
		user = db.child("Users").child(UID).get().val()
		username = user["username"]
		loged_in = True
    
	return render_template("home.html", loged_in = loged_in, username = username)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':

		email = request.form['email'].lower()
		password = request.form['password']
		login_session['email'] = email
		login_session['password'] = password

		try:
			login_session['user'] = auth.sign_in_with_email_and_password(email, password)
			

			return redirect(url_for('home'))
		except:
			return render_template("login.html")

	else:          
		return render_template("login.html")



@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		try:
			email = request.form['email'].lower()
			password = request.form['password']

			login_session['email'] = email
			login_session['password'] = password
			login_session['user'] = auth.create_user_with_email_and_password(email, password)
			login_session['user'] = auth.sign_in_with_email_and_password(email, password)
			user = {"username": request.form['username'], "bio": request.form['bio']}

			UID = login_session['user']['localId']
			db.child("Users").child(UID).set(user)


			return redirect(url_for('home'))

		except:
			return render_template("signup.html")

	else:          
		return render_template("signup.html")
    


@app.route('/profile')
def profile():
	try:
		UID = login_session['user']['localId']
		user_reviews = db.child("Users").child(UID).child("reviews").get().val() 
		print(reviews)   
		return render_template("profile.html", reviews = user_reviews)
	except:
		return redirect(url_for('login'))


@app.route('/reviews')
def reviews():
	try:
		all_reviews = user = db.child("Reviews").get().val()
		return render_template("reviews.html", reviews = all_reviews)
	except:
		all_reviews = {}
		return render_template("reviews.html", reviews = all_reviews)




@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
	current_user = auth.current_user
	if current_user == None:
		return redirect(url_for('login'))

	else:
		if request.method == 'POST':

			try:

				UID = login_session['user']['localId']
				user = db.child("Users").child(UID).get().val()
				username = user["username"]
				review = {"username": username, "title": request.form['title'], "artist":request.form['artist'], "review_text": request.form['review_text'], "ranking": request.form['ranking']}
				db.child("Reviews").push(review)

				db.child("Users").child(UID).child("reviews").push(review)
				return redirect(url_for('reviews'))


			except:
				return render_template("add_review.html")

		else:
			return render_template("add_review.html")

@app.route('/logout')
def logout():
	login_session['user'] = None
	auth.current_user = None
	return redirect(url_for('home'))





if __name__ == '__main__':
    app.run(debug=True)