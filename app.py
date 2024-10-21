from flask import Flask, render_template, request
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

if __name__ == '__main__':
    app.run()
