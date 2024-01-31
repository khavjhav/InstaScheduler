import json

data = json.loads(open("instagram/user.json","r").read())

edges = data['edge_owner_to_timeline_media']['edges']
print(len(edges))