import os
import threading
import concurrent.futures
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from typing import List
from faker import Faker
from sqlalchemy.exc import IntegrityError

from . import db
from .utils import timing_decorator, make_request_with_retries
from fnmcode.models import FNMSessions

main = Blueprint("main", __name__)
fake = Faker()

current_file_path = os.path.abspath(__file__)
project_dir = os.path.dirname(current_file_path)
main_dir = os.path.dirname(project_dir)


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

    response = make_request_with_retries(req)

    result = response.read()
    return json.loads(result)["output"].strip()


@main.route("/")
def index():
    """
    Index page for Factory Namespace Manager

    Returns:
        Response: Rendered HTML page for the Factory Namespace Manager.
    """
    return render_template("index.html")


def generate_session_name():
    """Function to generate session name"""
    random_words = fake.words(2)
    capitalized_words = [word.capitalize() for word in random_words]
    session_name = "_".join(capitalized_words)
    # Get the current UTC time and format it
    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    session_name = f"{session_name}_{current_timestamp}"
    return session_name


@main.route("/fnmpage", methods=["GET", "POST"])
@login_required
def fnmpage():
    """
    Web form of the main user input for Factory Namespace Manager

    Returns:
        Response: Rendered HTML page for the Factory Namespace Manager.
    """
    if request.method == "POST":
        # Get data from the form
        example_data = request.form.get("example_data")
        additional_instructions = request.form.get("additional_instructions")
        variables = request.form.get("variables")

        # For now, print to console (later replace with logic)
        print(f"Example Data: {example_data}")
        print(f"Additional Instructions: {additional_instructions}")
        print(f"Variables: {variables}")
    sample_input_content = ""
    sample_output_content = ""
    api_key = ""
    api_endpoint = ""
    if current_user.name == "demo":
        demo_sample_input = f"{project_dir}/demo_input.txt"
        with open(demo_sample_input, "r") as file:
            sample_input_content = file.read().strip()

        demo_sample_output = f"{project_dir}/demo_output.txt"
        with open(demo_sample_output, "r") as file:
            sample_output_content = file.read().strip()

        api_key = "rISeEPawBAuuG59K2MGfqp5aFMsLhWB0"
        api_endpoint = "https://fnm-5630-bbfga.eastus2.inference.ml.azure.com/score"

    session_name = generate_session_name()

    return render_template(
        "fnm.html",
        sample_input_content=sample_input_content,
        sample_output_content=sample_output_content,
        api_key=api_key,
        api_endpoint=api_endpoint,
        session_name=session_name,
    )


@main.route("/license")
def get_license():
    """
    Render the license agreement page.

    Returns:
        Response: Rendered HTML page for the license agreement.
    """

    return render_template("license_agreement.html")


@login_required
@main.route("/generate-table", methods=["POST"])
@timing_decorator
def generate_table():
    """
    Generate the table of new tag names based on the user input.

    Returns:
        Response: JSON response containing the table data.
    """
    # Get the input from the user
    data = request.get_json()
    endpoint = data.get("endpointurl", "")
    api_key = data.get("apikey", "")
    user_input_examples = data.get("input", "")
    user_input_new_tags = data.get("rename_tags", "")
    user_input_instructions = data.get("additional_info", "")
    session_name = data.get("session_name", generate_session_name())

    # Get the configurable number of threads (default to 3 if not provided)
    num_threads = int(data.get("num_threads", 3))

    # Initialize an empty list to store the results
    table_data = []

    # Use a thread lock to safely append to the table_data from multiple threads
    lock = threading.Lock()

    def process_new_tag(new_tag_info):
        # This function will process a single new_tag_info in parallel
        if not new_tag_info:
            return None

        try:
            tag_new_name = get_name_from_examples(
                user_input_examples,
                user_input_instructions,
                new_tag_info,
                endpoint,
                api_key,
            )
            print(f"For {new_tag_info} Answer is {tag_new_name}")

            # Return the result to be appended to table_data
            return {"input_definition": new_tag_info, "new_name": tag_new_name}

        except Exception as e:
            print(f"Error: {e}")
            return {"input_definition": new_tag_info, "new_name": "Error"}

    # Use ThreadPoolExecutor to process each new_tag_info in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Start parallel execution of the tasks
        futures = [
            executor.submit(process_new_tag, new_tag_info)
            for new_tag_info in user_input_new_tags.split("\n")
        ]

        # Collect the results as they complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                with lock:
                    table_data.append(result)

    # After processing, create a session for this user
    existing_session = FNMSessions.query.filter_by(
        name=session_name, user_id=current_user.id
    ).first()

    if existing_session:
        existing_session.inputs = user_input_examples
        existing_session.instructions = user_input_instructions
        existing_session.tags = user_input_new_tags
    else:
        new_session = FNMSessions(
            name=session_name,
            inputs=user_input_examples,
            instructions=user_input_instructions,
            tags=user_input_new_tags,
            user_id=current_user.id,
        )
        db.session.add(new_session)
    db.session.commit()

    # Return the data in JSON format
    return jsonify(table_data)


# New API route to serve the history data dynamically
@login_required
@main.route("/get-history", methods=["GET"])
def get_history():
    """
    Returns a history of user saved sessions
    """
    # Query session
    sessions = (
        FNMSessions.query.filter_by(user_id=current_user.id)
        .order_by(FNMSessions.created_at.desc())
        .all()
    )

    history_data = [
        {
            "id": session.id,
            "description": session.name,
            "timestamp": session.created_at.isoformat(),
        }
        for session in sessions
    ]

    # Return history data as JSON response
    return jsonify({"history": history_data})


@main.route("/delete-history/<session_id>", methods=["DELETE"])
@login_required  # Ensures the user is logged in
def delete_history(session_id):
    # Find the session by its ID
    session = FNMSessions.query.filter_by(id=session_id).first()

    # If session not found, return 404
    if not session:
        # flash("Session not found")
        return jsonify({"error": "Session not found"}), 404

    # Check if the current user ID matches the session's user_id
    if int(session.user_id) != current_user.id:
        # flash("Unauthorized !!")
        return jsonify({"error": "Unauthorized"}), 403

    # Delete the session from the database
    try:
        db.session.delete(session)
        db.session.commit()
        # flash("Session deleted successfully")
        return jsonify({"message": "Session deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        # flash(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@main.route("/view-history/<session_id>", methods=["GET"])
@login_required  # Ensures the user is logged in
def view_history(session_id):
    # Find the session by its ID
    session = FNMSessions.query.filter_by(id=session_id).first()

    # If session not found, return 404
    if not session:
        # flash("Session not found")
        return jsonify({"error": "Session not found"}), 404

    # Check if the current user ID matches the session's user_id
    if int(session.user_id) != current_user.id:
        # flash("Unauthorized !!")
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(
        {
            "session_name": session.name,
            "sample_input_content": session.inputs,
            "sample_output_content": session.tags,
            "sample_instructions": session.instructions,
        }
    )
