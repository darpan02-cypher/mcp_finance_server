"""
Gradio MCP Server for Financial Tools
Extends the stock price tool example with additional financial analysis capabilities.

Setup:
    pip install "gradio[mcp]" yfinance
    
Run:
    python gradio_mcp_finance_server.py
    
Connect to MCP Client (e.g., Claude Desktop):
    Add this to your MCP Client config:
    {
        "mcpServers": {
            "gradio-finance": {
                "url": "http://localhost:7860/gradio_api/mcp/sse"
            }
        }
    }
"""

import gradio as gr
import yfinance as yf
from datetime import datetime, timedelta
import json


# ============================================================================
# Financial Tools - Pure Logic Functions
# ============================================================================

def get_stock_price(symbol: str) -> str:
    """
    Get the current stock price for a ticker symbol.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
    
    Returns:
        str: A formatted string with the stock price information
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.info
        price = data.get("currentPrice")
        if price:
            currency = data.get("currency", "USD")
            return f"{symbol.upper()}: ${price:.2f} {currency}"
        else:
            return f"Could not retrieve price for {symbol.upper()}"
    except Exception as e:
        return f"Error fetching price for {symbol.upper()}: {str(e)}"


def get_stock_info(symbol: str) -> str:
    """
    Get detailed company information for a stock ticker.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
    
    Returns:
        str: JSON formatted company information including market cap, PE ratio, industry
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        company_info = {
            "symbol": symbol.upper(),
            "name": info.get("longName", "N/A"),
            "industry": info.get("industry", "N/A"),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
        
        return json.dumps(company_info, indent=2, default=str)
    except Exception as e:
        return f"Error fetching info for {symbol.upper()}: {str(e)}"


def compare_stocks(symbols: str) -> str:
    """
    Compare multiple stocks side by side.
    
    Args:
        symbols (str): Comma-separated ticker symbols (e.g., AAPL,MSFT,TSLA)
    
    Returns:
        str: Formatted comparison table with prices and key metrics
    """
    try:
        tickers = [s.strip().upper() for s in symbols.split(",")]
        comparison = {}
        
        for ticker in tickers:
            t = yf.Ticker(ticker)
            info = t.info
            comparison[ticker] = {
                "price": info.get("currentPrice", "N/A"),
                "change_percent": info.get("regularMarketChangePercent", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
            }
        
        return json.dumps(comparison, indent=2, default=str)
    except Exception as e:
        return f"Error comparing stocks: {str(e)}"


def get_stock_trend(symbol: str, days: str = "30") -> str:
    """
    Get historical price trend and statistics for a stock.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
        days (str): Number of days of history to analyze (default: 30)
    
    Returns:
        str: JSON formatted trend data with price changes and statistics
    """
    try:
        days_int = int(days)
        ticker = yf.Ticker(symbol.upper())
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int)
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            return f"No historical data available for {symbol.upper()}"
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        price_change = end_price - start_price
        percent_change = (price_change / start_price) * 100
        
        trend_data = {
            "symbol": symbol.upper(),
            "period_days": days_int,
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
            "price_change": round(price_change, 2),
            "percent_change": round(percent_change, 2),
            "high_price": round(hist['High'].max(), 2),
            "low_price": round(hist['Low'].min(), 2),
            "average_price": round(hist['Close'].mean(), 2),
        }
        
        return json.dumps(trend_data, indent=2)
    except Exception as e:
        return f"Error fetching trend for {symbol.upper()}: {str(e)}"


def analyze_portfolio(symbols: str, quantities: str = "") -> str:
    """
    Analyze a portfolio of stocks.
    
    Args:
        symbols (str): Comma-separated ticker symbols (e.g., AAPL,MSFT,TSLA)
        quantities (str): Optional comma-separated quantities owned (e.g., 10,5,2). If not provided, assumes 1 share each.
    
    Returns:
        str: Portfolio analysis with total value and allocation
    """
    try:
        tickers = [s.strip().upper() for s in symbols.split(",")]
        qty_list = []
        
        if quantities:
            qty_list = [float(q.strip()) for q in quantities.split(",")]
        else:
            qty_list = [1.0] * len(tickers)
        
        if len(qty_list) != len(tickers):
            return "Error: Number of quantities must match number of symbols"
        
        portfolio_data = {}
        total_value = 0
        
        for ticker, qty in zip(tickers, qty_list):
            t = yf.Ticker(ticker)
            price = t.info.get("currentPrice", 0)
            value = price * qty
            total_value += value
            
            portfolio_data[ticker] = {
                "quantity": qty,
                "price_per_share": round(price, 2),
                "total_value": round(value, 2),
            }
        
        portfolio_data["portfolio_total_value"] = round(total_value, 2)
        
        # Calculate allocation percentages
        for ticker in tickers:
            if total_value > 0:
                allocation = (portfolio_data[ticker]["total_value"] / total_value) * 100
                portfolio_data[ticker]["allocation_percent"] = round(allocation, 2)
        
        return json.dumps(portfolio_data, indent=2)
    except Exception as e:
        return f"Error analyzing portfolio: {str(e)}"


# ============================================================================
# Gradio Interface Setup
# ============================================================================

with gr.Blocks(title="Finance MCP Server") as demo:
    gr.Markdown("""
    # 📊 Finance MCP Server
    
    This is an MCP (Model Context Protocol) server exposing financial analysis tools.
    
    **Available Tools:**
    - Get current stock prices
    - Retrieve detailed company information
    - Compare multiple stocks
    - Analyze price trends
    - Portfolio analysis
    
    **MCP Connection:**
    - URL: `http://localhost:7860/gradio_api/mcp/sse`
    - Add this to your MCP Client configuration to use these tools with Claude or other LLM applications
    """)
    
    # Stock Price Tool
    with gr.Tab("Get Stock Price"):
        gr.Markdown("Fetch the current price of a stock")
        symbol_input = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL")
        price_output = gr.Textbox(label="Result")
        gr.Button("Get Price").click(get_stock_price, inputs=symbol_input, outputs=price_output)
    
    # Stock Info Tool
    with gr.Tab("Get Stock Info"):
        gr.Markdown("Get detailed information about a company")
        symbol_input = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL")
        info_output = gr.Textbox(label="Result")
        gr.Button("Get Info").click(get_stock_info, inputs=symbol_input, outputs=info_output)
    
    # Compare Stocks Tool
    with gr.Tab("Compare Stocks"):
        gr.Markdown("Compare multiple stocks side by side")
        symbols_input = gr.Textbox(label="Stock Symbols", placeholder="e.g., AAPL,MSFT,TSLA")
        compare_output = gr.Textbox(label="Result")
        gr.Button("Compare").click(compare_stocks, inputs=symbols_input, outputs=compare_output)
    
    # Stock Trend Tool
    with gr.Tab("Get Stock Trend"):
        gr.Markdown("Analyze historical price trends for a stock")
        trend_symbol = gr.Textbox(label="Stock Symbol", placeholder="e.g., AAPL")
        trend_days = gr.Textbox(label="Days", value="30", placeholder="e.g., 30")
        trend_output = gr.Textbox(label="Result")
        gr.Button("Get Trend").click(get_stock_trend, inputs=[trend_symbol, trend_days], outputs=trend_output)
    
    # Portfolio Analysis Tool
    with gr.Tab("Analyze Portfolio"):
        gr.Markdown("Analyze a portfolio of stocks")
        portfolio_symbols = gr.Textbox(label="Stock Symbols", placeholder="e.g., AAPL,MSFT,TSLA")
        portfolio_quantities = gr.Textbox(label="Quantities (optional)", placeholder="e.g., 10,5,2")
        portfolio_output = gr.Textbox(label="Result")
        gr.Button("Analyze Portfolio").click(analyze_portfolio, inputs=[portfolio_symbols, portfolio_quantities], outputs=portfolio_output)


if __name__ == "__main__":
    # Launch the Gradio app as an MCP server
    # The server will be available at: http://localhost:7860/gradio_api/mcp/sse
    print("🚀 Starting Finance MCP Server...")
    print("📍 MCP Server URL: http://localhost:7860/gradio_api/mcp/sse")
    print("🌐 Web Interface: http://localhost:7860")
    print("\n✅ Server is ready! Add it to your MCP Client configuration to use these tools.\n")
    
    demo.launch(mcp_server=True, server_name="0.0.0.0", server_port=7860, share=True)