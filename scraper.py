from module.instagram import InstagramScraper
from json import loads, dump
from os import listdir, path, mkdir
from time import sleep, time
from requests import get
from threading import Thread
from datetime import timedelta
from bson import ObjectId
if __name__ == "__main__":
    config = loads(open("config.json","r").read())
    scraper = InstagramScraper(
        username=None,
        password=None,
        headless=False,
        proxy=config['proxy'],
        database = config['db'],
        use_db_logins=True
    )

    scraper.driver.get("https://instagram.com/sipherw")
    sleep(6)
    scraper.accept_cookies()
    sleep(3)
    scraper.csrftoken = scraper.get_crsf()
    if scraper.csrftoken == None:
        scraper.ui()
        scraper.pprint(f"Unable to get csrftoken of browser session.")
        exit()
    else:
        scraper.ui()
        scraper.pprint(f"I have retrieved the csrftoken: {scraper.csrftoken}.")
        sleep(1)
    scraper.wwwclaim = scraper.get_wwwclaim()
    if not config['mode'] in "1 2 3 4".split():
        scraper.ui(True)
        config['mode'] = input(scraper.format)
    if config['mode'] == "1":
        scraper.ui()
        scraper.pprint('Enter username of user to scrape')
        user = input(scraper.format)
        scraper.user = user
        scraper.ui()
        scraper.startScraper()
    elif config['mode'] == "2":
        scraper.ui() 
        start = time()
        scraper.pprint('Getting users from database...') 
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "pk",
                    "foreignField": "id",
                    "as": "matched_docs"
                }
            },
            {
                "$match": {
                    "matched_docs": []
                }
            },
            {
                "$project": {
                    "matched_docs": 0
                }
            }
        ]
        sleep(4)
        target_object_id = ObjectId(config["checkpoint"])
        print("Target ObjectId:", target_object_id)
        query = {'_id': {'$gt': target_object_id}, 'is_private': False}
        print("Query:", query)

        scraper.users =  scraper.db.instagram.chunks.find(query).limit(10000)
        print(scraper.users)
        scraper.users = list(scraper.users)
        #print(scraper.users)
        print(len(scraper.users))
        print(scraper.users[0])
        end = time()
        scraper.pprint(f"Recieved {len(scraper.users)} users. Took {str(timedelta(seconds=int(round(end-start))))}")
        scraper.errorcount = 0
        for user in scraper.users:
            dupe = scraper.db.instagram.users.find_one({"id": user['pk']}, {'_id': 0})
            if dupe == None: 
                
                Thread(target=scraper.upload_data, args=(user,)).start()
                id_string = str(user['_id'])
                #desired_part = id_string[10:len(id_string)-2]
                config['checkpoint'] = id_string

                # Write the updated data back to the JSON file
                with open("config.json", "w") as json_file:
                    dump(config, json_file, indent=2)
                sleep(0.2)
                #scraper.upload_data(user)
            else:
                scraper.pprint(f"User @{user['username']} | {user['pk']} already exists in database.")
            
    elif config['mode'] == "3":
        scraper.ui()
        username = config['user']['3']
        scrapeduser = scraper.get_follower_data(username)      
        scraper.ui()
        if scrapeduser != None:
            scraper.pprint(f"Recieved valid user {scrapeduser['username']} | {scrapeduser['id']}")
            scraper.pprint(f"Recieved {len(scrapeduser['edge_related_profiles']['edges'])} related profiles.")
            scraper.pprint("Authenticating browser...")
            scraper.authenticate()
            if not scraper.authenticated:
                scraper.pprint("Failed to authenticate.")
            scraper.csrftoken = scraper.get_crsf()
            scraper.ui()
            for user in scrapeduser['edge_related_profiles']['edges']:
                if user['node']['is_verified'] == False and user['node']['is_private'] == False:
                    if not user['node']['username'] in config['skip_users']:
                        scraper.user = user['node']['username']
                        nextmax = None
                        scraper.driver.get(f"https://instagram.com/{user['node']['username']}")
                        sleep(3)
                        scraper.csrftoken = scraper.get_crsf()
                        data = scraper.startScraper()
    elif config['mode'] == "4":
        scraper.ui() 
        start = time()
        scraper.pprint('Getting users from database...') 
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "pk",
                    "foreignField": "id",
                    "as": "matched_docs"
                }
            },
            {
                "$match": {
                    "matched_docs": []
                }
            },
            {
                "$project": {
                    "matched_docs": 0
                }
            }
        ]
        sleep(4)
        target_object_id = ObjectId("653988b08d1db588fb6e3e7a")
        print("Target ObjectId:", target_object_id)
        query = {'_id': {'$gt': target_object_id}}
        print("Query:", query)

        scraper.users =  scraper.db.instagram.users.find(query).limit(100)
        #print(scraper.users)
        scraper.users = list(scraper.users)
        #print(scraper.users)
        print(len(scraper.users))
        #print(scraper.users[0])
        end = time()
        scraper.pprint(f"Recieved {len(scraper.users)} users. Took {str(timedelta(seconds=int(round(end-start))))}")
        scraper.errorcount = 0
        count = 0
        import copy
        users_copy = copy.deepcopy(scraper.users)
        for user in users_copy:
            query = {"pk": user['pk']}
            dupe = scraper.db.instagram.chunks.find_one(query)

            # Thread(target=scraper.upload_data_for_user_recheck, args=(dupe,)).start()
            scraper.upload_data_for_user_recheck(dupe,)
            # sleep(1)
            
            # Check if newuser is None before accessing its properties
            newuser = scraper.db.instagram.latest_posts.find_one(query)
            # tempcount = 0
            # if newuser is None:
            #     while newuser is None:
            #         newuser = scraper.db.instagram.latest_posts.find_one(query)
            #         if tempcount > 9:
            #             break
            #         tempcount += 1
            #         sleep(1)

            
            if newuser is not None:
                #print(newuser)
                #print(len(newuser["posts"]))
                #print(len(user["posts"]))
                scraper.pprint(f"Scrapped User :{user['pk']}")
                
                if len(newuser["posts"]) != len(user["posts"]):
                    poststemp = []
                    for elm in newuser["posts"]:
                        if len(user["posts"])!=0:
                            if user["posts"][0]["taken_at"] < elm["taken_at"]:
                                #poststemp.append(elm)
                                scraper.db.instagram.new_posts.insert_one(elm)
                                scraper.pprint(f"New post found for user {user['pk']}")
                        else:
                            scraper.db.instagram.new_posts.insert_one(elm)
                            scraper.pprint(f"New post found for user {user['pk']}")

                    #print(count)
                        
                    #print()
                
            else:
                # Handle the case where newuser is None (document not found)
                scraper.pprint(f"No data found for user {user['pk']} in latest_posts collection")

            count += 1
               