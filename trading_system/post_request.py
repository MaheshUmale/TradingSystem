import requests
import json

def simulate_post_request():
    """
    Simulates the POST request as described by the user-provided
    headers and payload.
    """
    # The target URL for the POST request
    url = "https://opal.withgoogle.com/board/proxy"

    # The headers for the request. We select the most relevant ones that the
    # server is likely to check.
    headers = {
        'content-type': 'text/plain;charset=UTF-8',
        'referer': 'https://opal.withgoogle.com/?flow=drive:/1cLrnQ-DHTtD-Jgy0bT2QovLbOd8y6dO0&mode=app',
        'sec-ch-ua': '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0'
    }

    # The payload for the request, structured as a Python list containing a
    # string and a dictionary, matching the provided format.
    #
    # IMPORTANT: The Authorization Bearer token is likely expired.
    # You will need to replace it with a valid token for the request to work.
    payload_dict = ["proxy", {
        "node": {
            "id": "fetch-called-from-run-module",
            "type": "fetch"
        },
        "inputs": {
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            "method": "POST",
            "headers": {
                 
                 
            },
            "body": {
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
        }
    }]

    # Since the 'content-type' is 'text/plain', we must serialize the payload
    # dictionary to a JSON formatted string before sending it.
    payload_str = json.dumps(payload_dict)

    try:
        # Send the POST request with the specified url, headers, and data.
        # We use the 'data' parameter because we are sending a pre-formatted string.
        response = requests.post(url, headers=headers, data=payload_str.encode('utf-8'))

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Print the results
        print(f"Request successful!")
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        # The response is text/event-stream, so we print it as text.
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # To run this script, you need to have the 'requests' library installed.
    # You can install it by running: pip install requests
    simulate_post_request()
