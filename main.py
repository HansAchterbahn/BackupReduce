import os
import re
from datetime import datetime
import natsort
import logging
from collections import defaultdict

def find_first_unique_item_in_list(items:list, amount:int=0, direction:str= "backward"):
    # looks for the first unique entries in a given list and returns these entries and their IDs
    # parameters
    # - items       :list:  list with entries
    # - amount      :int:   amount of unique items to be returned
    # - direction   :str:   describes the count direction in the list of unique items for return

    # loops to the list, check for unique items and add them to a unique item list
    items_unique = []
    last_item = ""
    for i, item in enumerate(items):
        if item == last_item:
            pass
        else:
            items_unique.append([i, item])
            last_item = item

    # reduces the unique item list according to unique item amount and counting direction
    if direction == "forward":
        return items_unique[:amount]
    elif direction == "backward":
        return items_unique[-amount:]
    else:
        return items_unique

def reduce_backup_files(file_amount:int = 7, file_path:str = "", remove_folder_path = "remove"):
    # Parameters
    # - file_amount         :int:   files to ceeped per type (yearly, monthly, weekly, daily)
    # - file_path           :str:   path to the backup files
    # - remove_folder_path  :str:   path/folder to move the unwanted files to (ex. remove, /dev/null)

    # Set up logging
    #logging.basicConfig(filename="reduce" + '.log', format='%(message)s', level=logging.INFO)
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("["+file_path+" | "+str(datetime.now())+"]")


    # read the file list and sort it
    files = [f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]
    files = natsort.natsorted(files)
    files_ignored = []

    prefixes_dict = dict()
    prefixes = set([])
    for file in files:
        match = re.search("(^[^_]*)_?([0-9]{4}-[0-9]{2}-[0-9]{2})", file)
        if match:
            prefix = match.group(1)
            if prefix in prefixes:
                prefixes_dict[prefix].append(file)
            else:
                prefixes_dict[prefix] = [file]
                prefixes.add(prefix)
        else:
            files_ignored.append(file)


    # create remove folder if not exist
    try:
        os.makedirs(remove_folder_path)
    except:
        pass

    # generate keep and remove files list & remove files from remove file list
    for prefix in prefixes_dict:
        keep_files, remove_files = calculate_keep_and_remove_files(files=prefixes_dict[prefix], backup_amount=file_amount)
        logging.info("Remove prefix list %s: \n- %s", prefix, remove_files)
        for file in remove_files:
            os.rename(str(file_path + "/" + file), str(remove_folder_path + "/" + file))





def calculate_keep_and_remove_files(files:list, backup_amount:int=7, yearly:bool=True, monthly:bool=True, weekley:bool=True, daily:bool=True):
    # create empty lists for yearly, monthly, weekly and daily backups
    yearly = []
    monthly = []
    weekly = []
    daily = []

    # sort files in to the yearly, monthly, weekly and daily backup lists
    for i, file in enumerate(files):
        match = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", file)
        if match:
            date = match.group()
            yearly.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y"))
            monthly.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m"))
            weekly.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%V"))
            daily.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d"))

    # find first unique items in wanted amount and direction for yearly, monthly, weekly and daily backups
    yearly = find_first_unique_item_in_list(yearly, backup_amount, "backward")
    monthly = find_first_unique_item_in_list(monthly, backup_amount, "backward")
    weekly = find_first_unique_item_in_list(weekly, backup_amount, "backward")
    daily = find_first_unique_item_in_list(daily, backup_amount, "backward")

    # log separat keep lists
    #logging.info("Years match: %s", yearly)
    #logging.info("Month match: %s", monthly)
    #logging.info("Weeks match: %s", weekly)
    #logging.info("Days match: %s",  daily)

    # merge all wanted unique items together in the keep file list by looping to every separate list
    keep_files = set([])
    keep_ids = set([])
    for list in [daily, weekly, monthly, yearly]:
        for item in list:
            keep_ids.add(item[0])
            keep_files.add(files[item[0]])

    #logging.info("Keep files: %s", natsort.natsorted(keep_files))

    # create list of files to be removed
    remove_files = []
    for file in files:
        if file not in keep_files:
            remove_files.append(file)

    return keep_files, remove_files


if __name__ == "__main__":
    # user Settings
    backups = [
        {"path": ".Contacts-Backup",  "amount": 7},
        {"path": ".Calendar-Backup",  "amount": 7},
        {"path": ".KeePassXC-Backup", "amount": 7},
        {"path": ".Signal-Backup",    "amount": 4}
    ]

    # run script
    for backup in backups:
        reduce_backup_files(file_amount=backup["amount"], file_path=backup["path"], remove_folder_path=backup["path"]+"/remove")
