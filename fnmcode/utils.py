import time
import urllib.request
import urllib.error
from functools import wraps


def timing_decorator(func):
    """
    A decorator to measure the execution time of a function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Record the start time
        start_time = time.time()

        # Call the original function
        result = func(*args, **kwargs)

        # Record the end time
        end_time = time.time()

        # Calculate and print the execution time
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time:.4f} seconds")

        return result

    return wrapper


# Retry logic for handling non-200 status codes
def make_request_with_retries(req, max_retries=5, retry_delay=1):
    retries = 0
    while retries < max_retries:
        try:
            response = urllib.request.urlopen(req)
            return response
        except urllib.error.HTTPError as error:
            # print(error.info())
            # print(error.read().decode("utf8", "ignore"))
            # Retry on 429 (Too Many Requests) and other non-200 status codes
            if error.code in [429, 500]:
                retries += 1
                print(
                    f"Received status code {error.code}. Retrying attempt {retries} .."
                )
                # time.sleep(retry_delay)
            else:
                print(
                    f"Request failed with status code {error.code}. No retry will be attempted."
                )
                raise error
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
    # If we reach here, retries have been exhausted
    print("Max retries reached. Failing the request.")
    raise Exception("Max retries reached for the request.")
