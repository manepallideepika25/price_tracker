from flask import Flask, render_template, request, redirect, url_for
import database
import scraper
import threading
import schedule
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    products = database.get_all_products()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    url = request.form['url']
    target_price = int(request.form['target_price'])
    email = request.form['email']
    
    try:
        # We get the product info to ensure the URL is valid and scrapable
        # before adding it to the database.
        product_name, _ = scraper.get_product_info(url)
        database.add_product(url, target_price, email)
        print(f"Added product: {product_name}")
    except Exception as e:
        print(f"Could not add product with url {url}. Error: {e}")
        # In a real app, you might want to show an error message to the user.
        
    return redirect(url_for('index'))

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    database.delete_product(product_id)
    return redirect(url_for('index'))

def check_prices():
    # The scheduler runs in a separate thread, so it needs its own app context
    # to use the database and other features of the Flask app.
    with app.app_context():
        products = database.get_all_products()
        print(f"Checking prices for {len(products)} products...")
        for product in products:
            product_id, url, target_price, email = product
            try:
                product_name, current_price = scraper.get_product_info(url)
                if current_price <= target_price:
                    scraper.send_email(email, product_name, current_price, url)
                    print(f"Price for {product_name} is below target. Email sent to {email}.")
                else:
                    print(f"Price for {product_name} ({current_price}) is not below target ({target_price}).")
            except Exception as e:
                print(f"Could not check price for {url}. Error: {e}")

def run_scheduler():
    # Schedule the price check to run every 30 minutes
    schedule.every(30).minutes.do(check_prices)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    database.create_table()
    print("Initialized the database.")

# Start the background scheduler thread.
# The check for WERKZEUG_RUN_MAIN ensures that the scheduler is only started
# in the main Flask process, not in the reloader process during debug mode.
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    print("Started background price checker scheduler.")

if __name__ == '__main__':
    # It is recommended to run the app using the `flask run` command.
    # Running with `python app.py` can cause issues with the reloader
    # and the scheduler running twice.
    app.run(debug=True)
