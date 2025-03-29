# Currency Conversion Predictor

Currency Conversion Predictor is a web application built with Streamlit that allows users to analyze forex trends, predict the best time to convert currencies, and calculate potential gains or losses from currency conversions.

## Features

- **Live Rates**: Fetch and display the latest exchange rates for selected currencies.
- **Historical Trends**: Visualize historical exchange rate trends for selected currencies over a specified date range.
- **Forecasting**: Generate and display exchange rate forecasts for selected currencies using time series models.
- **Gain/Loss Calculator**: Calculate potential gains or losses if you had converted currencies in the past.
- **Economic News**: Fetch and display the latest economic news that might impact currency exchange rates.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/amitwadhwa83/currency-conversion-predictor.git
    cd currency-conversion-predictor
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:
    ```sh
    streamlit run app.py
    ```

## Usage

1. **Settings**: Configure the base currency, target currencies, forecast days, and investment amount in the sidebar.
2. **Live Rates**: View the current exchange rates and a bar chart comparison of selected currencies.
3. **Historical Trends**: Select a date range to visualize historical exchange rate trends and view statistical insights.
4. **Forecasting**: Generate and view exchange rate forecasts for selected currencies, along with recommendations.
5. **Gain/Loss Calculator**: Calculate potential gains or losses from past currency conversions.
6. **Economic News**: Fetch and read the latest economic news relevant to selected currencies.

## Dependencies

- `streamlit`
- `pandas`
- `plotly`
- `numpy`
- `datetime`
- `time`
- Custom modules: `currency_api`, `time_series_model`, `news_api`, `utils`