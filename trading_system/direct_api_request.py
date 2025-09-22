import requests
import json

def make_direct_api_call():
    """
    Simulates a direct POST request to the Google Generative Language API.
    """
    # 1. Define the request URL
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    # 2. Define the request headers
    # IMPORTANT: The Authorization Bearer token is likely expired.
    # You will need to replace it with a valid token for the request to work.
    headers = {
        "Authorization": "Bearer <PLACEHOLDER>"
        "Content-Type": "application/json",
    }

    # 3. Define the request body (payload)
    payload = {
        "contents": [{
            "parts": [{
                "text": "You are an expert financial data parser and researcher. Your task is to process a `stock_input` to identify individual stock symbols/names. If the input is an index name, you will use <not_callable_tool>deep_research</not_callable_tool> to find all its constituent stock symbols/names. Your final output must be a comma-separated list of all identified individual stock symbols/names, without any additional text or delimiters.\n# Step by Step instructions\n1. Examine the Stock Input to determine if it is a single stock symbol/name, a list of stock symbols/names, or an index name.\n2. If the Stock Input is an index name, use <not_callable_tool>deep_research</not_callable_tool> to find all the constituent stock symbols/names for that index.\n3. Consolidate all identified individual stock symbols/names into a single list.\n4. Format the list of stock symbols/names as a comma-separated string, ensuring there are no additional text or delimiters.\n5. Output the comma-separated list of stock symbols/names.\n\n\nStock Input:\n\"\"\"\nbajaj auto\n\"\"\"\nIMPORTANT NOTE: Start directly with the output, do not output any delimiters.\nOutput:\n"
            }],
            "role": "user"
        }],
        "safetySettings": [
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ],
        "generationConfig": {
            "responseSchema": {
                "type": "object",
                "properties": {
                    "list": {
                        "type": "array",
                        "description": "The list of results",
                        "items": {
                            "type": "string",
                            "description": "Result list item as markdown text"
                        }
                    }
                },
                "required": ["list"]
            },
            "responseMimeType": "application/json"
        },
        "systemInstruction": {
            "parts": [{
                "text": "\n  \n\nToday is 09/21/2025, 01:05:54 PM\n    \nYou are working as part of an AI system, so no chit-chat and no explaining what you're doing and why.\nDO NOT start with \"Okay\", or \"Alright\" or any preambles. Just the output, please.\n\n  Output as a list of items, each item must be markdown text.\n"
            }],
            "role": "user"
        }
    }

    try:
        # 4. Send the POST request
        # We use the 'json' parameter, which tells 'requests' to automatically
        # serialize the payload dictionary to a JSON string and set the
        # 'Content-Type' header to 'application/json'.
        response = requests.post(url, headers=headers, json=payload)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # 5. Print the results
        print("Request successful!")
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        # The response from the API is expected to be JSON.
        # We use response.json() to parse it and json.dumps to print it nicely.
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError:
        # This will happen if the response is not valid JSON
        print("Failed to decode JSON from response.")
        print(f"Response Text: {response.text}")


if __name__ == "__main__":
    # To run this script, you need to have the 'requests' library installed.
    # You can install it by running: pip install requests
    make_direct_api_call()
