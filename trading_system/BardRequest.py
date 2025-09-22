import requests
import urllib.parse

def generate_bard_request():
    """
    Replicates the PowerShell Invoke-WebRequest to Google's Bard/Gemini service.
    """
    # 1. Define the URL, including all query parameters
    url = "https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate?bl=boq_assistant-bard-web-server_20250917.05_p4&f.sid=-3620611722600704078&hl=en-GB&_reqid=4071025&rt=c"

    # 2. Define the Headers, transcribed from the PowerShell command
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.115 Safari/537.36",
        "sec-ch-ua-full-version-list": "",
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua": '"Google Chrome";v="135", "Chromium";v="135", "Not_A Brand";v="24"',
        "sec-ch-ua-bitness": '""',
        "sec-ch-ua-model": '""',
        "sec-ch-ua-mobile": "?0",
        "X-Same-Domain": "1",
        "sec-ch-ua-wow64": "?0",
        "sec-ch-ua-form-factors": "",
        "sec-ch-ua-arch": '""',
        "x-goog-ext-73010989-jspb": "[0]",
        "sec-ch-ua-full-version": '""',
        "x-goog-ext-525001261-jspb": '[1,null,null,null,"9ec249fc9ad08861",null,null,0,[4]]',
        "Referer": "https://gemini.google.com/",
        "sec-ch-ua-platform-version": '""',
        # The Content-Type is important for form data.
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }



    f_req_value = (
        '[null,"[[\\"DO ANALYSIS for ticker=Reliance based on You are a sophisticated Stock-Forecasting '
        'Agent. Your role is to analyze a set of technical indicators for a given stock and predict '
        'the most likely trend for the next trading day.    Based on the following technical '
        'metrics for the stock {ticker}:  {metrics_json}    Please provide your forecast in '
        'the following JSON format:  {{     \\"P_up  \\": <probability of uptrend, float '
        'between 0.0 and 1.0>,     \\"P_down  \\": <probability of downtrend, float '
        'between 0.0 and 1.0>,     \\"P_side  \\": <probability of sideways movement, '
        'float between 0.0 and 1.0>,     \\"trend  \\": <\\\\uptrend\\\ \\\\downtrend\\', 'or \\\\sideways\\>,     \\"reasoning  \\": <a brief explanation of your reasoning '
        'for the forecast>  }}    The probabilities (P_up, P_down, P_side) must sum to 1.0. '
        "The \\'trend\\' should be the one with the highest probability.  The output must be only "
        'the JSON object, without any markdown formatting like ```json ... ```.    \"  \"  \\"\\\\"\\",0,null,null,null,null,0],[\\"en-GB\\"],'
        '[\\"c_ebdcb1c6664b8d20\\",\\"r_7a7835e417c461a1\\",\\"rc_19d7c5c2f07720f9\\",null,null,null,null,null,null,\\"AwAAAAAAAAAQ4DUFz3Xz2P5Pe0nKlhk\\"],'
        '\\"!n5ylnMTNAAa-BNTXngRCBTLuScW2GxY7ADQBEArZ1EJGiEsT3wCYQjcg820OWHv_Ifghayv9Lv4ESfCfaeI7DpkgPYP8jXmKmq4PdQgFAgAAAIxSAAAABGgBB34AQRbr2krXt_Nj3zlP22jBxeZNN6gHu4pDwNFTdgxVmCGIPbsT5elH0ZaC4MFIN16PdRupvR_sJbuzFBMcEJpz7LtpmQOHTDyngmg8SVdqj3EOuOc3m5SumuJ1EwRzUsfPY6M_wXbEBAUr6mv7_8jMvr7OKG-o6tWiyrqLafz0jAk4MNkwCmDyVBwJPEATsFrJziNfj_zGsXu-65-3Tyj9V6EmclaffPQxkdhmR-rzvvni8wb_jgz2P70Y2TOeIati0E5IHGQV6aGl9IhTe_Ckv9A8H9lyKKTLpZ-IYY95Fj42sLLgOFPRgoDU1d6IPWCS_sJuYT1ntoCclQNVAVFDUOuk6oGS6zUycsUToLIUOeELP4RqdDA3R89bt-4RkPQDFZIXjc_7xRk6nJ-gMmbyL29WNVAQlQZq5oS-Wo-2pk7Rto_h5wvAjfYA4YhmHjB8hsBOO15D7B4To-53tvNLFQVQQHgo67KAGKHtcX8rLq3r09KyhZ_VTWm7HxZX7YrH5gWp80RGET09x-vWCWXdiItOLLkMGyJr9FJplCYdUn_LGmovdzmMS5hFr5wCqDyidlnSuKX8dcFQGToW3V0LcBR2vuzlVnaeWT5uyPS52JI7lgKwnG_bI5owaxOz2uvqhVjrVuKmNq7F5JwJRdEZ0WuSXvrlmFF2ZCIi1DEY3T154WpQ8lBnxrNiq9EOgNCc_Gfo2z6gLpUpAFLCBRbfs3_A3H4ZJ36Y6uSxy9RphMq0bYuoC0BZtRp6f-OZa_64iwKKctklQYaiyJ6oLWOUBbNrbuLu_6NqffbfmjkYDVUpnLLquMKHFkvg_B3KhbCQXnGv8rRLSuUixlTt5vAURvx7x0dKlOKUtrvf4RQoYbHlb4EEr9dh15dp0q-YlPte17qSd2MqcYP_kHushPfZwlSFXIfA3cgncmcLzVwiPHGMDlisue6TepFJSb7L1qVSFIO7qiecDZg8OlhKQKjp8vEGp3ildlXgoUEW9KQY8uF_3Nc_Zv6p7D15xnMuiTJDTe_VoO-Gu8F_Fld6tWaGGszIeUo-xxYVZreFbeEzY3UyNVFXd6d-UdCs5LYC9In6hbxXZ6P5Bf6SdyBnR7uZ4EHxgscVvWQkyEbe9v-tuHgrvKLAn_WSaoQJkR0eqx8NWAQ1S_0yQTiQBNeB7CE0G2Ec0wf39xpYWhKhfDnwvejDdFMFPIdv-S3i3afwyTf7d2rwXC_ZCYYffXxurDw92ywBLExj2F1XuI-fgLQeeiu8Y4M1kpoU3LWQP-dNI5FDsmcdhdun8KI5TdbL\\",\\"db29d76a1ae56f2b70d97068365be1a3\\",null,[0],1,null,null,1,0,null,null,null,null,null,[[4]],0,null,null,null,null,null,null,null,null,1,null,null,[4],null,null,null,null,null,null,null,null,null,null,[1],null,null,null,null,null,null,null,null,null,null,null,0,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,[]]]'
    )
    ticker = "RELIANCE"
    metrics_json = '{"RSI": 55.2, "MACD": 1.5, "SMA_50": 2500.0, "SMA_200": 2450.0, "Volume": 3000000}'
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

        # 3. Define the Body Data (form data)
        # The 'f.req' value is a complex, stringified JSON structure.
        # We pass it as a string within the data dictionary.   
        
    at_value = "AJoiUyNFfC7N-GU7pOQgeb_5EPLK:1758464022528"

        # The body needs to be a dictionary for the 'data' parameter
    body_data = {
            "f.req": f_req_value,
            "at": at_value,
        }

    try:
        # 4. Send the POST request
        # Using the 'data' parameter tells 'requests' to form-encode the payload.
        response = requests.post(url, headers=headers, data=body_data)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # 5. Print the response
        print("Request successful!")
        print(f"Status Code: {response.status_code}")
        print("Response Text:")
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_bard_request()
