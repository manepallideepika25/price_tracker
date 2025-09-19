import requests
from bs4 import BeautifulSoup
import smtplib
import database

# --- CONFIGURATION ---
# Your email credentials for sending alerts
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "YOUR_APP_PASSWORD"
RECEIVER_EMAIL = "receiver_email@example.com"

# The User-Agent header helps mimic a real browser request.
HEADERS = {
    "User-Agent": "Your User Agent Here"
}

def send_email(product, price):
    """Sends an email alert."""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) # Adjust for your email provider
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        subject = f"Price Drop Alert! Price for {product['url']} is now ${price}"
        body = f"The price of the product at {product['url']} has dropped to ${price}. Buy it now!"
        msg = f"Subject: {subject}\r\n\r\n{body}"

        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg)
        print(f"Email alert sent for {product['url']}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        if 'server' in locals() and server:
            server.quit()

def get_price_from_url(url):
    """Scrapes the product page and returns the current price."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # --- Website-Specific Price Extraction Logic ---
        # This is where you need to add your custom logic for each website.
        # You can use if/elif statements to check the domain of the URL.

        if "amazon.com" in url:
            price_element = soup.find(id="priceblock_ourprice")
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = float(price_text.replace('$', '').replace(',', ''))
                return price

        # Add more elif blocks for other websites here
        # elif "walmart.com" in url:
        #     # Add Walmart-specific scraping logic
        #     pass

        else:
            print(f"No specific scraping logic for {url}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during request for {url}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return None

def check_price(product):
    """Checks the price of a single product and sends an alert if needed."""
    price = get_price_from_url(product['url'])

    if price:
        database.update_price(product['id'], price)
        if price < product['threshold_price']:
            print(f"Price for {product['url']} has dropped to ${price}. Sending email.")
            send_email(product, price)
        else:
            print(f"Price for {product['url']} is ${price}, which is not below the threshold.")
    else:
        print(f"Could not retrieve the price for {product['url']}.")
