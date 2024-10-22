import io
import csv
import json
from flask import Flask, jsonify, render_template, request, Response
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get data from the form
        example_data = request.form.get('example_data')
        additional_instructions = request.form.get('additional_instructions')
        variables = request.form.get('variables')

        # For now, print to console (later replace with logic)
        print(f"Example Data: {example_data}")
        print(f"Additional Instructions: {additional_instructions}")
        print(f"Variables: {variables}")

    return render_template('index.html')


@app.route('/export-csv')
def export_csv():
    # Create a blank CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Optionally add a header row or leave it blank
    # writer.writerow(['Column 1', 'Column 2', 'Column 3'])

    output.seek(0)  # Rewind the file to the beginning

    # Prepare response to send CSV as download
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            "Content-Disposition": "attachment;filename=data.csv"
        }
    )


@app.route('/export-json')
def export_json():
    # Create a blank JSON structure
    blank_json = {}

    # Convert dictionary to JSON string
    json_data = json.dumps(blank_json, indent=4)

    # Prepare response to send JSON as download
    return Response(
        json_data,
        mimetype='application/json',
        headers={
            "Content-Disposition": "attachment;filename=data.json"
        }
    )

@app.route('/generate-table', methods=['POST'])
def generate_table():
    # Get the input from the user
    data = request.get_json()
    user_input = data.get('input', '')

    # Split the input by lines and prepare the data for the table
    table_data = []
    for line in user_input.splitlines():
        if line.strip():  # Ignore empty lines
            table_data.append({
                'input_definition': line.strip(),
                'new_name': ''  # New name column is left blank for now
            })

    # Return the data in JSON format
    return jsonify(table_data)

if __name__ == '__main__':
    app.run()
