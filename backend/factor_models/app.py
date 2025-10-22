# app.py - Factor Models API

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import yfinance as yf
from barra_model import BarraFactorModel
from factor_analysis import FactorAnalyzer
from risk_attribution import RiskAttributor

app = Flask(__name__)
CORS(app)

# Cache for models
models = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Factor Models & Risk Attribution',
        'version': '1.0.0'
    })


@app.route('/api/factors/barra', methods=['POST'])
def analyze_barra():
    """
    Barra factor model analysis.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.25, "AMZN": 0.25},
        "start_date": "2022-01-01",
        "end_date": "2024-12-31"
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        weights = data['weights']
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Create and fit model
        model = BarraFactorModel(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date
        )

        model.fetch_data()
        model.calculate_factors()
        model.estimate_factor_returns()
        model.calculate_factor_covariance()
        model.calculate_specific_risk()

        # Analyze portfolio
        risk_decomp = model.decompose_portfolio_risk(weights)
        tilts = model.factor_tilts(weights)

        return jsonify({
            'risk_decomposition': risk_decomp,
            'factor_tilts': tilts,
            'factor_exposures': model.factors.to_dict(),
            'specific_risks': model.specific_risk.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/factors/pca', methods=['POST'])
def extract_pca_factors():
    """
    Extract statistical factors using PCA.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"],
        "n_factors": 3,
        "start_date": "2022-01-01",
        "end_date": "2024-12-31"
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        n_factors = data.get('n_factors', 3)
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Fetch returns
        prices = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
        returns = prices.pct_change().dropna()

        # PCA
        analyzer = FactorAnalyzer(returns)
        result = analyzer.extract_pca_factors(n_factors)

        return jsonify({
            'n_factors': n_factors,
            'explained_variance': result['explained_variance'],
            'total_explained': result['total_explained'],
            'loadings': result['loadings'].to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/factors/factor-betas', methods=['POST'])
def calculate_factor_betas():
    """
    Calculate asset's beta to statistical factors.

    Body:
    {
        "benchmark_tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "asset_ticker": "TSLA",
        "n_factors": 3
    }
    """
    try:
        data = request.json
        benchmark_tickers = data['benchmark_tickers']
        asset_ticker = data['asset_ticker']
        n_factors = data.get('n_factors', 3)
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Fetch benchmark returns
        benchmark_prices = yf.download(benchmark_tickers, start=start_date,
                                      end=end_date, progress=False)['Adj Close']
        benchmark_returns = benchmark_prices.pct_change().dropna()

        # Extract factors from benchmark
        analyzer = FactorAnalyzer(benchmark_returns)
        analyzer.extract_pca_factors(n_factors)

        # Fetch asset returns
        asset_prices = yf.download(asset_ticker, start=start_date,
                                  end=end_date, progress=False)['Adj Close']
        asset_returns = asset_prices.pct_change().dropna()

        # Calculate betas
        betas = analyzer.calculate_factor_betas(asset_returns)

        return jsonify({
            'asset': asset_ticker,
            'betas': betas['betas'],
            'alpha': betas['alpha'],
            'r_squared': betas['r_squared']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/factors/mimicking-portfolio', methods=['POST'])
def create_mimicking_portfolio():
    """
    Create a portfolio that mimics a specific factor.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "factor_index": 0,
        "n_factors": 3
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        factor_index = data.get('factor_index', 0)
        n_factors = data.get('n_factors', 3)
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Fetch returns
        prices = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
        returns = prices.pct_change().dropna()

        # Extract factors
        analyzer = FactorAnalyzer(returns)
        analyzer.extract_pca_factors(n_factors)

        # Create mimicking portfolio
        factor_name = f'PC{factor_index + 1}'
        weights = analyzer.factor_mimicking_portfolio(factor_name)

        return jsonify({
            'factor': factor_name,
            'weights': weights
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/risk/attribution', methods=['POST'])
def risk_attribution():
    """
    Comprehensive risk attribution analysis.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.25, "AMZN": 0.25}
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        weights = data['weights']
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Create Barra model
        model = BarraFactorModel(tickers=tickers, start_date=start_date, end_date=end_date)
        model.fetch_data()
        model.calculate_factors()
        model.estimate_factor_returns()
        model.calculate_factor_covariance()
        model.calculate_specific_risk()

        # Create risk attributor
        attributor = RiskAttributor(model)

        # Calculate all attribution metrics
        mcr = attributor.marginal_contribution_to_risk(weights)
        ccr = attributor.component_contribution_to_risk(weights)
        factor_contrib = attributor.factor_risk_contribution(weights)
        div_ratio = attributor.diversification_ratio(weights)

        return jsonify({
            'marginal_contribution_to_risk': mcr,
            'component_contribution_to_risk': ccr,
            'factor_risk_contribution': factor_contrib,
            'diversification_ratio': div_ratio
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/risk/stress-test', methods=['POST'])
def stress_test():
    """
    Stress test portfolio under factor shocks.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.25, "AMZN": 0.25},
        "factor_shocks": {"Size": -0.02, "Value": 0.03, "Momentum": -0.01}
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        weights = data['weights']
        factor_shocks = data['factor_shocks']
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Create Barra model
        model = BarraFactorModel(tickers=tickers, start_date=start_date, end_date=end_date)
        model.fetch_data()
        model.calculate_factors()
        model.estimate_factor_returns()
        model.calculate_factor_covariance()
        model.calculate_specific_risk()

        # Create risk attributor
        attributor = RiskAttributor(model)

        # Run stress test
        stress_results = attributor.stress_test(weights, factor_shocks)

        return jsonify(stress_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/risk/budget', methods=['POST'])
def risk_budget():
    """
    Risk budgeting analysis.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.25, "AMZN": 0.25},
        "target_budgets": {"AAPL": 25, "MSFT": 25, "GOOGL": 25, "AMZN": 25}
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        weights = data['weights']
        target_budgets = data.get('target_budgets')
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Create Barra model
        model = BarraFactorModel(tickers=tickers, start_date=start_date, end_date=end_date)
        model.fetch_data()
        model.calculate_factors()
        model.estimate_factor_returns()
        model.calculate_factor_covariance()
        model.calculate_specific_risk()

        # Create risk attributor
        attributor = RiskAttributor(model)

        # Analyze risk budget
        budget_analysis = attributor.risk_budget_analysis(weights, target_budgets)

        return jsonify(budget_analysis)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/factors/comprehensive', methods=['POST'])
def comprehensive_factor_analysis():
    """
    Comprehensive factor analysis combining Barra and PCA.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "weights": {"AAPL": 0.25, "MSFT": 0.25, "GOOGL": 0.25, "AMZN": 0.25}
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        weights = data['weights']
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date', '2024-12-31')

        # Barra model
        barra_model = BarraFactorModel(tickers=tickers, start_date=start_date, end_date=end_date)
        barra_model.fetch_data()
        barra_model.calculate_factors()
        barra_model.estimate_factor_returns()
        barra_model.calculate_factor_covariance()
        barra_model.calculate_specific_risk()

        risk_decomp = barra_model.decompose_portfolio_risk(weights)
        tilts = barra_model.factor_tilts(weights)

        # PCA analysis
        prices = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
        returns = prices.pct_change().dropna()
        pca_analyzer = FactorAnalyzer(returns)
        pca_result = pca_analyzer.extract_pca_factors(3)

        # Risk attribution
        attributor = RiskAttributor(barra_model)
        div_ratio = attributor.diversification_ratio(weights)
        factor_contrib = attributor.factor_risk_contribution(weights)

        return jsonify({
            'barra_analysis': {
                'risk_decomposition': risk_decomp,
                'factor_tilts': tilts
            },
            'pca_analysis': {
                'explained_variance': pca_result['explained_variance'],
                'total_explained': pca_result['total_explained']
            },
            'risk_attribution': {
                'diversification_ratio': div_ratio,
                'factor_risk_contribution': factor_contrib
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("[START] Factor Models & Risk Attribution API")
    print("[INFO] Available endpoints:")
    print("  - POST /api/factors/barra")
    print("  - POST /api/factors/pca")
    print("  - POST /api/factors/factor-betas")
    print("  - POST /api/factors/mimicking-portfolio")
    print("  - POST /api/risk/attribution")
    print("  - POST /api/risk/stress-test")
    print("  - POST /api/risk/budget")
    print("  - POST /api/factors/comprehensive")
    print("\n[OK] Server running on http://localhost:5004\n")

    app.run(host='0.0.0.0', port=5004, debug=True)
