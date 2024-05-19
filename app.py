from flask import Flask, render_template, jsonify, request, send_from_directory
import sqlite3
import socket
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    # Drop the existing inventory table if it exists
    c.execute('DROP TABLE IF EXISTS inventory')

    # Create a new inventory table with the updated schema
    c.execute('''CREATE TABLE inventory
                 (id INTEGER PRIMARY KEY, quantity INTEGER, name TEXT, section TEXT)''')
    conn.commit()
    conn.close()
    logging.info("Database initialized and table created.")

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    quantity = data['quantity']
    name = data['name']
    section = data['section']

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('INSERT INTO inventory (quantity, name, section) VALUES (?, ?, ?)',
              (quantity, name, section))
    conn.commit()
    conn.close()

    logging.info(f"Item added: {name}, Quantity: {quantity}, Section: {section}")
    return jsonify({'message': 'Item added successfully'})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM inventory WHERE id = ?', (id,))
    item = c.fetchone()

    if item is None:
        logging.warning(f"Attempt to delete non-existing item with ID: {id}")
        return jsonify({'message': 'Item not found'}), 404

    c.execute('DELETE FROM inventory WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    logging.info(f"Item deleted: ID {id}")
    return jsonify({'message': 'Item deleted successfully'})

@app.route('/get', methods=['GET'])
def get():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM inventory')
    items = c.fetchall()
    conn.close()

    logging.info("Inventory data fetched")
    return jsonify(items)

@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    data = request.json
    fields = []
    values = []

    for key, value in data.items():
        fields.append(f"{key} = ?")
        values.append(value)

    values.append(id)

    set_clause = ", ".join(fields)

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    c.execute('SELECT * FROM inventory WHERE id = ?', (id,))
    item = c.fetchone()
    if item is None:
        logging.warning(f"Attempt to update non-existing item with ID: {id}")
        return jsonify({'message': 'Item not found'}), 404

    c.execute(f'UPDATE inventory SET {set_clause} WHERE id = ?', values)
    conn.commit()
    conn.close()

    logging.info(f"Item updated: ID {id}, Updates: {data}")
    return jsonify({'message': 'Item updated successfully'})

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    local_ip = get_local_ip()
    logging.info(f"Server starting on IP {local_ip}, port 5000")
    app.run(host=local_ip, port=5000, debug=True)
