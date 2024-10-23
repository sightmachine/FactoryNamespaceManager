import os

import io
import csv
import json
from flask import Flask, jsonify, render_template, request, Response

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, AssistantMessage, UserMessage

app = Flask(__name__)


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

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        max_tokens=1000,
        temperature=0,
    )

    user_pre_prompt = f""" 
    You are an AI companion that uses this data to try to predict new names based on provided keywords.
    If you see a number, followed by a dash, followed by a number -- e.g., 1-3 -- these are important parts of the naming.
    In general, pay attention to numbers.  They are often important.

    The following keywords are associated with predefined mappings:
    {user_input_examples}

    {user_input_instructions}

    Answer the following questions:
    1.  What is the best name?
    2.  Why did you choose this name?
    3.  Are there any discrepancies between the use of numbers in the keywords versus in the name?
    4.  How many of the predefined mappings did you use?  Provide a number, followed by a comma, followed by a list of which ones.
    5.  How of the associated keywords did you use?  Provide a number, followed by a comma, followed by a list of which ones.
    6.  How many words were in your list of keywords?  Provide just a number.
    7.  How many characters were in the chosen best name?  Provide just a number.

    ANSWERS:
    1.  The best name is:
    2.  I chose that name because:
    3.  Discrepancies:
    4.  Which mappings:
    5.  Number of keywords:
    6.  Number of words in Keywords:
    7.  Number of characters in the best name.

    """

    assist_reply = "OK, I will assist you with that."
    table_data = []

    for new_tag_info in user_input_new_tags.split("\n"):
        if not new_tag_info:
            continue
        print(f"Doing for {new_tag_info}")
        user_prompt = f""" 
        What is the best name associated with keywords '{new_tag_info}'?
        """

        try:
            response = client.complete(
                messages=[
                    UserMessage(content=user_pre_prompt),
                    AssistantMessage(content=assist_reply),
                    UserMessage(content=user_prompt),
                ],
            )

            tag_new_name = response["choices"][0]["message"]["content"]
            tag_new_name = tag_new_name.strip()
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
