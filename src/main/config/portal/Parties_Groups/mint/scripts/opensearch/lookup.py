from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Exception

# JCU - this script has been customised to support the JCU restructure where the Groups were changed.
# This script checks for a searchTerm containing 'currentGroups'. If present, only records containing 'Active_To' value of ''
# are returned to the end user. This ensures that users of the Dashboard can only select current groups.
# All calls to obtain groups from the Dashboard have been modified to support this feature.
#
#For all other parts of the system, all records are retrieved to ensure that old Groups will still be available if 'published' records are modified.
# Jay: but how can I indicate old vs new rows. append Name ?? ugly but works.


class LookupData:
    def __activate__(self, context):
        self.log = context["log"]
        self.services = context["Services"]
        self.portalId = context["portalId"]
        self.formData = context["formData"]
        
        request = context["request"]
        request.setAttribute("Content-Type", "application/json")
        
        self.__solrData = self.__getSolrData()
        self.__results = self.__solrData.getResults()

        baseUrl = context["systemConfig"].getString("", ["urlBase"])
        if baseUrl.endswith("/"):
            baseUrl = baseUrl[:-1]
        self.__baseUrl = baseUrl
    
    def getBaseUrl(self):
        return self.__baseUrl + "/" + self.portalId
    
    def getLink(self):
        return ""
    
    def getTotalResults(self):
        return self.__solrData.getNumFound()
    
    def getStartIndex(self):
        return self.getFormData("startIndex", "0")
    
    def getItemsPerPage(self):
        return self.getFormData("count", "25")
    
    def getRole(self):
        return "request"
    
    def getSearchTerms(self):
        return self.getFormData("searchTerms", "")
    
    def getStartPage(self):
        #index = int(self.getStartIndex())
        #perPage = int(self.getItemsPerPage())
        return 0 #(index / perPage)
    
    def getResults(self):
        return self.__solrData.getResults()
    
    def getValue(self, doc, field):
        value = doc.getFirst(field)
        if value:
            return value.replace('"',"'").replace('\n','').strip()
        return ""
    
    def getValueList(self, doc, field):
        valueList = doc.getList(field)
        if valueList.isEmpty():
            return []
        return ('["%s"]' % '", "'.join(valueList) + "").strip()
    
    def __getSolrData(self):

        # JCU: checking for searchTerm: currentGroups
        searchTerms = self.getSearchTerms()
        currentGroups = False
        if searchTerms != "":
            terms = searchTerms.split(" ")
            if (len(terms) == 1) and (terms[0] == 'currentGroups'):
                currentGroups = True

        query = "*:*"

        portal = self.services.portalManager.get(self.portalId)
        sq = portal.searchQuery
        if sq not in ["", "*:*"]:
            query = query + " AND " + portal.searchQuery
        req = SearchRequest(query)
        req.setParam("fq", 'item_type:"object"')
        if portal.query:
            req.addParam("fq", portal.query)

        if currentGroups:
            req.addParam("fq", 'Active_To:""')

        req.setParam("fl", "score")
        req.setParam("sort", "score desc, f_dc_title asc")
        req.setParam("start", self.getStartIndex())
        req.setParam("rows", self.getItemsPerPage())
        
        try:
            out = ByteArrayOutputStream()
            indexer = self.services.getIndexer()
            indexer.search(req, out)
            return SolrResult(ByteArrayInputStream(out.toByteArray()))
        except Exception, e:
            self.log.error("Failed to lookup '{}': {}", prefix, e.getMessage())
        
        return SolrResult('{"response":{"numFound":0}}')
    
    def getFormData(self, name, default):
        value = self.formData.get(name)
        if value is None or value == "":
            return default
        return value
