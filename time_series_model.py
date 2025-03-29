import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

def forecast_currency(historical_df, forecast_days=30):
    """
    Generate exchange rate forecasts using Facebook Prophet.
    
    Args:
        historical_df (pd.DataFrame): DataFrame with 'ds' (dates) and 'y' (rates) columns
        forecast_days (int): Number of days to forecast into the future
        
    Returns:
        pd.DataFrame: DataFrame containing the forecast
    """
    try:
        # Check if we have enough data
        if len(historical_df) < 10:
            print("Not enough historical data for reliable forecasting")
            return fallback_forecast(historical_df, forecast_days)
        
        # Create and fit the Prophet model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,  # Flexibility of trend
            seasonality_prior_scale=10.0,  # Strength of seasonality
            changepoint_range=0.9  # Percentage of history where trend changes can occur
        )
        
        model.fit(historical_df)
        
        # Create future dataframe for predictions
        future = model.make_future_dataframe(periods=forecast_days)
        
        # Generate forecast
        forecast = model.predict(future)
        
        return forecast
    except Exception as e:
        print(f"Prophet forecasting failed: {e}")
        return fallback_forecast(historical_df, forecast_days)

def fallback_forecast(historical_df, forecast_days=30):
    """
    Fallback forecasting method using ARIMA model when Prophet fails.
    
    Args:
        historical_df (pd.DataFrame): DataFrame with 'ds' (dates) and 'y' (rates) columns
        forecast_days (int): Number of days to forecast into the future
        
    Returns:
        pd.DataFrame: DataFrame containing the forecast
    """
    try:
        # Extract the time series
        y = historical_df['y'].values
        
        # Simple ARIMA model
        model = ARIMA(y, order=(5, 1, 0))
        model_fit = model.fit()
        
        # Get forecast
        forecast_values = model_fit.forecast(steps=forecast_days)
        
        # Create forecast dataframe
        last_date = historical_df['ds'].iloc[-1]
        future_dates = [last_date + pd.Timedelta(days=i+1) for i in range(forecast_days)]
        
        # Combine historical and forecast data
        forecast_df = pd.DataFrame({
            'ds': pd.concat([historical_df['ds'], pd.Series(future_dates)]),
            'yhat': np.concatenate([historical_df['y'].values, forecast_values])
        })
        
        # Add uncertainty intervals (simple approach)
        forecast_std = np.std(y) * np.sqrt(np.arange(1, len(forecast_values) + 1) / 10)
        historical_std = np.zeros(len(historical_df))
        
        forecast_df['yhat_lower'] = np.concatenate([
            historical_df['y'].values, 
            forecast_values - 1.96 * forecast_std
        ])
        
        forecast_df['yhat_upper'] = np.concatenate([
            historical_df['y'].values, 
            forecast_values + 1.96 * forecast_std
        ])
        
        return forecast_df
    except Exception as e:
        print(f"ARIMA forecasting failed: {e}")
        return simple_forecast(historical_df, forecast_days)

def simple_forecast(historical_df, forecast_days=30):
    """
    Extremely simple forecasting as a last resort.
    Uses a simple moving average trend.
    
    Args:
        historical_df (pd.DataFrame): DataFrame with 'ds' (dates) and 'y' (rates) columns
        forecast_days (int): Number of days to forecast into the future
        
    Returns:
        pd.DataFrame: DataFrame containing the forecast
    """
    # Get the last value
    last_value = historical_df['y'].iloc[-1]
    
    # Calculate trend from last 30 days (or less if not available)
    window = min(30, len(historical_df) - 1)
    if window > 0:
        trend = (last_value - historical_df['y'].iloc[-1-window]) / window
    else:
        trend = 0
    
    # Create future dates
    last_date = historical_df['ds'].iloc[-1]
    future_dates = [last_date + pd.Timedelta(days=i+1) for i in range(forecast_days)]
    
    # Generate forecast values with trend
    forecast_values = [last_value + trend * (i+1) for i in range(forecast_days)]
    
    # Combine historical and forecast data
    forecast_df = pd.DataFrame({
        'ds': pd.concat([historical_df['ds'], pd.Series(future_dates)]),
        'yhat': np.concatenate([historical_df['y'].values, forecast_values])
    })
    
    # Add uncertainty intervals (increasing with time)
    forecast_std = np.std(historical_df['y']) * np.sqrt(np.arange(1, len(forecast_values) + 1) / 5)
    historical_std = np.zeros(len(historical_df))
    
    forecast_df['yhat_lower'] = np.concatenate([
        historical_df['y'].values, 
        forecast_values - 1.96 * forecast_std
    ])
    
    forecast_df['yhat_upper'] = np.concatenate([
        historical_df['y'].values, 
        forecast_values + 1.96 * forecast_std
    ])
    
    return forecast_df
