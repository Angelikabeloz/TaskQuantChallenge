from flask import Flask, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Constants
path_w = "trades.sqlite"
table_w = "epex_12_20_12_13"


def compute_pnl(strategy_id: str, *args, **kwargs) -> float:
    path = kwargs.get("path", path_w)
    table = kwargs.get("table", table_w)

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    query = f"""
        SELECT SUM(
            CASE 
                WHEN side = 'sell' THEN quantity * price
                WHEN side = 'buy' THEN -quantity * price
            END
        ) as pnl
        FROM {table}
        WHERE strategy = ?
    """

    cursor.execute(query, (strategy_id,))
    result = cursor.fetchone()[0]
    connection.close()

    return result if result is not None else 0.0


@app.route("/v1/pnl/<strategy_id>", methods=["GET"])
def get_pnl(strategy_id):
    pnl = compute_pnl(strategy_id)
    response = {
        "strategy": strategy_id,
        "value": pnl,
        "unit": "euro",
        "capture_time": datetime.utcnow().isoformat() + "Z"
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
