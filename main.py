import os
import re
from datetime import datetime
import natsort
import logging

def find_first_unique_item_in_list(items:list, amount:int=0, direction:str= "backward"):
    # looks for the first unique entries in a given list and returns these entries and their IDs
    # items     :list:  list with entries
    # amount    :int:   amount of unique items to be returned
    # direction :str:   describes the count direction in the list of unique items for return

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

if __name__ == "__main__":

    # User definitions
    file_ammount = 7                            # How many files should be ceeped per type (yearly, monthly, weekly, dayly)?
    file_location = ".Contacts-Backup"          # Where are the files located?
    remove_folder = "remove"                    # How should the folder be named to move the unwanted files to? (ex. remove, /dev/null)

    # Set up logging
    #logging.basicConfig(filename='remove.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(filename=file_location+'.log', format='%(message)s', level=logging.INFO)
    logging.info("["+str(datetime.now())+"]")


    # read the file list and sort it
    files = [f for f in os.listdir(file_location) if os.path.isfile(os.path.join(file_location, f))]
    files = natsort.natsorted(files)

    # create empty lists for yearly, monthly, weekly and daily backups
    yearly = []
    monthly = []
    weekly = []
    daily = []

    # sort files in to the yearly, monthly, weekly and daily backup lists
    for i, file in enumerate(files):
        date = re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", file).group()
        yearly.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y"))
        monthly.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m"))
        weekly.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%V"))
        daily.append(datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d"))

    # find first unique items in wanted amount and direction for yearly, monthly, weekly and daily backups
    yearly = find_first_unique_item_in_list(yearly, file_ammount, "backward")
    monthly = find_first_unique_item_in_list(monthly, file_ammount, "backward")
    weekly = find_first_unique_item_in_list(weekly, file_ammount, "backward")
    daily = find_first_unique_item_in_list(daily, file_ammount, "backward")

    # log separat keep lists
    logging.info("Years match: %s", yearly)
    logging.info("Month match: %s", monthly)
    logging.info("Weeks match: %s", weekly)
    logging.info("Days match: %s",  daily)

    # merge all wanted unique items together in the keep file list by looping to every separate list
    keep_files = set([])
    keep_ids = set ([])
    for list in [daily, weekly, monthly, yearly]:
        for item in list:
            keep_ids.add(item[0])
            keep_files.add(files[item[0]])

    logging.info("Keep files: %s", natsort.natsorted(keep_files))

    # create list of files to be removed
    remove_files = []
    for file in files:
        if file not in keep_files:
            remove_files.append(file)

    # create remove folder if not exist
    try:
        os.makedirs(file_location + "/" + remove_folder)
    except:
        pass

    logging.info("Remove list: %s", remove_files)

    # remove files from remove list
    for file in remove_files:
        os.rename(str(file_location+"/"+file), str(file_location+"/"+remove_folder+"/"+file))
