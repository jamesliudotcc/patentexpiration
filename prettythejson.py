import json
import flatten_json

with open('fromAPIrequest.json') as f:
    ugly_json = f.read()

pretty_json = json.dumps(json.loads(ugly_json), indent=2, sort_keys=True)
print(pretty_json)

with open('fromAPIrequestpretty.json', 'w') as g:
    g.write(pretty_json)

flat_json = json.dumps(flatten_json.flatten(json.loads(ugly_json)))

