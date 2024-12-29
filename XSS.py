from flask import Flask, request, render_template_string
from markupsafe import Markup
import sqlite3

app = Flask(__name__, static_url_path='', static_folder='.')

# Veritabanı oluşturma ve örnek veri ekleme
def init_db():
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, image TEXT, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, product_id INTEGER, comment TEXT, FOREIGN KEY(product_id) REFERENCES products(id))''')

    # Resimleri doğrudan ana dizinden al
    c.execute("INSERT OR IGNORE INTO products (id, name, price, image, description) VALUES (1, 'Laptop', 999.99, 'laptop.png', 'High-performance laptop for work and gaming.')")
    c.execute("INSERT OR IGNORE INTO products (id, name, price, image, description) VALUES (2, 'Smartphone', 699.99, 'smartphone.png', 'Latest model smartphone with excellent camera.')")
    c.execute("INSERT OR IGNORE INTO products (id, name, price, image, description) VALUES (3, 'Headphones', 199.99, 'headphone.png', 'Noise-cancelling over-ear headphones.')")

    # Örnek yorumlar ekleme
    c.execute("INSERT OR IGNORE INTO reviews (id, product_id, comment) VALUES (1, 1, 'Great laptop, very fast!')")
    c.execute("INSERT OR IGNORE INTO reviews (id, product_id, comment) VALUES (2, 2, 'Amazing camera quality on this phone.')")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()

    html = '''
    <html>
    <head>
        <title>Store</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                padding: 20px;
                justify-content: center;
            }
            .product {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                text-align: center;
                background: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s;
                width: 300px;
            }
            .product:hover {
                transform: scale(1.05);
            }
            .product img {
                max-width: 100%;
                height: auto;
                border-radius: 5px;
            }
            .product h2 {
                margin-top: 10px;
                font-size: 18px;
            }
            .product p {
                font-size: 16px;
                color: #555;
            }
            .product a {
                display: inline-block;
                margin-top: 10px;
                text-decoration: none;
                color: #007BFF;
            }
            .product a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            {% for product in products %}
            <div class="product">
                <img src="{{ product[3] }}" alt="{{ product[1] }}">
                <h2>{{ product[1] }}</h2>
                <p>${{ product[2] }}</p>
                <a href="/product/{{ product[0] }}">View Details</a>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, products=products)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    conn = sqlite3.connect('store.db')
    c = conn.cursor()

    # Ürün bilgilerini al
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()

    # Yorumları al
    c.execute('SELECT comment FROM reviews WHERE product_id = ?', (product_id,))
    reviews = c.fetchall()

    if request.method == 'POST':
        comment = request.form['comment']
        # Yorumları ekle (XSS'yi aktif hale getiriyoruz)
        c.execute('INSERT INTO reviews (product_id, comment) VALUES (?, ?)', (product_id, comment))
        conn.commit()

    conn.close()

    html = '''
    <html>
    <head>
        <title>{{ product[1] }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }
            .product-details {
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background: white;
                border-radius: 5px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .product-details img {
                max-width: 100%;
                border-radius: 5px;
            }
            .reviews {
                margin-top: 20px;
            }
            .reviews ul {
                list-style-type: none;
                padding: 0;
            }
            .reviews li {
                background: #f9f9f9;
                margin: 5px 0;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .review-form {
                margin-top: 20px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .review-form textarea {
                width: 100%;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            .review-form button {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .review-form button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="product-details">
            <img src="{{ product[3] }}" alt="{{ product[1] }}">
            <h1>{{ product[1] }}</h1>
            <p>${{ product[2] }}</p>
            <p>{{ product[4] }}</p>

            <div class="reviews">
                <h3>Reviews</h3>
                <ul>
                    {% for review in reviews %}
                    <li>{{ review[0]|safe }}</li>  <!-- Burada |safe kullanarak XSS'yi aktif ediyoruz -->
                    {% endfor %}
                </ul>

                <form class="review-form" method="post">
                    <textarea name="comment" placeholder="Leave a comment..."></textarea>
                    <button type="submit">Submit</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, product=product, reviews=reviews)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)
