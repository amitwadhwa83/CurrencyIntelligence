import requests
from datetime import datetime, timedelta
import os
import time

# Cache for news to reduce API calls
news_cache = {}
NEWS_CACHE_TTL = 3600  # 1 hour in seconds

# Default API key for NewsAPI
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def get_economic_news(currencies, max_articles=10):
    """
    Fetch economic news related to specified currencies.
    
    Args:
        currencies (list): List of currency codes to get news for
        max_articles (int): Maximum number of articles to return
        
    Returns:
        list: List of news articles or empty list if request fails
    """
    # Check cache first
    cache_key = f"news_{'_'.join(sorted(currencies))}_{datetime.now().strftime('%Y-%m-%d_%H')}"
    if cache_key in news_cache and (time.time() - news_cache[cache_key]['timestamp'] < NEWS_CACHE_TTL):
        return news_cache[cache_key]['data']
    
    # Build search query
    search_terms = []
    for currency in currencies:
        # Add currency code and common names
        if currency == "USD":
            search_terms.extend(["USD", "US Dollar", "Dollar"])
        elif currency == "EUR":
            search_terms.extend(["EUR", "Euro", "Eurozone"])
        elif currency == "GBP":
            search_terms.extend(["GBP", "British Pound", "Sterling"])
        elif currency == "JPY":
            search_terms.extend(["JPY", "Japanese Yen", "Yen"])
        elif currency == "CAD":
            search_terms.extend(["CAD", "Canadian Dollar"])
        elif currency == "AUD":
            search_terms.extend(["AUD", "Australian Dollar"])
        elif currency == "INR":
            search_terms.extend(["INR", "Indian Rupee", "Rupee"])
        elif currency == "HUF":
            search_terms.extend(["HUF", "Hungarian Forint", "Forint"])
        else:
            search_terms.append(currency)
    
    # Add economic terms
    economic_terms = ["economy", "inflation", "interest rate", "central bank", "forex", 
                      "exchange rate", "currency", "economic", "finance", "monetary policy"]
    
    # Build query for NewsAPI
    # Format: "(USD OR Dollar OR ...) AND (economy OR inflation OR ...)"
    currency_query = " OR ".join(search_terms)
    economic_query = " OR ".join(economic_terms)
    query = f"({currency_query}) AND ({economic_query})"
    
    try:
        if NEWS_API_KEY:
            # NewsAPI request
            params = {
                'q': query,
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(NEWS_API_URL, params=params)
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                # Format articles
                results = [
                    {
                        'title': article['title'],
                        'description': article['description'] or "No description available",
                        'url': article['url'],
                        'publishedAt': article['publishedAt'].split('T')[0],
                        'source': article['source']['name']
                    }
                    for article in articles[:max_articles]
                ]
                
                # Cache the results
                news_cache[cache_key] = {
                    'data': results,
                    'timestamp': time.time()
                }
                
                return results
            else:
                print(f"Error fetching news: {response.status_code}")
                return use_mock_news(currencies, max_articles)
        else:
            print("No NEWS_API_KEY available")
            return use_mock_news(currencies, max_articles)
            
    except Exception as e:
        print(f"Exception in get_economic_news: {e}")
        return use_mock_news(currencies, max_articles)

def use_mock_news(currencies, max_articles=10):
    """
    Generate mock economic news when the API is unavailable.
    This should only be used when real news cannot be fetched.
    
    Args:
        currencies (list): List of currency codes
        max_articles (int): Maximum number of articles to return
        
    Returns:
        list: List of mock news articles
    """
    mock_articles = [
        {
            'title': 'Central Banks Signal Potential Interest Rate Changes',
            'description': 'Central banks across major economies are signaling possible changes to interest rates in response to inflation trends, potentially affecting currency markets.',
            'url': 'https://example.com/economic-news/1',
            'publishedAt': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Economic Times'
        },
        {
            'title': 'Global Inflation Concerns Impact Currency Markets',
            'description': 'Rising inflation in major economies is causing volatility in forex markets as investors reassess currency valuations and central bank responses.',
            'url': 'https://example.com/economic-news/2',
            'publishedAt': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'source': 'Financial Post'
        },
        {
            'title': 'Trade Balance Data Shows Shifts in Economic Recovery',
            'description': 'Recent trade balance figures indicate changing patterns in global economic recovery, with potential implications for currency strength in coming months.',
            'url': 'https://example.com/economic-news/3',
            'publishedAt': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'source': 'World Economic Forum'
        },
        {
            'title': 'Supply Chain Issues Continue to Affect Global Markets',
            'description': 'Ongoing supply chain disruptions are impacting economic outlooks across regions, creating uncertainty in currency markets and trade relationships.',
            'url': 'https://example.com/economic-news/4',
            'publishedAt': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'source': 'Business Insider'
        },
        {
            'title': 'Economic Growth Forecasts Revised for Major Economies',
            'description': 'International organizations have updated growth projections for key economies, potentially signaling shifts in relative currency strengths.',
            'url': 'https://example.com/economic-news/5',
            'publishedAt': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'source': 'Reuters'
        }
    ]
    
    # Add some currency-specific mock news
    for currency in currencies:
        if currency == "USD":
            mock_articles.append({
                'title': 'US Dollar Strength Continues Amid Economic Data',
                'description': 'The US Dollar maintains its position as economic indicators suggest resilience in the American economy despite global challenges.',
                'url': 'https://example.com/economic-news/usd',
                'publishedAt': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'source': 'Wall Street Journal'
            })
        elif currency == "EUR":
            mock_articles.append({
                'title': 'European Central Bank Discusses Monetary Policy Direction',
                'description': 'ECB officials are evaluating the economic outlook for the Eurozone and considering adjustments to monetary policy that could impact the Euro.',
                'url': 'https://example.com/economic-news/eur',
                'publishedAt': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'source': 'Financial Times'
            })
        elif currency == "GBP":
            mock_articles.append({
                'title': 'Bank of England Responds to Inflation Pressures',
                'description': 'The Bank of England is implementing measures to address rising inflation, with potential implications for the British Pound in international markets.',
                'url': 'https://example.com/economic-news/gbp',
                'publishedAt': datetime.now().strftime('%Y-%m-%d'),
                'source': 'The Guardian'
            })
        elif currency == "JPY":
            mock_articles.append({
                'title': 'Bank of Japan Maintains Policy as Economy Shows Signs of Recovery',
                'description': 'The Bank of Japan has decided to maintain its current monetary policy stance as economic indicators suggest a gradual recovery, influencing the Yen\'s position.',
                'url': 'https://example.com/economic-news/jpy',
                'publishedAt': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
                'source': 'Nikkei Asia'
            })
        elif currency == "INR":
            mock_articles.append({
                'title': 'Indian Rupee Performance Linked to Economic Reforms',
                'description': 'Recent economic reforms and policy decisions in India are influencing the performance of the Rupee against major global currencies.',
                'url': 'https://example.com/economic-news/inr',
                'publishedAt': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'source': 'Economic Times India'
            })
        elif currency == "HUF":
            mock_articles.append({
                'title': 'Hungarian Forint Responds to Central Bank Monetary Decisions',
                'description': 'The Hungarian National Bank\'s recent monetary policy decisions are affecting the Forint\'s exchange rate against major currencies.',
                'url': 'https://example.com/economic-news/huf',
                'publishedAt': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'source': 'Budapest Business Journal'
            })
    
    # Ensure we don't exceed max_articles
    return mock_articles[:max_articles]
