from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import time
import os
import pexpect
import json
from json import loads, dump
from pymongo import MongoClient

config = loads(open("config.json","r").read())
client=MongoClient(config['db'])

app = FastAPI()

# Declare subprocess as a global variable
subprocess_instance = None
def pprint(self, text):
        print(f"[ {Fore.GREEN}+{Fore.RESET} ] {text}")
def change_mode(config_path, new_mode):
    # Load the existing configuration from the file
    with open(config_path, 'r') as file:
        config = json.load(file)

    # Update the "mode" value
    config['mode'] = new_mode

    # Write the updated configuration back to the file
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=2)

def terminate_subprocess(process):
    try:
        # Terminate the subprocess
        process.terminate()
        process.wait(timeout=5)  # Wait for the process to finish gracefully
    except Exception as e:
        print(f"Error terminating subprocess: {e}")

def run_script():
    global subprocess_instance  # Use the global variable

    # Replace the path with the actual path to your Python script
    script_path = "scraper.py"
    config_path = 'config.json'
    new_mode_value = '4'  # Change this to the desired mode value
    change_mode(config_path, new_mode_value)

    # Check if there's an existing subprocess
    if subprocess_instance:
        terminate_subprocess(subprocess_instance)

    # Start a new subprocess
    subprocess_instance = subprocess.Popen(["python", script_path])

def run_script2():
    global subprocess_instance  # Use the global variable

    # Replace the path with the actual path to your Python script
    script_path = "scraper.py"
    config_path = 'config.json'
    new_mode_value = '2'  # Change this to the desired mode value
    change_mode(config_path, new_mode_value)

    # Check if there's an existing subprocess
    if subprocess_instance:
        terminate_subprocess(subprocess_instance)

    # Start a new subprocess
    subprocess_instance = subprocess.Popen(["python", script_path])

# Schedule the function to run every day at 12 AM BDT
scheduler = BackgroundScheduler()
scheduler.add_job(run_script, CronTrigger(hour=4, minute=54, second=0, timezone="Asia/Dhaka"))

#scheduler.add_job(run_script, CronTrigger(minute=(time.localtime().tm_min + 3) % 60)) #for degug purpose 
scheduler.start()

@app.get("/start")
def read_root():
    # Execute the modified external Python script

    run_script2()
    # Check if the script executed successfully
    return {"message":"Scrapper running!"}

@app.get("/end")
def read_root():
    # Execute the modified external Python script
    global subprocess_instance 
    terminate_subprocess(subprocess_instance)
    # Check if the script executed successfully
    return {"message":"Scrapper terminated!"}

@app.get("/checkForNewUserManually")
def read_root():
    # Execute the modified external Python script

    run_script()
    # Check if the script executed successfully
    return {"message":"New User Checker running!"}


# @app.get("/deleteUsers")
# def read_root():
#     db = client['instagram']
#     collection = db['users']
#     deletion_limits=18000
#     # Step 1: Find the ObjectId threshold
#     # Get the last 400 documents based on the _id in descending order
#     last_docs = collection.find().sort([('_id', -1)]).limit(deletion_limits)
    
#     # Get the _id of the 400th document
#     last_id = None
#     for doc in last_docs:
#         last_id = doc['_id']
    
#     # Step 2: Delete documents
#     # Delete documents with _id less than or equal to the threshold _id
#     if last_id is not None:
#         collection.delete_many({'_id': {'$lte': last_id}})
#         return {"message":f"Deleting last {deletion_limits} scrapped users!"}




    
