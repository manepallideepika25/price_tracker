from flask import Flask, render_template, request, redirect, url_for
import database
import scraper
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# --- Routes ---

@app.route('/')
def index():
    products = database.get_all_products()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    url = request.form.get('url')
    threshold_price = float(request.form.get('threshold_price'))
    
    if url and threshold_price:
        database.add_product(url, threshold_price)
    
    return redirect(url_for('index'))

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    database.delete_product(product_id)
    return redirect(url_for('index'))

# --- Background Scheduler ---

def check_prices_job():
    """Job to check prices of all products."""
    print("Running price check job...")
    products = database.get_all_products()
    for product in products:
        scraper.check_price(product)

if __name__ == '__main__':
    # Initialize the database
    database.init_db()
    
    # Start the background scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_prices_job, 'interval', minutes=30)
    scheduler.start()
    
    # Run the Flask app
    app.run(debug=True)