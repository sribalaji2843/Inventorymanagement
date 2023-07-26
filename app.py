from flask import Flask, render_template, request, redirect, url_for
import sqlite3
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
def initialize_database():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Product ( product_id INTEGER PRIMARY KEY, product_name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Location ( location_id INTEGER PRIMARY KEY,location_name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ProductMovement (movement_id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL,from_location INTEGER, to_location INTEGER, product_id INTEGER,qty INTEGER NOT NULL, FOREIGN KEY (from_location) REFERENCES Location(location_id),FOREIGN KEY (to_location) REFERENCES Location(location_id), FOREIGN KEY (product_id) REFERENCES Product(product_id))''')
    conn.commit()
    conn.close()
initialize_database()
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_name = request.form['product_name']
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('INSERT INTO Product (product_name) VALUES (?)', (product_name,))
        conn.commit()
        conn.close()
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Product')
    products = c.fetchall()
    conn.close()
    return render_template('products.html', products=products)
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        location_name = request.form['location_name']
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('INSERT INTO Location (location_name) VALUES (?)', (location_name,))
        conn.commit()
        conn.close()
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Location')
    locations = c.fetchall()
    conn.close()
    return render_template('locations.html', locations=locations)
@app.route('/movements', methods=['GET', 'POST'])
def movements():
    if request.method == 'POST':
        timestamp = request.form['timestamp']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        product_id = request.form['product_id']
        qty = request.form['qty']
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('''INSERT INTO ProductMovement (timestamp, from_location, to_location, product_id, qty) VALUES (?, ?, ?, ?, ?)''', (timestamp, from_location, to_location, product_id, qty))
        conn.commit()
        conn.close()
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT ProductMovement.movement_id, timestamp, from_location, to_location, Product.product_name, qty FROM ProductMovement LEFT JOIN Product ON ProductMovement.product_id = Product.product_id''')
    movements = c.fetchall()
    conn.close()
    return render_template('movements.html', movements=movements)
def calculate_balance_qty(location_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT SUM(CASE WHEN from_location = ? THEN -qty ELSE qty END) as balance_qty FROM ProductMovement WHERE from_location = ? OR to_location = ?''', (location_id, location_id, location_id))
    balance_qty = c.fetchone()[0]
    conn.close()
    return balance_qty
@app.route('/report')
def report():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Location')
    locations = c.fetchall()
    conn.close()
    report_data = []
    for location in locations:
        location_id, location_name = location
        balance_qty = calculate_balance_qty(location_id)
        report_data.append((location_name, balance_qty))

    return render_template('report.html', report_data=report_data)
if __name__ == '__main__':
    app.run(debug=True)