import os
import json
import argparse

from os.path import join, getsize

##
# This data fix program is designed to clean up the 'localPid' in TF_OBJ_META due to a problem with the curation of Software Services.
# The localPid should be "localPid=jcu.edu.au/tdh/service/australian-birds"
# This fix only needs to be executed once.
# 1. Check the queues in Mint and ReDBox. If they are empty, stop both servers. Back up the 'storage' folder in 'The Mint'
# 2. Restart Mint and ReDBox.
# 4. Using the updated Software_Services_TDH.json reharvest.
# 4. Run this script against mint/storage folder.
# 5. Log into the Mint as admin, change to the 'Services' view, 'Reharvest View.
# 6. Reindex the individual Software Services, 1 by 1, but there are only 4 services. 
#
 
parser = argparse.ArgumentParser(description='Perform data cleanup of Software Services')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within The Mint.')

print 'Using the following path to process mint cleanup: ', parser.parse_args().storagePath

for root, dirs, files in os.walk(parser.parse_args().storagePath):
     if 'metadata.json' in files:
        #print os.path.join(root, 'metadata.json')
        try:
             file = open(os.path.join(root, 'metadata.json'), 'r+')
             jsonData = json.load(file)
             file.close()
             if  (jsonData["recordIDPrefix"] == "jcu.edu.au/tdh/service/"):
                 file = open(os.path.join(root, 'TF-OBJ-META'), 'r+')
                 ##not a json formatted file. :)
                 fileData = file.read()
                 file.close()
                 if  ("localPid=https\://eresearch.jcu.edu.au/nameauthority/published/detail/4a80b87b02b306dc68dbfcd47e66953c" in fileData):
                     fileData = fileData.replace("localPid=https\://eresearch.jcu.edu.au/nameauthority/published/detail/4a80b87b02b306dc68dbfcd47e66953c", "localPid=jcu.edu.au/tdh/service/australian-birds")
                 else:
                     identifier = jsonData["metadata"]["dc.identifier"]
                     fileData = fileData + "localPid=" + identifier + "\n"
                 print ("fileData: ", fileData)
                 file = open(os.path.join(root, 'TF-OBJ-META'), 'w')
                 file.write(fileData)
                 file.close()
                 print("Record processed: ", os.path.join(root, 'TF-OBJ-META'))
        except ValueError as e:
            print ("Oops, there is a dodgy one: ", os.path.join(root, 'TF_OBJ_META')) 
            print ("ValueError: ", e)