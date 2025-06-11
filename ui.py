from flask import Flask, request, render_template_string
from db_handler import fetch_tables_and_top_rows
import ast

app = Flask(__name__)
data =  fetch_tables_and_top_rows(10)
# HTML template
html_template = """
<!doctype html>
<html>
<head>
    <title>Telemetry Tables</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 90%; margin-bottom: 40px; }
        th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
        th { background-color: #f0f0f0; }
        h2 { margin-top: 40px; }
    </style>
</head>
<body>
    <h1>Telemetry Data</h1>
    {% for var_name, rows in structured_data.items() %}
        <h2>{{ var_name }}</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                {% for col in columns[var_name] %}
                    <th>{{ col }}</th>
                {% endfor %}
            </tr>
            {% for timestamp, values in rows %}
                <tr>
                    <td>{{ timestamp }}</td>
                    {% for col in columns[var_name] %}
                        <td>{{ values.get(col, '') }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    {% endfor %}
</body>
</html>
"""

@app.route("/")
def show_data():
    structured_data = {}
    columns = {}

    for var_name, rows in data.items():
        parsed_rows = []
        col_set = set()

        for timestamp, raw_str in rows:
            try:
                # Normalize unusual unit strings
                safe_str = raw_str.replace("<UnitsContainer({'gps': 1})>", "'gps'")
                parsed = ast.literal_eval(safe_str)
                
                # If parsed is a tuple or list, convert to dict
                if isinstance(parsed, (tuple, list)):
                    parsed = {f"value_{i}": val for i, val in enumerate(parsed)}
                
                # If not a dict, wrap in one
                elif not isinstance(parsed, dict):
                    parsed = {"value": parsed}

            except Exception:
                parsed = {"raw": raw_str}  # fallback if parsing fails

            col_set.update(parsed.keys())
            parsed_rows.append((timestamp, parsed))

        structured_data[var_name] = parsed_rows
        columns[var_name] = sorted(col_set)

    return render_template_string(html_template, structured_data=structured_data, columns=columns)

if __name__ == "__main__":
    app.run(debug=True)