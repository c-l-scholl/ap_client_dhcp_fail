import pandas as pd
import requests
from pprint import pprint
import yaml

def make_request(verb, base_url, uri, parameters: dict = {}, token = ""):
    """make request, return response"""
    try: 
        request_headers = {}
        if token != "":
            request_headers = {
                "accept": "application/json",
                "authorization": f"Bearer {token}"
            }
        r = requests.request(method = verb, url = base_url + uri, json = parameters, headers=request_headers)
        r.raise_for_status()
        response = r.json()
        return response
    except requests.exceptions.RequestException as e:
        pprint(f"""Something happened with the request. 
Status Code: {r.status_code} 
Exception: {e.__class__.__name__} {e}""")
        pprint(r.json())
    except Exception as e:
        print(f"Something went wrong: {e.__class__.__name__} {e}")

def load_yaml(filename):
    with open(file = filename, mode = "r") as f:
        loaded = yaml.safe_load(f)
    return loaded

def refresh_token(api_gateway_file: str = "apis.yaml", secrets_file: str = "secrets.yaml") -> dict:
    """refresh token and update secrets file"""
    #import gateway url and uri's from yaml
    api_gateway_uri = load_yaml(api_gateway_file)
    rest_gateway = api_gateway_uri["rest_gateway"]["url"]
    refresh_method = api_gateway_uri["refresh"]["method"]
    refresh_uri = api_gateway_uri["refresh"]["uri"]
    #import secrets from yaml
    secrets = load_yaml(secrets_file)
    refresh_params= {"client_id" : secrets["client_id"],
                       "client_secret" : secrets["client_secret"],
                       "grant_type" : "refresh_token",
                       "refresh_token" : secrets["refresh_token"]}
    #request refresh
    refresh_token = make_request(refresh_method, rest_gateway, refresh_uri, refresh_params)
#update secrets
    secrets["access_token"] = refresh_token["access_token"]
    secrets["refresh_token"] = refresh_token["refresh_token"]
    with open(file = secrets_file, mode = "w") as yf:
        yaml.dump(secrets, yf, default_flow_style=False)
        print("secret update successful")

def main():
    #refresh token and update secrets file
    refresh_token()
    #load fresh secrets and apis for work
    secrets = load_yaml("secrets.yaml")
    apis = load_yaml("apis.yaml")
    base_rest_gateway = apis["rest_gateway"]["url"]
    data = pd.read_excel("aps_serials.xlsx").to_dict()
    ap_cli = {}
    get_per_ap_method = apis["get_per_ap"]["method"]
    get_per_ap_uri = apis["get_per_ap"]["uri"]
    post_per_ap_method = apis["post_per_ap"]["method"]
    post_per_ap_uri = apis["post_per_ap"]["uri"]
    #get ap cli 
    for index,serial in data["serial number"].items():
        r = make_request(get_per_ap_method, base_rest_gateway, get_per_ap_uri + serial, token = secrets["access_token"])
        ap_cli[index] = r
    # uncomment to see print of full ap by ap config    
    pprint(ap_cli) 
    for ap_index in ap_cli.keys():
        for index, content in enumerate(ap_cli[ap_index]):
            if "hostname" in content:
                ap_cli[ap_index][index] = f"  hostname {data["hostname"][ap_index]}"          
    #push to aps in list by AP      
    for ap_index in ap_cli.keys():
        post_per_ap_parameters = {"clis" : ap_cli[ap_index]}
        r = make_request(post_per_ap_method, base_rest_gateway, post_per_ap_uri + data["serial number"][ap_index], post_per_ap_parameters, token = secrets["access_token"]) 
        print(f"success pushing to {r}")
if __name__ == "__main__":
    main()