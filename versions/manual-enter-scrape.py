import requests, random, threading, os, json, time
from colorama import Fore
textformat = f"""{Fore.GREEN}{os.getcwd()}{Fore.RESET} via {Fore.YELLOW}🐍 [Sipher's World] v0.0.1{Fore.RESET}\n{Fore.GREEN} + >{Fore.RESET} """
proxy = 'spgblhan86:MjNliW8a8m3u3xbVas@gate.smartproxy.com:7000'
plus = f" {Fore.GREEN}+{Fore.RESET} "

class InstagramScraper:
    def __init__(self, proxy):
        os.system("cls")
        self.plus = plus
        self.format = textformat
        self.ui()
        self.crsftoken = input(f"\n[{self.plus}] Enter CRSF Token\n{self.format}")
        self.ui()
        self.cookie = input(f"\n[{self.plus}] Enter Cookie\n{self.format}")
        self.ui()
        self.igappid = '936619743392459'
        self.wwwclaim = input(f"\n[{self.plus}] Enter X-Ig-Www-Claim\n{self.format}")
        self.ui()
        self.proxy = proxy
        self.next_max_id = None
        self.users = []
        #self.age_model = cv2.dnn.readNetFromCaffe("models/deploy_age.prototxt", "models/age_net.caffemodel") 
        #self.gender_model = cv2.dnn.readNetFromCaffe("models/deploy_gender.prototxt", "models/gender_net.caffemodel") 
        #self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "models/haarcascade_frontalface_default.xml") 
    
    def ui(self, options=False):
        os.system("cls")
        print(f"""
{Fore.GREEN}

       .__       .__                                              .__       .___
  _____|__|_____ |  |__   ___________  ______ __  _  _____________|  |    __| _/
 /  ___/  \____ \|  |  \_/ __ \_  __ \/  ___/ \ \/ \/ /  _ \_  __ \  |   / __ | 
 \___ \|  |  |_> >   Y  \  ___/|  | \/\___ \   \     (  <_> )  | \/  |__/ /_/ | 
/____  >__|   __/|___|  /\___  >__|  /____  >   \/\_/ \____/|__|  |____/\____ | 
     \/   |__|        \/     \/           \/                                 \/ 

{Fore.RESET}
""")
        if options:
            print(f"""
[ {Fore.GREEN}1{Fore.RESET} ] Scrape follower chunks.
[ {Fore.GREEN}2{Fore.RESET} ] Carry on scraping from a file.
              """)
        
    def returnHeaders(self):
        return {
            "X-Csrftoken" : self.crsftoken,
            "X-Ig-App-Id" : self.igappid,
            "cookie" : self.cookie,
            "X-Ig-Www-Claim" : self.wwwclaim

        }

    def returnProxy(self):
        return {
            "all://" : f"http://{self.proxy}"
        }

    def get_follower_data(self, username):
        src = requests.get(
            "https://www.instagram.com/api/v1/users/web_profile_info/?username=" + username,
            headers=self.returnHeaders(),
            proxies=self.returnProxy()
        )

        
        data = src.json()
        if data['status'] == "ok":
            open("test.json", "w+").write(json.dumps(data['data']['user'], indent=4))
            return data['data']['user']
        else:
            return None
    
    def scrape_followers(self, scrapedUser):
        id = scrapedUser['id']
        next_max_id = None
        users = []
        while True:
            try:
                url = f"https://www.instagram.com/api/v1/friendships/{id}/followers/?count=100"
                if next_max_id != None: url += f"&max_id={next_max_id}"
                src = requests.get(
                    url,
                    headers=self.returnHeaders(),
                    proxies=self.returnProxy()
                )
                data = src.json()
                for user in data['users']:  
                    users.append(user)
                
                print(f"[{self.plus}] @{scrapedUser['username']} | +{len(data['users'])} | total scraped: {len(users)} | total followers: {scrapedUser['edge_followed_by']['count']}")
                
                if not "next_max_id" in data:        
                    next_max_id = None   
                    break
                else: 
                    next_max_id = data['next_max_id']
                    time.sleep(0.5)
            except Exception as e:
                print(f"[{self.plus}] Error: {e}")
                time.sleep(4)
                break
        

        return users
        

    def find_duplicate_user(self, user):
        retries = 0
        while retries <= 5:
            try:
                src = requests.post(
                    "http://localhost:3000/api/instagram/find_user",
                    json={
                        "username" : user['username'],
                        "id" : user['pk']
                    },
                    proxies=self.returnProxy()
                )
                src = src.json()
                if src["error"] == None: return True
                else: return False
            except:
                retries += 1
                time.sleep(2)

        return False
    
    def get_posts_chunk(self, userid, next_max_id):
        url = f"https://www.instagram.com/api/v1/feed/user/{userid}/?count=12"
        if next_max_id != None: url += f"&max_id={self.next_max_id}"
        src = requests.get(
            url,
           # headers=self.returnHeaders(),
            proxies=self.returnProxy()
        )
        data = src.json()
        return data
    
    def startpostScrape(self, user):
        next_max_id = None
        posts = []
        more = True
        try:
            while more == True:
                chunk = self.get_posts_chunk(user['id'], next_max_id)
                for user in chunk['items']: posts.append(user)
                
                #print(f"[{self.plus}] Scraped {len(posts)} post (+{len(chunk['items'])})", end="\r")
                #sys.stdout.flush()
                if not "next_max_id" in chunk:
                    more = False         
                    next_max_id = None   
                else: 
                    next_max_id = chunk['next_max_id']
                    time.sleep(1)
        except:
            pass
            
        return posts
    
    def download_image(self, url, path): 
        response = requests.get(url) 
        with open(path, 'wb') as f: 
            f.write(response.content) 

    def upload_user(self, user):
        retries = 0
        while retries <= 5:
            try:
                requests.post(
                    "http://localhost:3000/api/instagram/upload_user",
                    json=user,
                    proxies=self.returnProxy()
                )
                break
            except:
                retries += 1
                time.sleep(2)
    

    def upload_data(self, user, scrapedUser):
        #print('\033[1A', end='\x1b[2K')
        try:
            alldata = self.get_follower_data(user['username'])
            alldata['posts'] =[]
            if alldata['is_private'] == False: alldata['posts'] = self.startpostScrape(alldata)
            self.upload_user(alldata)
            if not os.path.exists(f"users/{scrapedUser['username']}/followers/{alldata['username']}"):
                os.mkdir(f"users/{scrapedUser['username']}/followers/{alldata['username']}")

            self.download_image(alldata['profile_pic_url_hd'], f"users/{scrapedUser['username']}/followers/{alldata['username']}/pfp.jpg") 
            open(f"users/{scrapedUser['username']}/followers/{alldata['username']}/user.json", "w+").write(json.dumps(alldata, indent=4))
            if not os.path.exists(f"users/{scrapedUser['username']}/followers/{alldata['username']}/pictures"):
                os.mkdir(f"users/{scrapedUser['username']}/followers/{alldata['username']}/pictures")
            
            for post in alldata["posts"][:20]:
                self.download_image(post['image_versions2']['candidates'][0]['url'], f"users/{scrapedUser['username']}/followers/{alldata['username']}/pictures/{post['code']}.png") 

            print(f"[{self.plus}] Scraped full data for @{user['username']} | {self.users.index(user) + 1}/{len(self.users)}")
            
        except Exception as e:
            print(f"[{self.plus}] Error: {e} | {self.users.index(user) + 1}/{len(self.users)}")
    
    def startScraper(self):
        self.ui()
        scrapedUser = self.get_follower_data(self.user)
        username = scrapedUser['username']
        if not os.path.exists(f"users/{username}"): os.mkdir(f"users/{username}")
        self.download_image(scrapedUser['profile_pic_url_hd'], f"users/{username}/pfp.jpg") 
        if not os.path.exists(f"users/{username}/followers"): os.mkdir(f"users/{username}/followers")
        open(f"users/{username}/user.json","w+").write(json.dumps(scrapedUser, indent=4))
        self.users = self.scrape_followers(scrapedUser)
        open(f"users/{username}/followers.json","w+").write(json.dumps(self.users, indent=4))
        print(f"[{self.plus}]  Scraped {len(self.users)} users in total")
        self.ui()
        print(f"[{self.plus}] Scraping user by user...")
        for user in self.users:
            dupe = self.find_duplicate_user(user)
            if dupe == False:
                t = threading.Thread(target=self.upload_data, args=[user, scrapedUser])
                t.start()
                time.sleep(1)
            else:
                print(f"[{self.plus}] Duplicate @{user['username']} | {self.users.index(user) + 1}/{len(self.users)}")

def find_val(array, key, value):
    for k in array:
        if k[key] == value:
            return True
    return False
if __name__ == "__main__":
    instagram = InstagramScraper(proxy)
    instagram.ui(True)
    choice = input(instagram.format)
    if choice == "1":
        user = input(f"[{plus}] Enter username of user to scrape\n{textformat}")
        instagram.user = user
        instagram.ui()
        instagram.startScraper()
    elif choice == "2":
        instagram.ui()
        lists = os.listdir("users")
        for user in lists: print(f"{lists.index(user) + 1}. {user}")
        print("\n")
        filepath = input(f"Enter the username.\n{instagram.format}")
        if not filepath in lists:
            print("Invalid user")
            exit()

        instagram.ui()
        userdata = json.loads(open(f"users/{filepath}/user.json", "r").read())
        scrapedusers = os.listdir(f"users/{filepath}/followers")
        print(f"""
User: {userdata['username']} | {userdata['id']}
Followers: {userdata['edge_followed_by']['count']}
Followers Scraped: {len(scrapedusers)}
""")
        instagram.users = json.loads(open(f"users/{filepath}/followers.json", "r").read())
        open("test.txt","w+").write("\n".join(scrapedusers))
        dupusers = requests.get("http://localhost:3000/api/instagram/get_all_users").json()
        dupusers = dupusers['data']['users']
        for user in instagram.users:
            dupe = find_val(dupusers, "username", user['username'])
            if not dupe:
                #instagram.upload_data(user, userdata)
                t = threading.Thread(target=instagram.upload_data, args=[user, userdata])
                t.start()

                time.sleep(0.5)