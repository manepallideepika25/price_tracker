import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import time

def get_product_info(url):
    """Scrapes the product page and returns the product name and price."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    
    response = None
    retries = 3
    for i in range(retries):
        try:
            print(f"Attempting to fetch URL (attempt {i+1}/{retries})...")
            response = requests.get(url, headers=headers, timeout=20) # Increased timeout
            response.raise_for_status()
            print("Successfully fetched URL.")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if i < retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All retries failed.")
                raise e

    if response is None:
        raise ValueError("Failed to get a valid response from the server.")

    soup = BeautifulSoup(response.content, "html.parser")

    # Logic for Amazon
    if "amazon" in url:
        product_name_element = soup.select_one("#productTitle")
        if not product_name_element:
            product_name_element = soup.select_one("#title")
        
        if product_name_element:
            product_name = product_name_element.get_text(strip=True)
        else:
            raise ValueError("Could not find product title on Amazon")

        price_element = soup.select_one(".a-price-whole")
        if price_element:
            price_str = price_element.get_text(strip=True).replace(',', '').replace('.', '')
            price = float(price_str)
        else:
            raise ValueError("Could not find product price on Amazon")

    # Logic for Flipkart
    elif "flipkart" in url:
        product_name_element = soup.select_one("span.B_NuCI")
        if product_name_element:
            product_name = product_name_element.get_text(strip=True)
        else:
            raise ValueError("Could not find product title on Flipkart")

        price_element = soup.select_one("div._30jeq3._16Jk6d")
        if price_element:
            price_str = price_element.get_text(strip=True).replace('₹', '').replace(',', '')
            price = float(price_str)
        else:
            raise ValueError("Could not find product price on Flipkart")
    
    else:
        raise ValueError(f"Unsupported website for scraping: {url}")

    return product_name, price

def send_email(receiver_email, product_name, product_price, product_url):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("Error: SENDER_EMAIL and SENDER_PASSWORD environment variables are not set.")
        return

    subject = f"Price Drop Alert for {product_name}"
    body = f"The price of {product_name} has dropped to {product_price}.\n\nBuy it now at: {product_url}"

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print(f"Email sent to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")