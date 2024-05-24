# AP rename
modify ap name via serial with excel upload

1. create a venv following the official python docs for your environment and activate it
2. run command: pip install -r requirements.txt
3. modify your "sample_secrets.yaml" file to include your client id, client secret, token and refresh token from the aruba central instance, and rename the file secrets.yaml
4. rename the secrets file "secrets.yaml"
5. modify your apis.yaml file updating the base api gateway url. 
6. export serials from aruba central for all aps and put them in the aps_serials.xlsx file. 
7. run the script with /path/to/venv/interpreter/python.exe /path/to/script/directory/python.exe

