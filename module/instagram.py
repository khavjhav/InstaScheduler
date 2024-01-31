import os, json, time, random
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from module.addproxy import get_proxy_extension
import httpx as requests
from pymongo import MongoClient
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
class InstagramScraper:
    def __init__(
        self,
        username,
        password,
        headless,
        proxy,
        database,
        use_db_logins
    ):

        self.use_db_logins = use_db_logins
        self.igappid = "936619743392459"
        self.csrftoken = None
        self.wwwclaim = None
        self.ua = UserAgent()
        self.user_agent = user_agent_rotator.get_random_user_agent()
        self.cookie = None
        self.authenticated = False
        self.username = username
        self.password = password
        self.format = f"""{Fore.GREEN}{os.getcwd()}{Fore.RESET} via {Fore.YELLOW}🐍 [Sipher's World] v0.0.1{Fore.RESET}\n{Fore.GREEN} + >{Fore.RESET} """
        self.proxy = proxy
        self.db = MongoClient(database)

        self.ui()
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints")
        chrome_options.add_argument(f'user-agent={self.user_agent}')

        if proxy:
            filepath = get_proxy_extension('us.smartproxy.com', '10000', 'spnz42b9uo', 'jwb1Sz3fU8xNYfx7re')
            chrome_options.add_extension(filepath)

        self.driver = webdriver.Chrome(
            options=chrome_options
        ) 
        self.driver.set_window_size(1500,1000)

    def get_wwwclaim(self):
        if self.authenticated == False: return '0'
        sstorage = self.driver.execute_script("return sessionStorage;")
        if "www-claim-v2" in sstorage:
            self.wwwclaim = sstorage["www-claim-v2"]
            self.pprint(f"I have retrieved the www-claim-v2: {self.wwwclaim}.")
        else:
            self.ui()
            self.pprint(f"Unable to get www-claim-v2 of browser session.")
            exit()
    def get_crsf(self):
        cookies = self.driver.get_cookies()
        cookies.reverse()
        self.cookie = "; ".join([str(y['name'])+"="+str(y['value']) for y in cookies])
        for data in cookies:
            if data["name"] == "csrftoken":
                return data["value"]
        
        return None
    def returnHeaders(self):

        return {
            "X-Csrftoken": self.csrftoken,
            "X-Ig-App-Id": self.igappid,
            "cookie": self.cookie,
            "X-Ig-Www-Claim": self.wwwclaim,
            #"User-Agent" : self.user_agent
        }

    def pprint(self, text):
        print(f"[ {Fore.GREEN}+{Fore.RESET} ] {text}")
    
    def click_onetap(self):
        try:
            onetap = self.driver.find_element(
                By.XPATH, "//div[text()='Not now']"
            )
            if onetap: 
                onetap.click()
        
        except:
            self.pprint(f"Failed to accept onetap.")
            time.sleep(2)

    def authenticate(self):
        if not self.use_db_logins:
            self.driver.get("https://instagram.com")
            time.sleep(7)
            username_input = self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')
            password_input = self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')
            self.pprint(f"using {self.username}:{self.password}")
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(10)
            self.driver.get("https://instagram.com")
            time.sleep(7)
            if "challenge" in self.driver.current_url:
                self.authenticated = False
                self.db.instagram.logins.update_one({"username" : self.username}, {"$set":{"challenge" : True}})
                time.sleep(456456)
            elif "suspended" in self.driver.current_url:
                self.authenticated = False
                self.db.instagram.logins.update_one({"username" : self.username}, {"$set":{"suspended" : True}})
                self.pprint("Suspended... logging out...")
                exit()
            elif "onetap" in self.driver.current_url:
                self.authenticated = True
            else:
                pass
        else:
            while self.authenticated == False:
                self.driver.get("https://instagram.com")
                time.sleep(7)
                userlist = self.db.instagram.logins.find({"suspended" : False, "challenge" : False})
                if userlist == None:
                    self.pprint(f"usernames are all invalid...")
                    exit()
                
                userlist = list(userlist)
                user = random.choice(userlist)
                self.pprint(f"using {user['username']}:{user['password']}")
                self.username = user['username']
                self.password = user['password']
                username_input = self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')
                password_input = self.driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')

                username_input.send_keys(self.username)
                password_input.send_keys(self.password)
                password_input.send_keys(Keys.RETURN)
                time.sleep(10)
                self.driver.get("https://instagram.com")
                time.sleep(7)
                if "challenge" in self.driver.current_url:
                    self.authenticated = False
                    self.db.instagram.logins.update_one({"username" : self.username}, {"$set":{"challenge" : True}})
                    time.sleep(456456)
                elif "suspended" in self.driver.current_url:
                    self.authenticated = False
                    self.db.instagram.logins.update_one({"username" : self.username}, {"$set":{"suspended" : True}})
                    self.pprint("Suspended... logging out...")
                    clicker = self.driver.find_element(
                        By.XPATH, "//div[contains(@data-bloks-name, 'ig.components.Icon')]"
                    )
                    clicker.click()
                    time.sleep(1)
                    onetap = self.driver.find_element(
                        By.XPATH, f"//span[contains(text(), 'Log out')]"
                    )
                    if onetap:
                        onetap.click()
                    time.sleep(1)
                    try:
                        onetap = self.driver.find_element(
                            By.XPATH, f"//div[contains(text(), 'Log out')]"
                        )
                        if onetap:
                            onetap.click()
                    except:
                        pass
                        
                    while "suspended" in self.driver.current_url: pass
                #time.sleep(7)
                elif "onetap" in self.driver.current_url:
                    self.authenticated = True
                    self.csrftoken = self.get_crsf()
                    self.wwwclaim = self.get_wwwclaim()
                else:
                    pass
            
    def accept_cookies(self):
        time.sleep(2)
        try:
            cookies = self.driver.find_element(
                By.XPATH, "//button[text()='Allow all cookies']"
            )
            if cookies:
                cookies.click()
                time.sleep(3)
        except:
            self.pprint(f"Failed to accept cookies.")

    def ui(self, options=False):
        os.system("cls")
        print(
            f"""
{Fore.GREEN}

       .__       .__                                              .__       .___
  _____|__|_____ |  |__   ___________  ______ __  _  _____________|  |    __| _/
 /  ___/  \____ \|  |  \_/ __ \_  __ \/  ___/ \ \/ \/ /  _ \_  __ \  |   / __ | 
 \___ \|  |  |_> >   Y  \  ___/|  | \/\___ \   \     (  <_> )  | \/  |__/ /_/ | 
/____  >__|   __/|___|  /\___  >__|  /____  >   \/\_/ \____/|__|  |____/\____ | 
     \/   |__|        \/     \/           \/                                 \/ 

  -  Proxy: {self.proxy}
  -  DB: {self.db}
  -  Crsftoken: {self.csrftoken}
  -  Www-Claim: {self.wwwclaim}
  -  User-Agent: {self.user_agent}
  -  Cookie: {self.cookie}
{Fore.RESET}
"""
        )
        if options:
            print(
                f"""
[ {Fore.GREEN}1{Fore.RESET} ] Scrape follower chunks.
[ {Fore.GREEN}2{Fore.RESET} ] Carry on scraping from a file.
[ {Fore.GREEN}3{Fore.RESET} ] Scrape user related files.

              """
            )

    def returnProxy(self):
        return {"all://": f"http://{self.proxy}"}

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
    
    def logout(self):
        clicker = self.driver.find_element(
            By.XPATH, "//span[text()='More']"
        )
        clicker.click()
        time.sleep(2)
        clicker = self.driver.find_element(
            By.XPATH, "//span[text()='Log out']"
        )
        clicker.click()
        self.pprint(f"Logged out of {self.username}")
        self.authenticated = False
        time.sleep(10)
        
    def scrape_followers(self, scrapedUser, currentmax):
        id = scrapedUser["id"]
        next_max_id = currentmax
        if next_max_id != None:
            self.pprint(f"@{scrapedUser['username']} | Starting from {self.before} | {len(self.chunkusers)}/{scrapedUser['edge_followed_by']['count']}")

        for x in range(self.before): self.chunkusers.append([])
        while True:
            try:
                url = f"https://www.instagram.com/api/v1/friendships/{id}/followers/?count=100"
                if next_max_id != None:
                    url += f"&max_id={next_max_id}"
                src = requests.get(
                    url, headers=self.returnHeaders(), proxies=self.returnProxy()
                )
                data = src.json()
                if not "users" in data: print(data)
                open("test.json","w+").write(json.dumps(data, indent=4))
                if src.status_code == 429 or not "users" in data or data['status'] == "fail":
                    self.pprint(f"Error: {data}")
                    time.sleep(1)
                    self.logout()
                    self.authenticate()
                    self.driver.get(f"https://instagram.com/{scrapedUser['username']}")
                    time.sleep(3)
                    self.csrftoken = self.get_crsf()
                    continue
                else:
                    for user in data["users"]:
                        user['chunked_from'] = {
                            "username" : scrapedUser['username'],
                            "id": id
                        }
                        self.chunkusers.append(user)

                    if len(self.chunkusers) >= scrapedUser['edge_followed_by']['count']:
                        break
                    else:
                        next_max_id = data["next_max_id"]
                        self.db.instagram.maxids.update_one({"username" : scrapedUser['username']}, {"$set":{"maxid" : next_max_id, "amount" : len(self.chunkusers)}})
                        time.sleep(0.5)
                    
                    self.db.instagram.chunks.insert_many(data['users'])
                    self.pprint(f"@{scrapedUser['username']} | +{len(data['users'])} | {len(self.chunkusers)}/{scrapedUser['edge_followed_by']['count']}")
            
            
            except Exception as e:
                self.pprint(f"Error: {e}")

        return next_max_id

    def find_duplicate_user(self, user):
        retries = 0
        while retries <= 5:
            try:
                src = requests.post(
                    "http://localhost:3000/api/instagram/find_user",
                    json={"username": user["username"], "id": user["pk"]},
                    proxies=self.returnProxy(),
                )
                src = src.json()
                if src["error"] == None:
                    return True
                else:
                    return False
            except:
                retries += 1
                time.sleep(2)

        return False

    def get_posts_chunk(self, userid, next_max_id, amount=33):
        url = f"https://www.instagram.com/api/v1/feed/user/{userid}/?count={amount}"
        if next_max_id != None:
            url += f"&max_id={self.next_max_id}"
        src = requests.get(
            url,
            headers=self.returnHeaders(),
            proxies=self.returnProxy(),
        )
        data = src.json()
        return data

    def startpostScrape(self, user):
        next_max_id = None
        posts = []
        more = True
        try:
            while more == True:
                chunk = self.get_posts_chunk(user["id"], next_max_id, 40)
                for user in chunk["items"]:
                    posts.append(user)

                # self.pprint(f"Scraped {len(posts)} post (+{len(chunk['items'])})", end="\r")
                # sys.stdout.flush()
                if not "next_max_id" in chunk:
                    more = False
                    next_max_id = None
                else:
                    next_max_id = chunk["next_max_id"]
                    time.sleep(1)
        except:
            pass

        return posts

    def download_image(self, url, path):
        response = requests.get(url)
        with open(path, "wb") as f:
            f.write(response.content)

    def upload_user(self, user):
        self.db.instagram.users.insert_one(user)

    def upload_rechecked_user(self,user):
        self.db.instagram.latest_posts.insert_one(user)

    def upload_data_for_user_recheck(self, user):
        try:
            alldata = self.get_follower_data(user["username"])
            alldata["posts"] = []

            if alldata["is_private"] == False:
                alldata["posts"] = self.startpostScrape(alldata)

            alldata['pk'] = alldata['id']
            self.upload_rechecked_user(alldata)

            self.pprint(f"Scraped full data for @{user['username']} | {self.users.index(user) + 1}/{len(self.users)}")
        except:
            print("Pass")


    def upload_data(self, user):
        try:
            alldata = self.get_follower_data(user["username"])
            alldata["posts"] = []
            if alldata["is_private"] == False: alldata["posts"] = self.startpostScrape(alldata)
            alldata['pk'] = alldata['id']
            self.upload_user(alldata)
            # if not os.path.exists(f"{userpath}/followers/{alldata['username']}"):
            #     os.mkdir(f"{userpath}/followers/{alldata['username']}")

            # self.download_image(alldata["profile_pic_url_hd"], f"{userpath}/followers/{alldata['username']}/pfp.jpg",)
            # open(
            #     f"{userpath}/followers/{alldata['username']}/user.json",
            #     "w+",
            # ).write(json.dumps(alldata, indent=4))
            # if not os.path.exists(
            #     f"{userpath}/followers/{alldata['username']}/pictures"
            # ):
            #     os.mkdir(
            #         f"{userpath}/followers/{alldata['username']}/pictures"
            #     )

            # for post in alldata["posts"][:20]:
            #     self.download_image(
            #         post["image_versions2"]["candidates"][0]["url"],
            #         f"{userpath}/followers/{alldata['username']}/pictures/{post['code']}.png",
            #     )
            # print(user)
            self.pprint(f"Scraped full data for @{user['username']} | {self.users.index(user) + 1}/{len(self.users)}")

        except Exception as e:
            unscraped_data = user.pop('_id', None)

            self.db.instagram.unscraped_users.insert_one(user)
            
            self.pprint(f"Error @{user['username']}: {e} | {self.users.index(user) + 1}/{len(self.users)}")
            


    def startScraper(self):
        self.ui()
        next_max_id = None
        self.before = 0
        user = self.db.instagram.maxids.find_one({"username": self.user})
        if user == None:
            self.db.instagram.maxids.insert_one({"username": self.user, "maxid": next_max_id, "amount" : 0})
        else:
            next_max_id = user["maxid"]
            self.before = user["amount"]
        self.chunkusers = []
        scrapedUser = self.get_follower_data(self.user)
        username = scrapedUser["username"]
        
        # if not os.path.exists(f"users/{username}"):
        #     os.mkdir(f"users/{username}")
        # if not os.path.exists(f"users/{username}"):
        #     os.mkdir(f"users/{username}")
        # if not os.path.exists(f"users/{username}/followers"):
        #     os.mkdir(f"users/{username}/followers")

        # open(f"users/{username}/user.json", "w+").write(json.dumps(scrapedUser, indent=4))
        # self.download_image(
        #     scrapedUser["profile_pic_url_hd"], f"users/{username}/pfp.jpg"
        # )

        # if os.path.isfile(f"users/{username}/followers.json"):
        #     followers = json.loads(open(f"users/{username}/followers.json","r").read())
        #     next_max_id = followers['next_max_id']
        #     self.chunkusers = followers['users']
        # else:
        #     open(f"users/{username}/followers.json", "w+").write(json.dumps({
        #         "next_max_id" : None,
        #         "users" : []
        #     }, indent=4)) 
        
        maxID = self.scrape_followers(scrapedUser, next_max_id)
        # for user in self.chunkusers:
        #     if "_id" in user:
        #         index = self.chunkusers.index(user)
        #         del self.chunkusers[index]["_id"]

        # open(f"users/{username}/followers.json", "w+").write(
        #     json.dumps({
        #         "next_max_id" : str(maxID),
        #         "users" : self.chunkusers
        #     }, indent=4)
        # )
        self.pprint(f"Scraped {len(self.chunkusers)} users in total")
        self.ui()


    def find_val(self, array, key, value):
        for k in array:
            if k[key] == value:
                return True
        return False
