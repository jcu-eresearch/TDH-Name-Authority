#This cleanup script loops through the solr index for all People who have not been published.
#It then updates the security_filter to "admin", thus preventing the outside world from viewing people unless then have published data.
#They must have published data on ReDBox before they are visible.

#The harvest script Parties_People_TDH.py has been modified to set the security_filter to 'admin' when people are first harvested and to then 
# change the security_filter to 'guest' when they are 'published'. 

#This python script uses sunburnt to query solr and perform the work:
# http://opensource.timetric.com/sunburnt/index.html

import argparse
import sunburnt

parser = argparse.ArgumentParser(description='Perform data cleanup of People - non Published people will be hidden from public view')
parser.add_argument('mintURL', metavar='mintURL', help='The url of The Mint. e.g. http://localhost:9001/solr/fascinator/')

if parser.parse_args().mintURL is not None:
    print 'Using the following URL to hide non published people on The Mint: ', parser.parse_args().mintURL
    
    solr_interface = sunburnt.SolrInterface(parser.parse_args().mintURL)
    
    query = solr_interface.query(solr_interface.Q("jcu.edu.au/parties/people") & solr_interface.Q(security_filter="guest") & ~solr_interface.Q(published="true"))
    
    startResult = 0
    rowsTotal = 1000
    
    responses = query.paginate(start=startResult, rows=rowsTotal).execute()
    
    print 'Response status: ', responses.status 
    
    while responses:
        for i in range(len(responses)):
            response = responses[i]
            print "response['Email']: ", response['Email']
            response['security_filter'] = (u'admin', )
            #the item_type field is indexed but not stored in the solr document. ReDBOx uses this field in queries
            #Need to add it back in when adding the updated document 
            response['item_type'] = 'object'
            solr_interface.add(response)
            
        print "Commit response: ", solr_interface.commit()
        #startResult = startResult + rowsTotal
        print "Reading more People: start: ", startResult
        responses = query.paginate(start=startResult, rows=rowsTotal).execute()
        print 'Response status: ', responses.status
