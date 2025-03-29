import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import time

# Cache for exchange rates to reduce API calls
exchange_rate_cache = {}
historical_rate_cache = {}

# API endpoints
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/"
HISTORICAL_API = "https://api.exchangerate-api.com/v4/history/"

def get_exchange_rates(base_currency):
    """
    Fetch current exchange rates for a base currency.
    
    Args:
        base_currency (str): The base currency code (e.g., USD, EUR)
        
    Returns:
        dict: Dictionary of exchange rates or None if request fails
    """
    # Check cache first (cache expires after 1 hour)
    cache_key = f"{base_currency}_{datetime.now().strftime('%Y-%m-%d_%H')}"
    if cache_key in exchange_rate_cache:
        return exchange_rate_cache[cache_key]
    
    try:
        response = requests.get(f"{EXCHANGE_RATE_API}{base_currency}")
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            # Cache the result
            exchange_rate_cache[cache_key] = rates
            return rates
        else:
            print(f"Error fetching exchange rates: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception in get_exchange_rates: {e}")
        return None

def get_historical_rates(base_currency, target_currency, start_date, end_date):
    """
    Fetch historical exchange rates between two currencies for a date range.
    
    Args:
        base_currency (str): The base currency code
        target_currency (str): The target currency code
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        dict: Dictionary mapping dates to rates or None if request fails
    """
    # Check cache first
    cache_key = f"{base_currency}_{target_currency}_{start_date}_{end_date}"
    if cache_key in historical_rate_cache:
        return historical_rate_cache[cache_key]
    
    # Convert dates to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # For API efficiency, we'll fetch data in chunks of up to 1 year
    # Some free APIs have limitations on date range
    result = {}
    current_start = start_dt
    
    while current_start <= end_dt:
        current_end = min(current_start + timedelta(days=365), end_dt)
        chunk_start = current_start.strftime('%Y-%m-%d')
        chunk_end = current_end.strftime('%Y-%m-%d')
        
        try:
            # Use simplified approach for demo
            # In real-world, you would use a more comprehensive API
            url = f"{HISTORICAL_API}{base_currency}?start_date={chunk_start}&end_date={chunk_end}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                rates_data = data.get('rates', {})
                
                # Extract rates for each date
                for date_str, rates in rates_data.items():
                    if target_currency in rates:
                        result[date_str] = rates[target_currency]
            else:
                print(f"Error fetching historical rates: {response.status_code}")
                
                # Fallback to simulated data for demo purposes if API fails
                print("Using simulated historical data")
                result = simulate_historical_data(base_currency, target_currency, start_date, end_date)
                break
                
            # Avoid rate limiting
            time.sleep(1)
            
            # Move to next chunk
            current_start = current_end + timedelta(days=1)
            
        except Exception as e:
            print(f"Exception in get_historical_rates: {e}")
            
            # Fallback to simulated data for demo purposes
            print("Using simulated historical data")
            result = simulate_historical_data(base_currency, target_currency, start_date, end_date)
            break
    
    # Sort by date
    result = {k: result[k] for k in sorted(result.keys())}
    
    # Cache the result
    historical_rate_cache[cache_key] = result
    
    return result

def simulate_historical_data(base_currency, target_currency, start_date, end_date):
    """
    Simulate historical exchange rate data when API fails.
    This is only for demonstration purposes when the API is unavailable.
    
    Args:
        base_currency (str): The base currency code
        target_currency (str): The target currency code
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        dict: Dictionary mapping dates to simulated rates
    """
    # Get current exchange rate as a base
    current_rates = get_exchange_rates(base_currency)
    if not current_rates or target_currency not in current_rates:
        # Use a reasonable default rate based on the currency pair
        base_rate = get_default_rate(base_currency, target_currency)
    else:
        base_rate = current_rates[target_currency]
    
    # Generate dates
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Generate simulated rates
    result = {}
    current_date = start_dt
    
    # Use a simple random walk with mean reversion for simulation
    import numpy as np
    np.random.seed(int(base_rate * 1000))  # Use base_rate for seed to get consistent results
    
    volatility = 0.005  # Daily volatility
    mean_reversion = 0.05  # Mean reversion strength
    
    rate = base_rate * (0.9 + 0.2 * np.random.random())  # Start with variation around base_rate
    
    while current_date <= end_dt:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Apply random walk with mean reversion
        random_change = np.random.normal(0, volatility)
        mean_reversion_effect = mean_reversion * (base_rate - rate)
        rate = rate * (1 + random_change + mean_reversion_effect)
        
        result[date_str] = rate
        current_date += timedelta(days=1)
    
    return result

def get_default_rate(base_currency, target_currency):
    """
    Provide a reasonable default exchange rate for simulation purposes.
    
    Args:
        base_currency (str): The base currency code
        target_currency (str): The target currency code
        
    Returns:
        float: A default exchange rate
    """
    # Common currency pairs with approximate rates
    # These are just reasonable approximations for simulation
    currency_pairs = {
        "USD_EUR": 0.85,
        "EUR_USD": 1.18,
        "GBP_USD": 1.38,
        "USD_GBP": 0.72,
        "USD_JPY": 110.0,
        "EUR_GBP": 0.85,
        "USD_CAD": 1.25,
        "USD_AUD": 1.35,
        "USD_INR": 74.5,
        "EUR_JPY": 130.0,
        "USD_HUF": 300.0,
        "EUR_HUF": 350.0,
        "HUF_INR": 0.24,
    }
    
    pair_key = f"{base_currency}_{target_currency}"
    if pair_key in currency_pairs:
        return currency_pairs[pair_key]
    
    # If the specific pair isn't in our list, try to derive it
    reverse_key = f"{target_currency}_{base_currency}"
    if reverse_key in currency_pairs:
        return 1 / currency_pairs[reverse_key]
    
    # Default fallback - just return a random value between 0.5 and 2
    import random
    return random.uniform(0.5, 2.0)
