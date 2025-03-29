import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time
from currency_api import get_exchange_rates, get_historical_rates
from time_series_model import forecast_currency
from news_api import get_economic_news
from utils import calculate_gain_loss, get_currency_list, get_currency_full_names

# Page configuration
st.set_page_config(
    page_title="Currency Conversion Predictor",
    page_icon="💱",
    layout="wide"
)

# Initialize session state variables
if 'selected_currencies' not in st.session_state:
    st.session_state.selected_currencies = []
if 'base_currency' not in st.session_state:
    st.session_state.base_currency = 'USD'
if 'forecast_days' not in st.session_state:
    st.session_state.forecast_days = 30
if 'investment_amount' not in st.session_state:
    st.session_state.investment_amount = 1000.0

# Header
st.title("Currency Conversion Predictor")
st.markdown("Analyze forex trends and predict the best time to convert currencies.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Base currency selection
    currency_list = get_currency_list()
    base_currency = st.selectbox(
        "Select Base Currency",
        options=currency_list,
        index=currency_list.index(st.session_state.base_currency)
    )
    
    if base_currency != st.session_state.base_currency:
        st.session_state.base_currency = base_currency
        st.session_state.selected_currencies = []
    
    # Target currencies selection
    available_currencies = [curr for curr in currency_list if curr != base_currency]
    selected_currencies = st.multiselect(
        "Select Target Currencies to Track",
        options=available_currencies,
        default=st.session_state.selected_currencies
    )
    
    st.session_state.selected_currencies = selected_currencies
    
    # Forecast settings
    st.subheader("Forecast Settings")
    st.session_state.forecast_days = st.slider("Forecast Days", 7, 90, st.session_state.forecast_days)
    
    # Investment calculator
    st.subheader("Investment Calculator")
    st.session_state.investment_amount = st.number_input(
        f"Investment Amount ({base_currency})",
        min_value=1.0,
        value=st.session_state.investment_amount,
        key="sidebar_investment_amount"
    )

# Main content
tabs = st.tabs(["Live Rates", "Historical Trends", "Forecasting", "Gain/Loss Calculator", "Economic News"])

# Tab 1: Live Rates
with tabs[0]:
    st.header("Current Exchange Rates")
    
    if not st.session_state.selected_currencies:
        st.warning("Please select at least one target currency in the sidebar.")
    else:
        with st.spinner("Fetching latest exchange rates..."):
            rates = get_exchange_rates(st.session_state.base_currency)
            if rates:
                # Create a DataFrame for display
                filtered_rates = {curr: rates[curr] for curr in st.session_state.selected_currencies if curr in rates}
                df_rates = pd.DataFrame({
                    'Currency': list(filtered_rates.keys()),
                    'Currency Name': [get_currency_full_names().get(curr, curr) for curr in filtered_rates.keys()],
                    'Exchange Rate': list(filtered_rates.values()),
                    f'Value of {st.session_state.investment_amount} {st.session_state.base_currency}': 
                        [st.session_state.investment_amount * rate for rate in filtered_rates.values()]
                })
                
                st.dataframe(df_rates, use_container_width=True)
                
                # Create bar chart for comparison
                fig = px.bar(
                    df_rates, 
                    x='Currency', 
                    y='Exchange Rate',
                    title=f"Current Exchange Rates (Base: {st.session_state.base_currency})",
                    color='Currency',
                    hover_data=['Currency Name']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to fetch exchange rates. Please try again later.")
                
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh rates (every 60 seconds)")
        if auto_refresh:
            st.info("Rates will refresh automatically every 60 seconds")
            # Add a placeholder for the auto-refresh time indicator
            refresh_placeholder = st.empty()
            # Wait for 60 seconds before rerunning
            for i in range(60, 0, -1):
                refresh_placeholder.text(f"Refreshing in {i} seconds...")
                time.sleep(1)
            st.rerun()

# Tab 2: Historical Trends
with tabs[1]:
    st.header("Historical Exchange Rate Trends")
    
    if not st.session_state.selected_currencies:
        st.warning("Please select at least one target currency in the sidebar.")
    else:
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date() - timedelta(days=90),
                max_value=datetime.now().date() - timedelta(days=1)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                min_value=start_date,
                max_value=datetime.now().date()
            )
        
        if start_date >= end_date:
            st.error("Start date must be before end date")
        else:
            with st.spinner("Fetching historical data..."):
                historical_data = {}
                for currency in st.session_state.selected_currencies:
                    historical_rates = get_historical_rates(
                        st.session_state.base_currency,
                        currency,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d')
                    )
                    if historical_rates:
                        historical_data[currency] = historical_rates
                
                if not historical_data:
                    st.error("Failed to fetch historical data. Please try again later.")
                else:
                    # Create figure for historical trends
                    fig = go.Figure()
                    
                    for currency, rates in historical_data.items():
                        dates = list(rates.keys())
                        values = list(rates.values())
                        
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=values,
                            mode='lines',
                            name=f"{st.session_state.base_currency}/{currency}"
                        ))
                    
                    fig.update_layout(
                        title=f"Historical Exchange Rates (Base: {st.session_state.base_currency})",
                        xaxis_title="Date",
                        yaxis_title="Exchange Rate",
                        legend_title="Currency Pair",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistical insights
                    st.subheader("Statistical Insights")
                    
                    for currency, rates in historical_data.items():
                        rates_values = list(rates.values())
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(f"{currency} - Average", f"{np.mean(rates_values):.4f}")
                        with col2:
                            st.metric(f"{currency} - Min", f"{min(rates_values):.4f}")
                        with col3:
                            st.metric(f"{currency} - Max", f"{max(rates_values):.4f}")
                        with col4:
                            volatility = np.std(rates_values) / np.mean(rates_values) * 100
                            st.metric(f"{currency} - Volatility", f"{volatility:.2f}%")

# Tab 3: Forecasting
with tabs[2]:
    st.header("Exchange Rate Forecasting")
    
    if not st.session_state.selected_currencies:
        st.warning("Please select at least one target currency in the sidebar.")
    else:
        st.info(f"Showing {st.session_state.forecast_days}-day forecast for selected currencies. Adjust forecast period in the sidebar.")
        
        forecast_currency_options = st.multiselect(
            "Select currencies to forecast",
            options=st.session_state.selected_currencies,
            default=st.session_state.selected_currencies[:1] if st.session_state.selected_currencies else []
        )
        
        if not forecast_currency_options:
            st.warning("Please select at least one currency to forecast.")
        else:
            with st.spinner("Generating forecasts..."):
                for currency in forecast_currency_options:
                    st.subheader(f"{st.session_state.base_currency}/{currency} Forecast")
                    
                    # Get historical data for training
                    historical_rates = get_historical_rates(
                        st.session_state.base_currency,
                        currency,
                        (datetime.now().date() - timedelta(days=365)).strftime('%Y-%m-%d'),
                        datetime.now().date().strftime('%Y-%m-%d')
                    )
                    
                    if historical_rates:
                        # Prepare data for forecasting
                        df_historical = pd.DataFrame({
                            'ds': pd.to_datetime(list(historical_rates.keys())),
                            'y': list(historical_rates.values())
                        })
                        
                        # Generate forecast
                        forecast_df = forecast_currency(df_historical, st.session_state.forecast_days)
                        
                        if forecast_df is not None:
                            # Plot the forecast
                            fig = go.Figure()
                            
                            # Historical data
                            fig.add_trace(go.Scatter(
                                x=df_historical['ds'],
                                y=df_historical['y'],
                                mode='lines',
                                name='Historical',
                                line=dict(color='blue')
                            ))
                            
                            # Forecast
                            fig.add_trace(go.Scatter(
                                x=forecast_df['ds'],
                                y=forecast_df['yhat'],
                                mode='lines',
                                name='Forecast',
                                line=dict(color='red')
                            ))
                            
                            # Upper and lower bounds
                            fig.add_trace(go.Scatter(
                                x=forecast_df['ds'],
                                y=forecast_df['yhat_upper'],
                                mode='lines',
                                line=dict(width=0),
                                showlegend=False
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=forecast_df['ds'],
                                y=forecast_df['yhat_lower'],
                                mode='lines',
                                line=dict(width=0),
                                fill='tonexty',
                                fillcolor='rgba(255, 0, 0, 0.2)',
                                name='Confidence Interval'
                            ))
                            
                            fig.update_layout(
                                title=f"{st.session_state.base_currency}/{currency} Exchange Rate Forecast",
                                xaxis_title="Date",
                                yaxis_title="Exchange Rate",
                                hovermode="x unified"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Forecast insights
                            current_rate = list(historical_rates.values())[-1]
                            future_rate = forecast_df['yhat'].iloc[-1]
                            percent_change = (future_rate - current_rate) / current_rate * 100
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    label="Current Rate",
                                    value=f"{current_rate:.4f}"
                                )
                            with col2:
                                st.metric(
                                    label=f"Forecast Rate in {st.session_state.forecast_days} days",
                                    value=f"{future_rate:.4f}",
                                    delta=f"{percent_change:.2f}%"
                                )
                            
                            # Recommendation
                            st.subheader("Recommendation")
                            if percent_change > 2:
                                st.success(f"Consider waiting to convert {st.session_state.base_currency} to {currency}. The rate is expected to improve significantly.")
                            elif percent_change < -2:
                                st.error(f"Consider converting {st.session_state.base_currency} to {currency} soon. The rate is expected to deteriorate.")
                            else:
                                st.info(f"The {st.session_state.base_currency}/{currency} rate is expected to remain relatively stable.")
                        else:
                            st.error(f"Failed to generate forecast for {st.session_state.base_currency}/{currency}.")
                    else:
                        st.error(f"Failed to fetch historical data for {st.session_state.base_currency}/{currency}.")

# Tab 4: Gain/Loss Calculator
with tabs[3]:
    st.header("Gain/Loss Calculator")
    
    if not st.session_state.selected_currencies:
        st.warning("Please select at least one target currency in the sidebar.")
    else:
        st.info(f"Calculate potential gains or losses if you had converted {st.session_state.base_currency} in the past")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calculator_amount = st.number_input(
                f"Investment Amount ({st.session_state.base_currency})",
                min_value=1.0,
                value=st.session_state.investment_amount,
                key="calculator_investment_amount"
            )
        
        with col2:
            past_date = st.date_input(
                "Past Date",
                value=datetime.now().date() - timedelta(days=30),
                max_value=datetime.now().date() - timedelta(days=1)
            )
        
        with col3:
            target_currency = st.selectbox(
                "Target Currency",
                options=st.session_state.selected_currencies
            )
        
        if st.button("Calculate"):
            with st.spinner("Calculating potential gain/loss..."):
                result = calculate_gain_loss(
                    st.session_state.base_currency,
                    target_currency,
                    calculator_amount,
                    past_date.strftime('%Y-%m-%d'),
                    datetime.now().date().strftime('%Y-%m-%d')
                )
                
                if result:
                    past_rate, current_rate, past_value, current_value, absolute_change, percentage_change = result
                    
                    st.subheader("Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            label=f"Exchange Rate on {past_date.strftime('%Y-%m-%d')}",
                            value=f"{past_rate:.4f}"
                        )
                        st.metric(
                            label=f"Value in {target_currency} on {past_date.strftime('%Y-%m-%d')}",
                            value=f"{past_value:.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            label="Current Exchange Rate",
                            value=f"{current_rate:.4f}"
                        )
                        st.metric(
                            label=f"Current Value in {target_currency}",
                            value=f"{current_value:.2f}"
                        )
                    
                    # Gain/Loss visualization
                    st.subheader("Gain/Loss Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            label="Absolute Change",
                            value=f"{absolute_change:.2f} {target_currency}",
                            delta=f"{percentage_change:.2f}%"
                        )
                    
                    with col2:
                        if percentage_change > 0:
                            st.success(f"You would have gained {percentage_change:.2f}% by converting on {past_date.strftime('%Y-%m-%d')}")
                        elif percentage_change < 0:
                            st.error(f"You would have lost {abs(percentage_change):.2f}% by converting on {past_date.strftime('%Y-%m-%d')}")
                        else:
                            st.info("The exchange rate has remained stable. No significant gain or loss.")
                else:
                    st.error("Failed to calculate gain/loss. Please try again.")

# Tab 5: Economic News
with tabs[4]:
    st.header("Economic News")
    
    st.info("Latest economic news that might impact currency exchange rates")
    
    selected_news_currencies = st.multiselect(
        "Select currencies to get relevant news",
        options=[st.session_state.base_currency] + st.session_state.selected_currencies,
        default=[st.session_state.base_currency] if st.session_state.base_currency else []
    )
    
    if not selected_news_currencies:
        st.warning("Please select at least one currency to get news.")
    else:
        with st.spinner("Fetching economic news..."):
            news_items = get_economic_news(selected_news_currencies)
            
            if news_items:
                for i, news in enumerate(news_items):
                    with st.expander(f"{news['title']} ({news['source']})", expanded=i==0):
                        st.write(f"**Published:** {news['publishedAt']}")
                        st.write(news['description'])
                        st.markdown(f"[Read more]({news['url']})")
            else:
                st.warning("No relevant economic news found. Please try again later.")

# Footer
st.markdown("---")
st.markdown("Currency Conversion Predictor | Data is for informational purposes only")
