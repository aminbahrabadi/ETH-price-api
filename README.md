# ETH Price Fetcher

This repository contains code to fetch the Ethereum (ETH) price for the last 30 days from CoinGecko and UniSwapV3.

## Introduction

This project aims to provide a simple and easy-to-use tool for retrieving historical ETH prices from CoinGecko and UniSwapV3 APIs. It offers a straightforward endpoint that returns the ETH prices for the last 30 days in a structured JSON format.

## Getting Started

To get started with using this tool, follow these steps:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/aminbahrabadi/ETH-price-api
    ```

2. Install the required dependencies. You can do this using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    python mangage.py runserver
    ```

4. Access the endpoint to retrieve ETH prices:

    ```
    GET /api/get-eth-prices/
    ```

## Endpoint Response

The endpoint returns a JSON object containing the ETH prices for the last 30 days from CoinGecko and UniSwapV3 APIs. Each entry in the response includes the following fields:

- **symbol**: The symbol for the cryptocurrency.
- **timestamp**: Unix timestamp representing the date of the price data.
- **CoinGecko**: ETH price obtained from the CoinGecko API.
- **UniSwapV3**: ETH price obtained from the UniSwapV3 API.

Example response:

```json
{
    "symbol": "WETH",
    "timestamp": 1714348800,
    "CoinGecko": 3200.0033574175,
    "UniSwapV3": 3199.9588681457
}
```

## Online Version

An online version of this tool is available at [https://prices.pytsts.ir/api/get-eth-prices/](https://prices.pytsts.ir/api/get-eth-prices/).
