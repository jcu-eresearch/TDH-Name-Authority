import os
import json
import argparse

from os.path import join, getsize

##
# This data fix program is designed to clean up the 'relationships' in metadata.json due to a problem with the 'Activities_TDH'
# data when originally imported into The Mint.
# This fix only needs to be executed once.
# 1. Check the queues in Mint and ReDBox. If they are empty, stop both servers. Back up the 'storage' folder in 'The Mint'
# 2. Restart Mint and ReDBox.
# 3. Reharvest the Software_Services_TDH and Activities_TDH data. Don't forget to regenerate the Activities_TDH data first
# 4. Run this script against mint/storage folder.
# 5. Log into the Mint as admin, change to the 'Research Activities' view, 'Reharvest View. Do the same for 'Services'. 
# 6. The 'Research Activities' data, should now be fixed. Software Services needs to be reharvested for curation of future metadata. 
##
 
parser = argparse.ArgumentParser(description='Perform data cleanup of Activities')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within The Mint.')

print 'Using the following path to process mint cleanup: ', parser.parse_args().storagePath

for root, dirs, files in os.walk(parser.parse_args().storagePath):
     if 'metadata.json' in files:
        #print os.path.join(root, 'metadata.json')
        try:
             file = open(os.path.join(root, 'metadata.json'), 'r+')
             jsonData = json.load(file)
             file.close()
             if  (jsonData["recordIDPrefix"] == "jcu.edu.au/activities/"):
                 if "relationships" in jsonData:
                    #print jsonData["relationships"]

                    jsonDataChanged = False
                    
                    #Removing OTHER_INVESTIGATORS from the relationships.
                    #[:] - causes python to make an internal copy of relationships as a subset, loop through the copy.
                    for relationship in jsonData["relationships"][:]:
                        identifier = relationship["identifier"]
                        for otherInvestigator in jsonData["data"]["OTHER_INVESTIGATORS"]:
                            #print otherInvestigator
                            #print jsonData["relationships"]
                            if  otherInvestigator in identifier:
                                jsonData["relationships"].remove(relationship)
                                jsonDataChanged = True

                    #Now removing the space incorrectly inserted in the identifier
                    for relationship in jsonData["relationships"]:
                        relationship["identifier"] = relationship["identifier"].replace(" ", "")
                        jsonDataChanged = True

                    if (jsonDataChanged== True):
                        # magic happens here to make it pretty-printed
                        file = open(os.path.join(root, 'metadata.json'), 'w')
                        file.write(json.dumps(jsonData, indent=4, sort_keys=True))
                        file.close()
                        print("Record processed: ", os.path.join(root, 'metadata.json'))
        except ValueError as e:
            print ("Oops, there is a dodgy one: ", os.path.join(root, 'metadata.json')) 
            print ("ValueError: ", e)