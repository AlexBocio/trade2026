# export_handlers.py - Heatmap Export Functionality
# Handles export to PNG, CSV, HTML, JSON formats

import numpy as np
import pandas as pd
import json
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def export_to_csv(heatmap_data: dict) -> io.StringIO:
    """
    Export heatmap data to CSV format.

    Args:
        heatmap_data: Heatmap data structure

    Returns:
        StringIO buffer containing CSV data
    """
    # Create DataFrame from matrix
    df = pd.DataFrame(
        heatmap_data['matrix'],
        columns=heatmap_data['timeframes'],
        index=heatmap_data['tickers']
    )

    # Add ticker column
    df.insert(0, 'Ticker', df.index)

    # Convert to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    logger.info(f"Exported heatmap to CSV: {len(heatmap_data['tickers'])} tickers × {len(heatmap_data['timeframes'])} timeframes")

    return csv_buffer


def export_to_json(heatmap_data: dict) -> str:
    """
    Export complete heatmap data to JSON.

    Args:
        heatmap_data: Heatmap data structure

    Returns:
        JSON string
    """
    export_data = {
        **heatmap_data,
        'export_metadata': {
            'exported_at': datetime.now().isoformat(),
            'export_type': 'json',
            'version': '1.0',
            'schema_version': '1.0'
        }
    }

    logger.info(f"Exported heatmap to JSON")

    return json.dumps(export_data, indent=2)


def export_to_html_simple(heatmap_data: dict, title: str = None) -> str:
    """
    Export heatmap to simple HTML table format.

    Args:
        heatmap_data: Heatmap data structure
        title: Custom title for the heatmap

    Returns:
        HTML string
    """
    if title is None:
        title = f"Stock Heatmap - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Create DataFrame
    df = pd.DataFrame(
        heatmap_data['matrix'],
        columns=heatmap_data['timeframes'],
        index=heatmap_data['tickers']
    )

    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            table {{
                border-collapse: collapse;
                margin: 20px auto;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                min-width: 60px;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .positive {{
                background-color: #c8e6c9;
                color: #2e7d32;
            }}
            .negative {{
                background-color: #ffcdd2;
                color: #c62828;
            }}
            .zero {{
                background-color: #fff9c4;
            }}
            .metadata {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
    """

    # Add timeframe headers
    zero_idx = heatmap_data['timeframes'].index('0')
    for i, tf in enumerate(heatmap_data['timeframes']):
        if i < zero_idx:
            html += f"<th style='background-color: #e57373;'>{tf}</th>"
        elif tf == '0':
            html += f"<th style='background-color: #ffd54f;'>{tf}</th>"
        else:
            html += f"<th style='background-color: #81c784;'>{tf}</th>"

    html += """
                </tr>
            </thead>
            <tbody>
    """

    # Add data rows
    for ticker, row in zip(heatmap_data['tickers'], heatmap_data['matrix']):
        html += f"<tr><td><strong>{ticker}</strong></td>"
        for val in row:
            if val > 0:
                html += f"<td class='positive'>{val:.2%}</td>"
            elif val < 0:
                html += f"<td class='negative'>{val:.2%}</td>"
            else:
                html += f"<td class='zero'>-</td>"
        html += "</tr>"

    html += """
            </tbody>
        </table>
        <div class="metadata">
            <p><strong>Market Regime:</strong> """ + heatmap_data.get('market_regime', 'N/A') + """</p>
            <p><strong>Generated:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p><strong>Stocks:</strong> """ + str(len(heatmap_data['tickers'])) + """ |
               <strong>Timeframes:</strong> """ + str(len(heatmap_data['timeframes'])) + """</p>
        </div>
    </body>
    </html>
    """

    logger.info(f"Exported heatmap to HTML")

    return html


def get_filename(format_type: str) -> str:
    """
    Generate filename with timestamp.

    Args:
        format_type: File extension (csv, json, html, png)

    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"heatmap_{timestamp}.{format_type}"
