import os
import sqlite3

from flask import Flask, request, jsonify, redirect, render_template, g, flash, json

from database import Database

DATABASE = 'test_db.sqlite'

app = Flask(__name__)
app.secret_key = 'My super secret key'


def load_data():
    """Loads and returns the data from the JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'info.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        db = get_db()
        users = Database.get_users(db)
        with open(json_path, 'w') as f:
            users_dict = [dict(zip(['id', 'username', 'occupation'], u)) for u in users]
            json.dump({'users': users_dict}, f)
        with open(json_path, 'r') as f:
            return json.load(f)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Use the application context to initialize the database
with app.app_context():
    conn = get_db()
    try:
        existing_records = Database.get_users(conn)
    except sqlite3.OperationalError:
        Database.populate_database(conn)
    # Load the data into a variable
    info_data = load_data()
    close_db()  # Close the connection

@app.route('/', methods=['GET'])
def home():
    db = get_db()

    users = Database.get_users(db)
    users_dict = [dict(zip(['id', 'username', 'occupation'], u)) for u in users]

    return render_template('index.html', users=users_dict)


@app.route('/get_request/<int:user_id>', methods=['GET'])
def get_request(user_id):
    db = get_db()
    user = Database.get_user(db, user_id)
    return render_template('details_page.html', user=user)


@app.route('/create_user_form', methods=['GET'])
def create_user_form():
    return render_template('create_page.html')


@app.route('/create_user', methods=['POST'])
def create_user():
    db = get_db()
    username = request.form['username']
    occupation = request.form['occupation']
    Database.add_user(db, username, occupation)
    flash('Record added', 'success')
    return redirect('/')


@app.route('/edit_user/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    db = get_db()
    user = Database.get_user(db, user_id)
    return render_template('edit_page.html', user=user)


@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    db = get_db()
    Database.update_user(db, user_id, request.form['occupation'])
    flash('Record updated', 'success')
    return redirect('/')


@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    db = get_db()
    Database.delete_user(db, user_id)
    flash('Record deleted', 'success')
    return redirect('/')


# Route to get all info
@app.route('/info', methods=['GET'])
def get_all_info():
    return jsonify(info_data)


@app.route('/info/<int:record_id>', methods=['GET'])
def get_info_by_id(record_id):
    record = next((item for item in info_data['users'] if item['id'] == record_id), None)
    if record:
        return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)
