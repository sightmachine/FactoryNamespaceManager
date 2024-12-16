import os

import io
import csv
import json
from flask import Flask, jsonify, render_template, request, Response

import urllib.request
import json
import os
import ssl

app = Flask(__name__)
ENDPOINT = ""
API_KEY = ""


def get_name_from_examples(examples, instructions, old, endpoint, api_key):
    def allowSelfSignedHttps(allowed):
        # bypass the server certificate verification on client side
        if (
            allowed
            and not os.environ.get("PYTHONHTTPSVERIFY", "")
            and getattr(ssl, "_create_unverified_context", None)
        ):
            ssl._create_default_https_context = ssl._create_unverified_context

    system_prompt = f""" 
    You are an AI companion creates renaming rules for variable names.
    
    Here are some hints to help you with the renaming:
    - If you see a number, followed by a dash, followed by a number -- e.g., 1-3 -- these are important parts of the naming.
    - In general, pay attention to numbers.  They are often important.
    
    A typical name will have a pattern like Line#_MachineName_Sensor.
    
    The following examples are associated with predefined mappings:
    {examples}

    The following are additional instructions on performing the renaming:
    {instructions}
    """

    user_prompt = f""" 
    What is the best name associated with keywords '{old}'?
    """

    allowSelfSignedHttps(
        True
    )  # this line is needed if you use self-signed certificate in your scoring service.

    data = {
        "input_data": {
            "input_string": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "parameters": {"temperature": 0.0},
        }
    }

    body = str.encode(json.dumps(data))
    url = endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + api_key),
    }
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        return json.loads(result)["output"].strip()

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        print(error.info())
        print(error.read().decode("utf8", "ignore"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get data from the form
        example_data = request.form.get("example_data")
        additional_instructions = request.form.get("additional_instructions")
        variables = request.form.get("variables")

        # For now, print to console (later replace with logic)
        print(f"Example Data: {example_data}")
        print(f"Additional Instructions: {additional_instructions}")
        print(f"Variables: {variables}")

    return render_template("index.html")


@app.route("/license")
def license():
    return render_template("license_agreement.html")


@app.route("/generate-table", methods=["POST"])
def generate_table():
    # Get the input from the user
    data = request.get_json()
    endpoint = data.get("endpointurl", "")
    api_key = data.get("apikey", "")
    user_input_examples = data.get("input", "")
    user_input_new_tags = data.get("rename_tags", "")
    user_input_instructions = data.get("additional_info", "")

    table_data = []
    for new_tag_info in user_input_new_tags.split("\n"):
        if not new_tag_info:
            continue
        print(f"For {new_tag_info}")

        try:
            tag_new_name = get_name_from_examples(
                user_input_examples,
                user_input_instructions,
                new_tag_info,
                endpoint,
                api_key,
            )
            print(f"Answer is {tag_new_name}")

            table_data.append(
                {"input_definition": new_tag_info, "new_name": tag_new_name}
            )
        except Exception as e:
            print(f"Error: {e}")
            tag_new_name = "Error"

    # Return the data in JSON format
    return jsonify(table_data)


# New API route to serve the history data dynamically
@app.route("/get-history", methods=["GET"])
def get_history():
    # Simulate history data (can replace this with actual logic)

    history_data = [
        {
            "description": "2023-10-20T14:43Z_Bold_Lion",
            "timestamp": "2024-01-25T00:50:00Z",
        },
        {
            "description": "2023-10-22T16:50Z_Brave_Tiger",
            "timestamp": "2024-01-24T12:52:00Z",
        },
        {
            "description": "2023-10-20T14:43Z_Quiet_Owl",
            "timestamp": "2024-01-23T12:32:00Z",
        },
        {
            "description": "2023-10-20T14:43Z_Mighty_Eagle",
            "timestamp": "2024-01-22T12:05:00Z",
        },
        {
            "description": "2023-10-21T14:43Z_Bright_Star",
            "timestamp": "2024-01-21T12:08:00Z",
        },
        {
            "description": "2023-10-21T14:43Z_Wise_Panda",
            "timestamp": "2024-01-20T12:35:00Z",
        },
        {
            "description": "2023-10-21T14:43Z_Fierce_Tiger",
            "timestamp": "2024-01-19T12:25:00Z",
        },
        {
            "description": "2023-10-21T14:43Z_Gentle_Dove",
            "timestamp": "2024-01-18T12:15:00Z",
        },
    ]

    # Return history data as JSON response
    return jsonify({"history": history_data})


if __name__ == "__main__":
    app.run()
