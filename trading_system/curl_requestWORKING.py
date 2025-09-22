import requests
from urllib.parse import parse_qsl

def print_dict_recursive(d, indent=0):
    """
    Recursively prints the keys and values of a dictionary, handling nested dictionaries.

    Args:
        d (dict): The dictionary to print.
        indent (int): The current indentation level for pretty printing.
    """
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{'  ' * indent}{key}:")
            print_dict_recursive(value, indent + 1)
        else:
            print(f"{'  ' * indent}{key}: {value}")

# Example usage:
nested_dict = {
    'person': {
        'name': 'Alice',
        'age': 30,
        'address': {
            'city': 'Wonderland',
            'zip': '12345'
        }
    },
    'company': {
        'name': 'Acme Corp',
        'employees': 100
    },
    'status': 'active'
}



def make_curl_request():
    """
    Replicates the provided cURL command to Google's Bard/Gemini service.
    """
    # 1. Define the URL from the cURL command
    url = 'https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate?bl=boq_assistant-bard-web-server_20250917.05_p4&f.sid=-456639814663206703&hl=en-GB&_reqid=8379513&rt=c'

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
    data_raw = "f.req=%5Bnull%2C%22%5B%5B%5C%22DO%20ANALYSIS%20for%20ticker%3DReliance%20based%20on%20You%20are%20a%20sophisticated%20Stock-Forecasting%20Agent.%20Your%20role%20is%20to%20analyze%20a%20set%20of%20technical%20indicators%20for%20a%20given%20stock%20and%20predict%20the%20most%20likely%20trend%20for%20the%20next%20trading%20day.%5C%5Cn%5C%5CnBased%20on%20the%20following%20technical%20metrics%20for%20the%20stock%20%7Bticker%7D%3A%5C%5Cn%7Bmetrics_json%7D%5C%5Cn%5C%5CnPlease%20provide%20your%20forecast%20in%20the%20following%20JSON%20format%3A%5C%5Cn%7B%7B%5C%5Cn%C2%A0%20%5C%5C%5C%22P_up%5C%5C%5C%22%3A%20%3Cprobability%20of%20uptrend%2C%20float%20between%200.0%20and%201.0%3E%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22P_down%5C%5C%5C%22%3A%20%3Cprobability%20of%20downtrend%2C%20float%20between%200.0%20and%201.0%3E%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22P_side%5C%5C%5C%22%3A%20%3Cprobability%20of%20sideways%20movement%2C%20float%20between%200.0%20and%201.0%3E%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22trend%5C%5C%5C%22%3A%20%5C%5C%5C%22%3C'uptrend'%2C%20'downtrend'%2C%20or%20'sideways'%3E%5C%5C%5C%22%2C%5C%5Cn%C2%A0%20%5C%5C%5C%22reasoning%5C%5C%5C%22%3A%20%5C%5C%5C%22%3Ca%20brief%20explanation%20of%20your%20reasoning%20for%20the%20forecast%3E%5C%5C%5C%22%5C%5Cn%7D%7D%5C%5Cn%5C%5CnThe%20probabilities%20(P_up%2C%20P_down%2C%20P_side)%20must%20sum%20to%201.0.%20The%20'trend'%20should%20be%20the%20one%20with%20the%20highest%20probability.%5C%5CnThe%20output%20must%20be%20only%20the%20JSON%20object%2C%20without%20any%20markdown%20formatting%20like%20%60%60%60json%20...%20%60%60%60.%5C%5Cn%5C%5C%5C%22%5C%5C%5C%22%5C%5C%5C%22%5C%22%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2C0%5D%2C%5B%5C%22en-GB%5C%22%5D%2C%5B%5C%22c_ebdcb1c6664b8d20%5C%22%2C%5C%22r_7a7835e417c461a1%5C%22%2C%5C%22rc_19d7c5c2f07720f9%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22AwAAAAAAAAAQ4DUFz3Xz2P5Pe0nKlhk%5C%22%5D%2C%5C%22!n5ylnMTNAAa-BNTXngRCBTLuScW2GxY7ADQBEArZ1EJGiEsT3wCYQjcg820OWHv_Ifghayv9Lv4ESfCfaeI7DpkgPYP8jXmKmq4PdQgFAgAAAIxSAAAABGgBB34AQRbr2krXt_Nj3zlP22jBxeZNN6gHu4pDwNFTdgxVmCGIPbsT5elH0ZaC4MFIN16PdRupvR_sJbuzFBMcEJpz7LtpmQOHTDyngmg8SVdqj3EOuOc3m5SumuJ1EwRzUsfPY6M_wXbEBAUr6mv7_8jMvr7OKG-o6tWiyrqLafz0jAk4MNkwCmDyVBwJPEATsFrJziNfj_zGsXu-65-3Tyj9V6EmclaffPQxkdhmR-rzvvni8wb_jgz2P70Y2TOeIati0E5IHGQV6aGl9IhTe_Ckv9A8H9lyKKTLpZ-IYY95Fj42sLLgOFPRgoDU1d6IPWCS_sJuYT1ntoCclQNVAVFDUOuk6oGS6zUycsUToLIUOeELP4RqdDA3R89bt-4RkPQDFZIXjc_7xRk6nJ-gMmbyL29WNVAQlQZq5oS-Wo-2pk7Rto_h5wvAjfYA4YhmHjB8hsBOO15D7B4To-53tvNLFQVQQHgo67KAGKHtcX8rLq3r09KyhZ_VTWm7HxZX7YrH5gWp80RGET09x-vWCWXdiItOLLkMGyJr9FJplCYdUn_LGmovdzmMS5hFr5wCqDyidlnSuKX8dcFQGToW3V0LcBR2vuzlVnaeWT5uyPS52JI7lgKwnG_bI5owaxOz2uvqhVjrVuKmNq7F5JwJRdEZ0WuSXvrlmFF2ZCIi1DSY3T154WpQ8lBnxrNiq9EOgNCc_Gfo2z6gLpUpAFLCBRbfs3_A3H4ZJ36Y6uSxy9RphMq0bYuoC0BZtRp6f-OZa_64iwKKctklQYaiyJ6oLWOUBbNrbuLu_6NqffbfmjkYDVUpnLLquMKHFkvg_B3KhbCQXnGv8rRLSuUixlTt5vAURvx7x0dKlOKUtrvf4RQoYbHlb4EEr9dh15dp0q-YlPte17qSd2MqcYP_kHushPfZwlSFXIfA3cgncmcLzVwiPHGMDlisue6TepFJSb7L1qVSFIO7qiecDZg8OlhKQKjp8vEGp3ildlXgoUEW9KQY8uF_3Nc_Zv6p7D15xnMuiTJDTe_VoO-Gu8F_Fld6tWaGGszIeUo-xxYVZreFbeEzY3UyNVFXd6d-UdCs5LYC9In6hbxXZ6P5Bf6SdyBnR7uZ4EHxgscVvWQkyEbe9v-tuHgrvKLAn_WSaoQJkR0eqx8NWAQ1S_0yQTiQBNeB7CE0G2Ec0wf39xpYWhKhfDnwvejDdFMFPIdv-S3i3afwyTf7d2rwXC_ZCYYffXxurDw92ywBLExj2F1XuI-fgLQeeiu8Y4M1kpoU3LWQP-dNI5FDsmcdhdun8KI5TdbL%5C%22%2C%5C%22db29d76a1ae56f2b70d97068365be1a3%5C%22%2Cnull%2C%5B0%5D%2C1%2Cnull%2Cnull%2C1%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B4%5D%5D%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1%2Cnull%2Cnull%2C%5B4%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B1%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C_null%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5D%5D%22%5D&at=AJoiUyNFfC7N-GU7pOQgeb_5EPLK%3A1758464022528&"
    #print(data_raw  )  # For debugging purposes
    data = dict(parse_qsl(data_raw))
    print(data)  # For debugging purposes
    print("----- Start of Data Dictionary -----")
    print_dict_recursive(data)
    print("----- End of Data Dictionary -----")
    try:
        # 4. Send the POST request
        response = requests.post(url, headers=headers, data=data)

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
    make_curl_request()
