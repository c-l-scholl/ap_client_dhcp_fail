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
    df = pd.read_excel("615_serials.xlsx")
    ap_cli = {}
    get_per_ap_method = apis["get_per_ap"]["method"]
    get_per_ap_uri = apis["get_per_ap"]["uri"]
    post_per_ap_method = apis["post_per_ap"]["method"]
    post_per_ap_uri = apis["post_per_ap"]["uri"]
    #get ap cli 
    for ap in df["serial number"].to_list():
        r = make_request(get_per_ap_method, base_rest_gateway, get_per_ap_uri + ap, token = secrets["access_token"])
        ap_cli[ap] = r
    #uncomment to see print of full ap by ap config    
    #pprint(ap_cli)
    #change parameter based on key word - changing the keyword changes the matched line. If it matches multiple times, multiple lines will be replaced. 
    for ap in ap_cli.keys():
        for index, content in enumerate(ap_cli[ap]):
            if "flex-dual-band" in content:
                ap_cli[ap][index] = "  flex-dual-band 5GHz-and-2.4GHz"
            ap_cli[ap].append("  flex-dual-band 5GHz-and-2.4GHz")
    #push to aps in list by AP      
    for ap in ap_cli.keys():
        post_per_ap_parameters = {"clis" : ap_cli[ap]}
        print(post_per_ap_parameters)
        r = make_request(post_per_ap_method, base_rest_gateway, post_per_ap_uri + ap, post_per_ap_parameters, token = secrets["access_token"]) 
        print(f"success pushing to {r}")
if __name__ == "__main__":
    main()