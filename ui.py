from flask import Flask, request, render_template_string, jsonify
from db_handler import fetch_tables_and_top_rows
import re
import ast


app = Flask(__name__)

html_template = """
<!doctype html>
<html>
<head>
    <title>Telemetry Tables & Graphs</title>
    <script src="https://cdn.plot.ly/plotly-2.26.1.min.js"></script>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 90%; margin-bottom: 40px; }
        th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
        th { background-color: #f0f0f0; }
        h2 { margin-top: 40px; }
        .graph-controls { margin: 30px 0; }
        .graph-controls select, .graph-controls button { margin-right: 10px; }
    </style>
</head>
<body>
    <h1>Telemetry Data</h1>

    <div class="graph-controls">
        <label>Select Data to Plot:</label>
        <select id="var-select" multiple size="5">
            {% for var_name in structured_data %}
                <option value="{{ var_name }}">{{ var_name }}</option>
            {% endfor %}
        </select>

        <label>Graph Type:</label>
        <select id="graph-type">
            <option value="time">Time Series</option>
            <option value="hist">Histogram</option>
            <option value="box">Box Plot</option>
        </select>

        <button onclick="plotSelected()">Plot</button>
    </div>

    <div id="plot" style="width: 100%; height: 600px;"></div>

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

    <script>
        async function fetchVariable(varName) {
            const res = await fetch(`/data/${varName}`);
            return await res.json();
        }

        async function plotSelected() {
            const selectedVars = Array.from(document.getElementById('var-select').selectedOptions).map(opt => opt.value);
            const graphType = document.getElementById('graph-type').value;

            const traces = [];

            for (const varName of selectedVars) {
                const entries = await fetchVariable(varName);
                const timestamps = [];
                const values = [];
                
                console.log(entries)

                entries.forEach(([ts, val]) => {
                    timestamps.push(ts);
                    values.push(parseFloat(val));
                });

                if (graphType === "time") {
                    traces.push({
                        x: timestamps,
                        y: values,
                        mode: 'lines+markers',
                        name: varName,
                        type: 'scatter'
                    });
                } else if (graphType === "hist") {
                    traces.push({
                        x: values,
                        type: 'histogram',
                        name: varName,
                        opacity: 0.6
                    });
                } else if (graphType === "box") {
                    traces.push({
                        y: values,
                        type: 'box',
                        name: varName
                    });
                }
            }

            const layout = {
                title: "Telemetry Graph",
                barmode: 'overlay',
                xaxis: { title: graphType === "time" ? "Time" : "Value" },
                yaxis: { title: graphType === "time" ? "Value" : "Count" }
            };

            Plotly.newPlot('plot', traces, layout);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def show_data():
    table_data = fetch_tables_and_top_rows(100)  # Reduce to avoid huge preview
    structured_data = {}
    columns = {}

    for var_name, rows in table_data.items():
        parsed_rows = []
        col_set = set()

        for timestamp, raw_str in rows:
            try:
                # Clean and parse the string
                safe_str = raw_str.replace("UnitsContainer", "'UnitsContainer'")  # sanitize for ast
                parsed = ast.literal_eval(safe_str)

                # Only use _magnitude
                if isinstance(parsed, dict) and '_magnitude' in parsed:
                    parsed = {'_magnitude': parsed['_magnitude']}  # ✅ CHANGED
                else:
                    parsed = {"value": parsed}

            except Exception:
                parsed = {"raw": raw_str}

            col_set.update(parsed.keys())
            parsed_rows.append((timestamp, parsed))

        structured_data[var_name] = parsed_rows
        columns[var_name] = sorted(col_set)

    return render_template_string(
        html_template,
        structured_data=structured_data,
        columns=columns
    )


@app.route("/data/<var_name>")
def get_variable_data(var_name):
    table_data = fetch_tables_and_top_rows(1000)

    if var_name not in table_data:
        return jsonify({"error": "Not found"}), 404

    graph_data = []

    for timestamp, raw_str in table_data[var_name]:
        try:
            # Replace <UnitsContainer(...)> or any <...> with a string 'unit'
            safe_str = re.sub(r"<[^>]+>", "'unit'", raw_str)

            # Parse safely as a Python literal
            parsed = ast.literal_eval(safe_str)

            # Extract _magnitude if it exists
            if isinstance(parsed, dict) and '_magnitude' in parsed:
                val = parsed['_magnitude']
            else:
                val = None

        except Exception as e:
            val = None  # fallback if parsing fails

        if val is not None:
            graph_data.append([timestamp, float(val)])

    return jsonify(graph_data)

if __name__ == "__main__":
    app.run(debug=True)