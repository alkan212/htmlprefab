import json

with open('site_info.json') as json_file:
    data = json.load(json_file)
    print(data)