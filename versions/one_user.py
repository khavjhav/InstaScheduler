import httpx, json, os, threading
from datetime import datetime

headers = {                         #
    "X-Csrftoken" : "IDMCYXOqQHFE4BG6AtzYSvZUzHVsxI8R",             #
    "X-Ig-App-Id" : '936619743392459',             #    You can get these from dev tools
    "cookie" : 'ig_did=15DA7B50-7809-41C4-B3C7-B6C443C950BA; datr=4fUSZRK9kcYMKATqEX572JXQ; ig_nrcb=1; csrftoken=IDMCYXOqQHFE4BG6AtzYSvZUzHVsxI8R; mid=ZRL14wAEAAEf1kVs1SsKbFa_CZ-e',                  #    once you login to an instagram account on browser  
    "X-Ig-Www-Claim" : "0"           #
}

def get_posts_chunk(userid):
    url = f"https://www.instagram.com/api/v1/feed/user/{userid}/?count=30"
    src = httpx.get(
        url,
        headers=headers,
        proxies={"all://": f"http://spgblhan86:MjNliW8a8m3u3xbVas@us.smartproxy.com:10000"},
    )
    data = src.json()
    return data
import random
start  = datetime.now() 
username = "ayehxncho"
src = httpx.get(
    "https://www.instagram.com/api/v1/users/web_profile_info/?username=" + username,
    headers=headers,
    proxies={"all://": f"http://spgblhan86:MjNliW8a8m3u3xbVas@us.smartproxy.com:10000"}
)

def download_image(url, path):
    try:
        response = httpx.get(url)
        with open(path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(e)

data = src.json()
if data['status'] == "ok":
    #os.mkdir("instagram")
    data = data['data']['user']
    open("instagram/user.json", "w+").write(json.dumps(data, indent=4))
    posts = get_posts_chunk(data['id'])
    data['posts'] = posts['items']
    open("instagram/user.json", "w+").write(json.dumps(data, indent=4))
    threads = []
    #resolutions = {
    #    "< 50000": [],
    #    "50001-200000": [],
    #    "200001+": [],

    #}
    # for post in posts['items']:
    #     #open("data.json","w+").write(json.dumps(posts['items'], indent=4))
    #     #exit()
    #     for link in post["image_versions2"]["candidates"]:
    #         px = link['width'] * link['height']
    #         link['code'] = post['code']
    #         if px <= 50000:
    #             resolutions['< 50000'].append(link)
    #         elif px > 50000 and px <= 200000:
    #             resolutions['50001-200000'].append(link)
    #         elif px >= 200001:
    #             resolutions["200001+"].append(link)
    #             "200001+"
            #resolutions[f"{link['width']}x{link['height']}"].append(link)
            
        # dir = os.mkdir(f"instagram/pictures/{post['code']}")
        # for link in post["image_versions2"]["candidates"]:
        #     t = threading.Thread(
        #         target=download_image,
        #         args=[
        #             link["url"],
        #             f"{dir}/{random.randint(12983, 3482734892)}.png"
        #         ]
        #     )
    """  keys = dict.keys(resolutions)
    dupes = {}
    for key in keys:
        dupes[key] = {}
        for post in resolutions[key]:
            px = post['width'] * post['height']
            if not post['code'] in dupes[key]:
                dupes[key][post['code']] = []
            
            dupes[key][post['code']].append(post)
    
    nodupes = {}
    for key in keys:
        posts = dict.keys(dupes[key]) 
        nodupes[key] = []
        for post in posts:
            postlist = dupes[key][post]
            highest = None
            for post in postlist:
                if highest == None: highest = post
                else:
                    if (post['width'] * post['height']) > (highest['width'] * highest['height']):
                        highest = post
            
            nodupes[key].append(highest) """
    #open("dupes.json", "w+").write(json.dumps(dupes, indent=4))
    #open("nodupes.json", "w+").write(json.dumps(nodupes, indent=4))
    #open("resolutions.json", "w+").write(json.dumps(resolutions, indent=4))
    #while threads != []:
     #   for thread in threads:
      #      if not thread.is_alive(): del threads[threads.index(thread)]
    # threads = []
    # for post in nodupes['200001+']:
    #     #print(post['url'])
    #     #for link in post["image_versions2"]["candidates"]:
    #     t = threading.Thread(
    #         target=download_image,
    #         args=[
    #             post["url"],
    #             f"instagram/pictures/{random.randint(3984394, 43593458)}.png"
    #         ]
    #     )
    #     threads.append(t)
    #     t.start()
    
    # while threads != []:
    #    for thread in threads:
    #        if not thread.is_alive(): del threads[threads.index(thread)]
    
    finish = datetime.now()

    date = finish - start
    print(f"Took {date.total_seconds()} seconds to scrape user data n 5 posts")
else:
    open("test.json", "w+").write(json.dumps(data, indent=4))