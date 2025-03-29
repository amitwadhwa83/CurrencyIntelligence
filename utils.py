import pandas as pd
from datetime import datetime
from currency_api import get_exchange_rates, get_historical_rates

def calculate_gain_loss(base_currency, target_currency, amount, past_date, current_date):
    """
    Calculate potential gain or loss if currency was converted on a past date vs. now.
    
    Args:
        base_currency (str): The base currency code
        target_currency (str): The target currency code
        amount (float): The amount in base currency
        past_date (str): Past date in YYYY-MM-DD format
        current_date (str): Current date in YYYY-MM-DD format
        
    Returns:
        tuple: (past_rate, current_rate, past_value, current_value, absolute_change, percentage_change)
            or None if calculation fails
    """
    try:
        # Get historical rate for the past date
        historical_rates = get_historical_rates(
            base_currency,
            target_currency,
            past_date,
            past_date
        )
        
        if not historical_rates or past_date not in historical_rates:
            print(f"Historical rate not available for {past_date}")
            return None
            
        past_rate = historical_rates[past_date]
        
        # Get current exchange rate
        current_rates = get_exchange_rates(base_currency)
        if not current_rates or target_currency not in current_rates:
            print(f"Current rate not available for {target_currency}")
            return None
            
        current_rate = current_rates[target_currency]
        
        # Calculate values
        past_value = amount * past_rate
        current_value = amount * current_rate
        
        absolute_change = current_value - past_value
        percentage_change = (absolute_change / past_value) * 100
        
        return (past_rate, current_rate, past_value, current_value, absolute_change, percentage_change)
    
    except Exception as e:
        print(f"Exception in calculate_gain_loss: {e}")
        return None

def get_currency_list():
    """
    Get a list of supported currencies.
    
    Returns:
        list: List of currency codes
    """
    # Common currencies
    return [
        "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", 
        "HKD", "NZD", "SEK", "NOK", "SGD", "MXN", "INR", "BRL", 
        "ZAR", "RUB", "TRY", "HUF", "PLN"
    ]

def get_currency_full_names():
    """
    Get a mapping of currency codes to full names.
    
    Returns:
        dict: Dictionary mapping currency codes to full names
    """
    return {
        "USD": "United States Dollar",
        "EUR": "Euro",
        "GBP": "British Pound Sterling",
        "JPY": "Japanese Yen",
        "CAD": "Canadian Dollar",
        "AUD": "Australian Dollar",
        "CHF": "Swiss Franc",
        "CNY": "Chinese Yuan",
        "HKD": "Hong Kong Dollar",
        "NZD": "New Zealand Dollar",
        "SEK": "Swedish Krona",
        "NOK": "Norwegian Krone",
        "SGD": "Singapore Dollar",
        "MXN": "Mexican Peso",
        "INR": "Indian Rupee",
        "BRL": "Brazilian Real",
        "ZAR": "South African Rand",
        "RUB": "Russian Ruble",
        "TRY": "Turkish Lira",
        "HUF": "Hungarian Forint",
        "PLN": "Polish Złoty"
    }
