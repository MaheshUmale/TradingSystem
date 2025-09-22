import traceback
import requests
from urllib.parse import parse_qsl

import urllib.parse

def url_encode_sentence(sentence):
  """
  Converts a text sentence into a URL-encoded format, replacing spaces with %20.

  Args:
    sentence: The input text sentence (string).

  Returns:
    The URL-encoded string.
  """
  encoded_sentence = urllib.parse.quote(sentence)
  return encoded_sentence

import json
import re


import json
import re




def remove_markdown_fences(text):
    """
    Removes common Markdown code fences from a string.
    """
    # Define a list of common code fences to remove
    fences = ["```json", "```"]
    
    # Strip whitespace first
    cleaned_text = text.strip()

    # Remove the prefixes and suffixes
    for fence in fences:
        if cleaned_text.startswith(fence):
            cleaned_text = cleaned_text.removeprefix(fence)
        if cleaned_text.endswith(fence):
            cleaned_text = cleaned_text.removesuffix(fence)
    
    # Strip any remaining whitespace
    return cleaned_text.strip()

# Example usage




def parse_google_ai_response(response_text):
    """
    Parses a streaming response from the Google AI API to extract and reconstruct
    the final JSON output.

    Args:
        response_text (str): The raw text of the API's streaming response.

    Returns:
        dict: The final, parsed JSON object as a Python dictionary.
    
    Raises:
        ValueError: If the response cannot be parsed or the final JSON is invalid.
    """
    full_json_string = ""
    lines = response_text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # The lines are formatted with a length header followed by the content.
        # We need to find the start of the JSON array.
        json_match = re.search(r'\[\[.*', line)
        if json_match:
            try:
                # The data is a stringified JSON array. We need to parse it.
                raw_json_chunk = json_match.group(0)
                parsed_data = json.loads(raw_json_chunk)
                
                # Check for the specific nested structure where the output is located.
                # This is based on empirical observation of the API's response format.
                if len(parsed_data) > 0 and isinstance(parsed_data[0], list):
                    # Check for a specific key that often precedes the JSON data.
                    # This helps filter out non-essential parts of the response.
                    if len(parsed_data[0]) > 2 and isinstance(parsed_data[0][2], str):
                        inner_data = json.loads(parsed_data[0][2])
                        
                        # Navigate to the specific path where the string fragments are stored.
                        # The path [4][0][1] is a common pattern for the main response payload.
                        if len(inner_data) > 4 and isinstance(inner_data[4], list):
                            if inner_data[4] and isinstance(inner_data[4][0], list):
                                if len(inner_data[4][0]) > 1 and isinstance(inner_data[4][0][1], list):
                                    string_fragments = inner_data[4][0][1]
                                    stringlist = (string_fragments) 
                                    json_string =""
                                    for s in stringlist:
                                        json_string += remove_markdown_fences(s)
                                    full_json_string = json_string
                                    # print("Current concatenated JSON string:", full_json_string)    

            except (json.JSONDecodeError, IndexError) as e:
                # Silently ignore chunks that don't conform to the expected structure
                # as they are often metadata or control signals.
                continue

    # After iterating through all lines, parse the concatenated string
    if full_json_string:
        try:
            # The final JSON string needs to be properly un-escaped and parsed.
            final_output = json.loads(full_json_string)
            # print("Final parsed JSON output:")
            # print(json.dumps(final_output, indent=2))   
            return final_output
        except json.JSONDecodeError:
            raise ValueError("Failed to parse the final JSON object.")
    else:
        raise ValueError("No parsable JSON content found in the response.")




def parse_google_ai_stream(raw_response_chunks: str) -> dict:
    """
    Parses a fragmented Google AI streaming response to extract the final output,
    which could be a JSON payload or other textual content.

    Args:
        raw_response_chunks (str): The raw streamed response string, potentially containing multiple chunks.

    Returns:
        dict: The final, parsed JSON object, or an empty dictionary if not found.
    """
    cleaned_response = ""
    # Remove length prefixes and process each line to rebuild the full response
    for line in raw_response_chunks.splitlines():
        # Skip lines that are only digits (the length prefix)
        if line and not re.match(r'^\d+$', line):
            cleaned_response += line

    # --- Strategy for extracting the final output ---
    # The output is always encapsulated within the most deeply nested, final array.
    # The final output is likely the *last* content in the cleaned_response string.

    # Regular expression to find the most deeply nested array content
    # This pattern is robust to different content types (JSON or text)
    # It finds the content inside the last `[["wrb.fr",null,"[null,...]]"]]` structure.
    final_output_match = re.search(r'\[\["wrb\.fr",null,"\[(.*)\]"\s*\]\]$', cleaned_response)

    if final_output_match:
        # Extract the content of the final nested array
        inner_content = final_output_match.group(1)
        
        # Try to parse as JSON first
        try:
            # First, un-escape the inner content, as the data is doubly-escaped
            unescaped_content = inner_content.encode('utf-8').decode('unicode_escape')
            
            # Now, attempt a JSON load. This will work for JSON-formatted final responses.
            final_output = json.loads(unescaped_content)
            print("Detected and parsed JSON output.")
            return final_output
            
        except (json.JSONDecodeError, IndexError):
            # If it fails, it's likely a simple text string.
            # In this case, we can try to extract the text from the last part of the response.
            print("Failed to parse as JSON. Extracting as raw text.")
            text_match = re.search(r'\\\"(.*)\\\"\]', inner_content)
            if text_match:
                # Capture the string, un-escape, and return it.
                return {"text": text_match.group(1).encode('utf-8').decode('unicode_escape')}
            else:
                print("Could not find a text string to extract.")
                return {}
    
    print("Could not find a parsable final output in the response.")
    return {}

def extract_from_bard_response(response_text):
    """
    Extracts the last JSON object from a fragmented Google AI on Google Search API response.

    Args:
        response_text (str): The raw streamed response string.

    Returns:
        dict: The extracted JSON object, or None if not found or parsing fails.
    """
    # Use a regular expression to find the JSON strings.
    # The pattern looks for JSON objects within the escaped strings.
    # Note: this is specifically tailored to the given response format.
    json_strings = re.findall(r'\\\"(\\{\\n(?:.*?)\\n\\\"\\})\\\"', response_text)

    if not json_strings:
        print("No JSON objects found in the response.")
        return None

    # Get the last JSON string from the list
    last_json_string = json_strings[-1]

    # Clean up the string by replacing escaped characters.
    # The `unicode_escape` decoder handles `\\\"` and `\\n`.
    cleaned_json_string = last_json_string.encode('utf-8').decode('unicode_escape')

    try:
        # Load the cleaned string into a JSON object.
        return json.loads(cleaned_json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing last JSON: {e}")
        return None






def make_curl_request(ticker, metrics_json):
    """
    Replicates the provided cURL command to Google's Bard/Gemini service.
    """
    # 1. Define the URL from the cURL command
    url = 'https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate?bl=boq_assistant-bard-web-server_20250917.05_p4&f.sid=-456639814663206703&hl=en-GB&_reqid=6379513&rt=c'
    # 2. Define the Headers from the -H arguments
    # Note: Trailing semicolons from the cURL command are removed for correctness.
    headers = {
        'sec-ch-ua-full-version-list': '',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Google Chrome";v="135", "Chromium";v="135", "Not_A Brand";v="24"',
        'sec-ch-ua-bitness': '""',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-mobile': '?0',
        'X-Same-Domain': '1',
        'sec-ch-ua-wow64': '?0',
        'sec-ch-ua-form-factors': '',
        'sec-ch-ua-arch': '""',
        'x-goog-ext-73010989-jspb': '[0]',
        'sec-ch-ua-full-version': '""',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'x-goog-ext-525001261-jspb': '[1,null,null,null,"9ec249fc9ad08861",null,null,0,[4]]',
        'Referer': 'https://gemini.google.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.115 Safari/537.36',
        'sec-ch-ua-platform-version': '""',
    }

    # 3. Define the data payload from the --data-raw argument.
    # The raw data string is parsed into a dictionary, which is the
    # standard way to provide form data to the `requests` library.
    #data_raw = "f.req=%5Bnull%2C%22%5B%5B%5C%22DO%20ANALYSIS%20for%20ticker%3DReliance%20based%20on%20You%20are%20a%20sophisticated%20Stock-Forecasting%20Agent.%20Your%20role%20is%20to%20analyze%20a%20set%20of%20technical%20indicators%20for%20a%20given%20stock%20and%20predict%20the%20most%20likely%20trend%20for%20the%20next%20trading%20day.%5C%5Cn%5C%5CnBased%20on%20the%20following%20technical%20metrics%20for%20the%20stock%20%7Bticker%7D%3A%5C%5Cn%7Bmetrics_json%7D%5C%5Cn%5C%5CnPlease%20provide%20your%20forecast%20in%20the%20following%20JSON%20format%3A%5C%5Cn%7B%7B%5C%5Cn%C2%A0%20%5C%5C%5C%22P_up%5C%5C%5C%22%3A%20%3Cprobability%20of%20uptrend%2C%20float%20between%200.0%20and%201.0%3E%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22P_down%5C%5C%5C%22%3A%20%3Cprobability%20of%20downtrend%2C%20float%20between%200.0%20and%201.0%3E%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22P_side%5C%5C%5C%22%3A%20%3Cprobability%20of%20sideways%20movement%2C%20float%20between%200.0%20and%201.0%3E%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22trend%5C%5C%5C%22%3A%20%5C%5C%5C%22%3C'uptrend'%2C%20'downtrend'%2C%20or%20'sideways'%3E%5C%5C%5C%22%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22reasoning%5C%5C%5C%22%3A%20%5C%5C%5C%22%3Ca%20brief%20explanation%20of%20your%20reasoning%20for%20the%20forecast%3E%5C%5C%5C%22%5C%5Cn%7D%7D%5C%5Cn%5C%5CnThe%20probabilities%20(P_up%2C%20P_down%2C%20P_side)%20must%20sum%20to%201.0.%20The%20'trend'%20should%20be%20the%20one%20with%20the%20highest%20probability.%5C%5CnThe%20output%20must%20be%20only%20the%20JSON%20object%2C%20without%20any%20markdown%20formatting%20like%20%60%60%60json%20...%20%60%60%60.%5C%5Cn%5C%5C%5C%22%5C%5C%5C%22%5C%5C%5C%22%5C%22%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2C0%5D%2C%5B%5C%22en-GB%5C%22%5D%2C%5B%5C%22c_ebdcb1c6664b8d20%5C%22%2C%5C%22r_7a7835e417c461a1%5C%22%2C%5C%22rc_19d7c5c2f07720f9%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22AwAAAAAAAAAQ4DUFz3Xz2P5Pe0nKlhk%5C%22%5D%2C%5C%22!n5ylnMTNAAa-BNTXngRCBTLuScW2GxY7ADQBEArZ1EJGiEsT3wCYQjcg820OWHv_Ifghayv9Lv4ESfCfaeI7DpkgPYP8jXmKmq4PdQgFAgAAAIxSAAAABGgBB34AQRbr2krXt_Nj3zlP22jBxeZNN6gHu4pDwNFTdgxVmCGIPbsT5elH0ZaC4MFIN16PdRupvR_sJbuzFBMcEJpz7LtpmQOHTDyngmg8SVdqj3EOuOc3m5SumuJ1EwRzUsfPY6M_wXbEBAUr6mv7_8jMvr7OKG-o6tWiyrqLafz0jAk4MNkwCmDyVBwJPEATsFrJziNfj_zGsXu-65-3Tyj9V6EmclaffPQxkdhmR-rzvvni8wb_jgz2P70Y2TOeIati0E5IHGQV6aGl9IhTe_Ckv9A8H9lyKKTLpZ-IYY95Fj42sLLgOFPRgoDU1d6IPWCS_sJuYT1ntoCclQNVAVFDUOuk6oGS6zUycsUToLIUOeELP4RqdDA3R89bt-4RkPQDFZIXjc_7xRk6nJ-gMmbyL29WNVAQlQZq5oS-Wo-2pk7Rto_h5wvAjfYA4YhmHjB8hsBOO15D7B4To-53tvNLFQVQQHgo67KAGKHtcX8rLq3r09KyhZ_VTWm7HxZX7YrH5gWp80RGET09x-vWCWXdiItOLLkMGyJr9FJplCYdUn_LGmovdzmMS5hFr5wCqDyidlnSuKX8dcFQGToW3V0LcBR2vuzlVnaeWT5uyPS52JI7lgKwnG_bI5owaxOz2uvqhVjrVuKmNq7F5JwJRdEZ0WuSXvrlmFF2ZCIi1DSY3T154WpQ8lBnxrNiq9EOgNCc_Gfo2z6gLpUpAFLCBRbfs3_A3H4ZJ36Y6uSxy9RphMq0bYuoC0BZtRp6f-OZa_64iwKKctklQYaiyJ6oLWOUBbNrbuLu_6NqffbfmjkYDVUpnLLquMKHFkvg_B3KhbCQXnGv8rRLSuUixlTt5vAURvx7x0dKlOKUtrvf4RQoYbHlb4EEr9dh15dp0q-YlPte17qSd2MqcYP_kHushPfZwlSFXIfA3cgncmcLzVwiPHGMDlisue6TepFJSb7L1qVSFIO7qiecDZg8OlhKQKjp8vEGp3ildlXgoUEW9KQY8uF_3Nc_Zv6p7D15xnMuiTJDTe_VoO-Gu8F_Fld6tWaGGszIeUo-xxYVZreFbeEzY3UyNVFXd6d-UdCs5LYC9In6hbxXZ6P5Bf6SdyBnR7uZ4EHxgscVvWQkyEbe9v-tuHgrvKLAn_WSaoQJkR0eqx8NWAQ1S_0yQTiQBNeB7CE0G2Ec0wf39xpYWhKhfDnwvejDdFMFPIdv-S3i3afwyTf7d2rwXC_ZCYYffXxurDw92ywBLExj2F1XuI-fgLQeeiu8Y4M1kpoU3LWQP-dNI5FDsmcdhdun8KI5TdbL%5C%22%2C%5C%22db29d76a1ae56f2b70d97068365be1a3%5C%22%2Cnull%2C%5B0%5D%2C1%2Cnull%2Cnull%2C1%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B4%5D%5D%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1%2Cnull%2Cnull%2C%5B4%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B1%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C_null%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5D%5D%22%5D&at=AJoiUyNFfC7N-GU7pOQgeb_5EPLK%3A1758464022528&"
    
   
    prompt = f"""
    You are a sophisticated Stock-Forecasting Agent. Your role is to analyze a set of technical indicators for a given stock and predict the most likely trend for the next trading day.
    Based on the following technical metrics for the stock {ticker}:
    {metrics_json}

    Please provide your forecast in the following JSON format:
    {{
    "P_up": <probability of uptrend, float between 0.0 and 1.0>,
    "P_down": <probability of downtrend, float between 0.0 and 1.0>,
    "P_side": <probability of sideways movement, float between 0.0 and 1.0>,
    "trend": "<'uptrend', 'downtrend', or 'sideways'>",
    "reasoning": "<a brief explanation of your reasoning for the forecast>"
    }}

    The probabilities (P_up, P_down, P_side) must sum to 1.0. The 'trend' should be the one with the highest probability.
    The output must be only the JSON object, without any markdown formatting like ```json ... ```.
    """

    promptText=url_encode_sentence(prompt)
    # data_raw = part1+promptText+part3
    
    #print(data_raw  )  # For debugging purposes

    promptText ="You are a sophisticated Stock-Forecasting Agent. Your role is to analyze a set of technical indicators for a given stock and predict the most likely trend for the next trading day. analyse " + ticker + " based on analyst and technical indicators rating for swing trades and give trend for next trading day in json format only with keys P_up, P_down, P_side, trend, reasoning. Probabilities must sum to 1.0 and trend should be the one with highest probability. No markdown formatting."
    promptText = promptText +"Please provide your forecast in the following JSON format:{{P_up: <probability of uptrend, float between 0.0 and 1.0>, P_down: <probability of downtrend, float between 0.0 and 1.0>,P_side: <probability of sideways movement, float between 0.0 and 1.0>,trend: <'uptrend', 'downtrend', or 'sideways'>,reasoning: <a brief explanation of your reasoning for the forecast>}}The probabilities (P_up, P_down, P_side) must sum to 1.0. The 'trend' should be the one with the highest probability.The output must be only the JSON object."
    promptText=url_encode_sentence(promptText)

    RAWDATA = "f.req=%5Bnull%2C%22%5B%5B%5C%22"+promptText+"%5C%22%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2C0%5D%2C%5B%5C%22en-GB%5C%22%5D%2C%5B%5C%22c_ebdcb1c6664b8d20%5C%22%2C%5C%22r_0a8e02235760bdcc%5C%22%2C%5C%22rc_20544167fb2fa1c6%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22AwAAAAAAAAAQ4DUFz3Xz2P5_USnPlhk%5C%22%5D%2C%5C%22!OTqlOmLNAAa-BNTXngRCYhc77f6S-7A7ADQBEArZ1EKPRtNIAqiZ1tu84LgbIZsYApNN6bpszvXM530wwYMj-WWW3Kz5J_Tv_oerOBTBAgAAAH5SAAAAB2gBB34AQYxEiVnF2XdfRYXgl2c4fvrwfqB8UvPXDdoPcpc1z_-zPgN9ciqklx4xXS9ZWx3qrqBWHhm2W8KpF7gvJYMyelqymQOC0JZQadqj6CgXAkcrMaSkL8quaSVcZlQXdSwpoJjk9S0RImZGkt7Fa0kYGC3O9rRaBn1HBu4TelJvfvF633CTWdmy3ecGwnLHF65Rw-5tSIByo7R9rKJ_9MIutZbjOixjN4K-NhScSc1wdPdDbIshz5RXNRRWtbRFjSdLTw_b5ITXsQh7uZtFGtkzh1Sgt0E6sJVOIv8sTOHjlaZ1fLPTnwz8fKTw7g05UUgKXgyNJVRKEvr0x92AA7QLnYHJhY7q1lVJlyeip4oQ_NGuHzofin9O3nyzwj4xCNBJ68fovojSdRrnMoeaNklS3KYMdUx332LoZLD550SZvGghYkCRmPkav5JuaFrejLm-HQNudoimkbWR6WY2jMNEiAHBqWfmTSBMsSotCzX-quU1oiRqnybDNdKDQ4ba--4KJQ77qpBjj1YFqK5LWrmTIDOBNQcwY81IGb_JIgtE0dj3PNuZHxuFyKPlzUf70x87wDPBlIxC-MrV9PbkZYZGr_Y_d_FY4Kj6HKo2gz9lK_ETUaI151jqcsbiLMySMJyoicghac551fUEuaVRu0Xj8q50UbXXX3OtWIooEvHPJz5wpOB3F9za3792p623ewcTg-Rei29N-IRnyPmFUtlnDMaxlzjLNaEFhTWco2XrU-oJWdYVB_zh2XgX_buP3OLWb8a2cS_BWql77a9fBIds-5aGf7Eyb-hvtMolf5wdBuUnisl-TDIQz1oxdkB7UShofMkSV8NJfiIMSAYsGXu9TdsSQbTMrZGyH97PZvUY65xGFXU7SZLKHtjjTs8EogfCTKQYTHKtDox605BLPgZqPGLm4ZESYSJ2wZqDZVvGGrQWS-rk5e5clEuEw2Ui5nKXzHYGpXthROulzpe_BB5NufzfNiL7cmKc1mjxuoV6d4tA75JL_RkzoIUztMlXB1W8nScOrUgsa3g1mLvZ2ulOPFoIwZbzZHVjDYGfQTq_bcPktF7REhZdMApExq72we09J1sLSGonob-lkorwzztRjMqIGH77kRkZI6nD8C-OS2QgrlxLJtd8h45eWlvsFk3LTg8EL-Rf_PcoF1jyvopYqH3sEfBi6S5-FJ7s-00HQTzaWBsGTlTTFXhwQO5S6qq_EKohIJl818-hRac0b8XbHjUnd5SZnzuDC7RQeh7KfeBEpYmATgM-U_Bz798tFerWShjmydFSVA%5C%22%2C%5C%22517cfe4d26dd2de09eaf707174605cd7%5C%22%2Cnull%2C%5B0%5D%2C1%2Cnull%2Cnull%2C1%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B6%5D%5D%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1%2Cnull%2Cnull%2C%5B4%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B1%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5D%5D%22%5D&at=AJoiUyMApCx3L84IzB-LGRCWYdO9%3A1758466656691&"
    data_raw=RAWDATA
    data = dict(parse_qsl(data_raw))
    #print(data)  # For debugging purposes
    try:
        # 4. Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # 5. Print the response
        print("Request successful!")
        print(f"Status Code: {response.status_code}")
        # print("Response Text:")
        # print(response)
        response_text=response.content.decode('utf-8')
        print(response_text)
        
        
        
        # Initialize an empty string to store the full response
        full_response = ""
         
        try:
            parsed_json = parse_google_ai_response(response_text)
            full_response = json.dumps(parsed_json, indent=2)
            print("Extracted JSON from response:")
            print(full_response)    
            print()
        except ValueError as e:
            print(f"Error: {e}")
            traceback.print_exc()
        # return {"error": str(e)}

        
           

        forecast = json.loads(full_response)

        required_keys = ["P_up", "P_down", "P_side", "trend", "reasoning"]
        if not all(key in forecast for key in required_keys):
            raise ValueError("Forecast JSON is missing required keys.")
        print("Forecast JSON is valid and contains all required keys.")
        return forecast

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return {"error": str(e)}




def make_curl_requestWithPrompt(promptText: str) -> dict:
    """
    Replicates the provided cURL command to Google's Bard/Gemini service.
    """
    # 1. Define the URL from the cURL command
    url = 'https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate?bl=boq_assistant-bard-web-server_20250917.05_p4&f.sid=-456639814663206703&hl=en-GB&_reqid=6379513&rt=c'
    # 2. Define the Headers from the -H arguments
    # Note: Trailing semicolons from the cURL command are removed for correctness.
    headers = {
        'sec-ch-ua-full-version-list': '',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Google Chrome";v="135", "Chromium";v="135", "Not_A Brand";v="24"',
        'sec-ch-ua-bitness': '""',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-mobile': '?0',
        'X-Same-Domain': '1',
        'sec-ch-ua-wow64': '?0',
        'sec-ch-ua-form-factors': '',
        'sec-ch-ua-arch': '""',
        'x-goog-ext-73010989-jspb': '[0]',
        'sec-ch-ua-full-version': '""',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'x-goog-ext-525001261-jspb': '[1,null,null,null,"9ec249fc9ad08861",null,null,0,[4]]',
        'Referer': 'https://gemini.google.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.115 Safari/537.36',
        'sec-ch-ua-platform-version': '""',
    }

    # 3. Define the data payload from the --data-raw argument.
    # The raw data string is parsed into a dictionary, which is the
    # standard way to provide form data to the `requests` library.
 

    RAWDATA = "f.req=%5Bnull%2C%22%5B%5B%5C%22"+promptText+"%5C%22%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2C0%5D%2C%5B%5C%22en-GB%5C%22%5D%2C%5B%5C%22c_ebdcb1c6664b8d20%5C%22%2C%5C%22r_0a8e02235760bdcc%5C%22%2C%5C%22rc_20544167fb2fa1c6%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22AwAAAAAAAAAQ4DUFz3Xz2P5_USnPlhk%5C%22%5D%2C%5C%22!OTqlOmLNAAa-BNTXngRCYhc77f6S-7A7ADQBEArZ1EKPRtNIAqiZ1tu84LgbIZsYApNN6bpszvXM530wwYMj-WWW3Kz5J_Tv_oerOBTBAgAAAH5SAAAAB2gBB34AQYxEiVnF2XdfRYXgl2c4fvrwfqB8UvPXDdoPcpc1z_-zPgN9ciqklx4xXS9ZWx3qrqBWHhm2W8KpF7gvJYMyelqymQOC0JZQadqj6CgXAkcrMaSkL8quaSVcZlQXdSwpoJjk9S0RImZGkt7Fa0kYGC3O9rRaBn1HBu4TelJvfvF633CTWdmy3ecGwnLHF65Rw-5tSIByo7R9rKJ_9MIutZbjOixjN4K-NhScSc1wdPdDbIshz5RXNRRWtbRFjSdLTw_b5ITXsQh7uZtFGtkzh1Sgt0E6sJVOIv8sTOHjlaZ1fLPTnwz8fKTw7g05UUgKXgyNJVRKEvr0x92AA7QLnYHJhY7q1lVJlyeip4oQ_NGuHzofin9O3nyzwj4xCNBJ68fovojSdRrnMoeaNklS3KYMdUx332LoZLD550SZvGghYkCRmPkav5JuaFrejLm-HQNudoimkbWR6WY2jMNEiAHBqWfmTSBMsSotCzX-quU1oiRqnybDNdKDQ4ba--4KJQ77qpBjj1YFqK5LWrmTIDOBNQcwY81IGb_JIgtE0dj3PNuZHxuFyKPlzUf70x87wDPBlIxC-MrV9PbkZYZGr_Y_d_FY4Kj6HKo2gz9lK_ETUaI151jqcsbiLMySMJyoicghac551fUEuaVRu0Xj8q50UbXXX3OtWIooEvHPJz5wpOB3F9za3792p623ewcTg-Rei29N-IRnyPmFUtlnDMaxlzjLNaEFhTWco2XrU-oJWdYVB_zh2XgX_buP3OLWb8a2cS_BWql77a9fBIds-5aGf7Eyb-hvtMolf5wdBuUnisl-TDIQz1oxdkB7UShofMkSV8NJfiIMSAYsGXu9TdsSQbTMrZGyH97PZvUY65xGFXU7SZLKHtjjTs8EogfCTKQYTHKtDox605BLPgZqPGLm4ZESYSJ2wZqDZVvGGrQWS-rk5e5clEuEw2Ui5nKXzHYGpXthROulzpe_BB5NufzfNiL7cmKc1mjxuoV6d4tA75JL_RkzoIUztMlXB1W8nScOrUgsa3g1mLvZ2ulOPFoIwZbzZHVjDYGfQTq_bcPktF7REhZdMApExq72we09J1sLSGonob-lkorwzztRjMqIGH77kRkZI6nD8C-OS2QgrlxLJtd8h45eWlvsFk3LTg8EL-Rf_PcoF1jyvopYqH3sEfBi6S5-FJ7s-00HQTzaWBsGTlTTFXhwQO5S6qq_EKohIJl818-hRac0b8XbHjUnd5SZnzuDC7RQeh7KfeBEpYmATgM-U_Bz798tFerWShjmydFSVA%5C%22%2C%5C%22517cfe4d26dd2de09eaf707174605cd7%5C%22%2Cnull%2C%5B0%5D%2C1%2Cnull%2Cnull%2C1%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B6%5D%5D%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1%2Cnull%2Cnull%2C%5B4%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B1%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5D%5D%22%5D&at=AJoiUyMApCx3L84IzB-LGRCWYdO9%3A1758466656691&"
    data_raw=RAWDATA
    data = dict(parse_qsl(data_raw))
    # print(data)  # For debugging purposes
    try:
        # 4. Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # 5. Print the response
        # print("Request successful!")
        # print(f"Status Code: {response.status_code}")
        # print("Response Text:")
        # print(response)
        response_text=response.content.decode('utf-8')
        # print(response_text)
        
        
        
        # Initialize an empty string to store the full response
        full_response = ""
         
        try:
            parsed_json = parse_google_ai_response(response_text)
            full_response = json.dumps(parsed_json, indent=2)
            # print("Extracted JSON from response:")
            # print(full_response)    
            # print()
        except ValueError as e:
            print(f"Error: {e}")
            traceback.print_exc()
        
           
 
        
        return full_response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
def make_curl_requestForFinancialReportAnalysis(ticker :str):
    financial_prompt = f"Analyze the financial reports of the following STOCK = {ticker}: ."
    financial_prompt += "You must output key financial metrics including revenue growth, profit margins, and any potential risks."
    financial_prompt += " The output must be in JSON format with keys 'revenue_growth_qoq', 'net_profit_margin', 'debt_to_equity', and 'potential_risks'."
    financial_prompt += " Ensure that your response is strictly in JSON format without any additional commentary or formatting."
    financialResponse = make_curl_requestWithPrompt(financial_prompt)
    print("Financial Report Analysis Response:")
    print(financialResponse)
    return financialResponse

def make_curl_requestForSentimentAnalysis(ticker :str):

    sentiment_prompt = f"Analyze the sentiment of the following STOCK = {ticker}: ."
    sentiment_prompt += "You must output a sentiment score for  stock ranging from -100 (extremely negative) to +100 (extremely positive), and provide brief and crisp reasoning for this score based on the research."
    # Step by Step instructions for calculating SCORE
    sentiment_prompt += "1. Carefully read through the entire Research Findings provided in Conduct Deep Research."
    sentiment_prompt += "2. Identify all positive, negative, and neutral indicators within the Research Findings that relate to the stock's sentiment."
    sentiment_prompt += "3. Weigh the impact of each indicator, considering its source, recency, and potential influence on the stock."
    sentiment_prompt += "4. Based on your analysis, determine an overall sentiment score for the stock, ranging from -100 (extremely negative) to +100 (extremely positive)."
    sentiment_prompt += "5. Write a brief and crisp explanation and reasoning for the assigned sentiment score, directly referencing specific elements from the Research Findings to support your conclusion."
    sentiment_prompt += "6. Review the sentiment score and reasoning. Does it accurately reflect the Research Findings and fully justify the score in a brief and crisp manner? If not, go back to step 2 and refine your analysis and reasoning."
    sentiment_prompt += " Provide a sentiment score between -1 (very negative) and 1 (very positive), along with a brief explanation of the sentiment."
    sentiment_prompt += " The output must be in JSON format with keys 'sentiment_score' and 'explanation'."
    sentiment_prompt += " Ensure that your response is strictly in JSON format without any additional commentary or formatting."
    # sentiment_prompt += " TEXT TO ANALYZE: " +  json.loads(deepResearchResponse)['deepAnalysisexplanation']
    sentimentResponse = make_curl_requestWithPrompt(sentiment_prompt)
    print("Sentiment Analysis Response:")
    print(sentimentResponse)
    return sentimentResponse


if __name__ == "__main__":
    ticker = "BAJAJ-AUTO"
    metrics_json = "{\"SMA_20\": 250.5, \"SMA_50\": 245.3, \"SMA_200\": 240.1, \"EMA_20\": 251.0, \"EMA_50\": 246.0, \"EMA_200\": 241.0, \"RSI_14\": 65.2, \"MACD\": 1.5, \"MACD_Signal\": 1.2, \"Bollinger_Bands\": {\"Upper\": 255.0, \"Middle\": 250.0, \"Lower\": 245.0}, \"Volume\": 1500000}"
    # make_curl_request(ticker, metrics_json)
    # deepresearch = "Conduct in-depth research using the generated query to gather social media discussions, news articles, and stock reports related to the specified stock. The research should cover nseindia.com and other relevant financial platforms."
    deepresearch = f"You are an expert financial analyst specializing in sentiment analysis for stocks. Your task is to meticulously review the provided research findings to determine the overall sentiment for  given stock ticker = {ticker}."
    deepresearch += "The sentiment should be quantified on a scale from -100 (extremely negative) to +100 (extremely positive)."
    deepresearch += "Your analysis should consider various factors, including but not limited to market trends, news articles, social media discussions, and expert opinions."
    deepresearch += "Provide a clear and very concise explanation for the assigned sentiment score, highlighting key points from the research that influenced your decision."
    deepresearch += "Your output must be in JSON format with the keys 'deepAnalysisScore' and 'deepAnalysisexplanation'."
    deepresearch += " Ensure that your response is strictly in JSON format without any additional commentary or formatting."
    deepresearch += " restrict explanation to max 10 statements from each section/sector,summarizing key points only."


    deepResearchResponse = make_curl_request(ticker=ticker,metrics_json=metrics_json)
    print("Deep Research Response:")
    print(deepResearchResponse)
    
    
    
