from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import os
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["MONGO_URI"] = "mongodb+srv://user1:sample1@sample.ofxan.mongodb.net/myDatabase"
mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one({'username': request.form['username']})
        if existing_user is None:
            hashed_password = generate_password_hash(request.form['password'])
            mongo.db.users.insert_one({'username': request.form['username'], 'password': hashed_password})
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        flash('Username already exists', 'error')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('profile.html', user=user)


@app.route('/create-portfolio')
def create_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('create_portfolio.html')


@app.route('/save-portfolio', methods=['POST'])
def save_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    portfolio_data = request.json
    user_id = ObjectId(session['user_id'])

    portfolio_id = mongo.db.portfolios.insert_one({
        'user_id': user_id,
        'content': portfolio_data
    }).inserted_id

    return {'success': True, 'portfolio_id': str(portfolio_id)}


@app.route('/portfolio/<username>/<portfolio_id>')
def view_portfolio(username, portfolio_id):
    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})
    if portfolio:
        return render_template('view_portfolio.html', portfolio=portfolio)
    return "Portfolio not found", 404


@app.route('/preview-portfolio', methods=['POST'])
def preview_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    portfolio_data = request.json
    return render_template('preview.html', portfolio=portfolio_data)


@app.route('/my-portfolios')
def my_portfolios():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    portfolios = list(mongo.db.portfolios.find({'user_id': user_id}))

    return render_template('my_portfolios.html', portfolios=portfolios)

@app.route('/save-portfolio', methods=['POST'])
def save_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    portfolio_data = request.json
    user_id = ObjectId(session['user_id'])

    portfolio_id = mongo.db.portfolios.insert_one({
        'user_id': user_id,
        'content': portfolio_data
    }).inserted_id

    # Redirecting to "My Portfolios" page after saving
    return {'success': True, 'redirect_url': url_for('my_portfolios')}


@app.route('/edit-portfolio/<portfolio_id>', methods=['GET', 'POST'])
def edit_portfolio(portfolio_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})

    if request.method == 'POST':
        updated_data = request.json
        mongo.db.portfolios.update_one({'_id': ObjectId(portfolio_id)}, {'$set': {'content': updated_data}})
        return {'success': True, 'redirect_url': url_for('my_portfolios')}

    return render_template('edit_portfolio.html', portfolio=portfolio)

if __name__ == '__main__':
    app.run(debug=True)
