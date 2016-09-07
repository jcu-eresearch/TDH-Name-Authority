#
# Rules file for Research Activity data
#
import time

from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple

from org.apache.commons.io import IOUtils

class IndexData:
    def __init__(self):
        pass

    def __activate__(self, context):
        # Prepare variables
        self.index = context["fields"]
        self.indexer = context["indexer"]
        self.object = context["object"]
        self.payload = context["payload"]
        self.params = context["params"]
        self.utils = context["pyUtils"]
        self.config = context["jsonConfig"]
        self.log = context["log"]        

        # Common data
        self.__newDoc()

        # Real metadata
        if self.itemType == "object":
            self.__basicData()
            self.__metadata()

        # Make sure security comes after workflows
        self.__security(self.oid, self.index)

    def __newDoc(self):
        self.oid = self.object.getId()
        self.pid = self.payload.getId()
        metadataPid = self.params.getProperty("metaPid", "DC")

        self.utils.add(self.index, "storage_id", self.oid)
        if self.pid == metadataPid:
            self.itemType = "object"
        else:
            self.oid += "/" + self.pid
            self.itemType = "datastream"
            self.utils.add(self.index, "identifier", self.pid)

        self.utils.add(self.index, "id", self.oid)
        self.utils.add(self.index, "item_type", self.itemType)
        self.utils.add(self.index, "last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.utils.add(self.index, "harvest_config", self.params.getProperty("jsonConfigOid"))
        self.utils.add(self.index, "harvest_rules", self.params.getProperty("rulesOid"))
        self.utils.add(self.index, "display_type", "research_activities")

        self.item_security = []

    def __basicData(self):
        self.utils.add(self.index, "repository_name", self.params["repository.name"])
        self.utils.add(self.index, "repository_type", self.params["repository.type"])
        # Persistent Identifiers
        pidProperty = self.config.getString(None, ["curation", "pidProperty"])
        if pidProperty is None:
            self.log.error("No configuration found for persistent IDs!")
        else:
            pid = self.params[pidProperty]
            if pid is not None:
                self.utils.add(self.index, "known_ids", pid)
                self.utils.add(self.index, "pidProperty", pid)
                self.utils.add(self.index, "oai_identifier", pid)
        self.utils.add(self.index, "oai_set", "Activities")
        # Publication
        published = self.params["published"]
        if published is not None:
            self.utils.add(self.index, "published", "true")

    def __metadata(self):
        self.utils.registerNamespace("dc", "http://purl.org/dc/terms/")
        self.utils.registerNamespace("foaf", "http://xmlns.com/foaf/0.1/")

        jsonPayload = self.object.getPayload("metadata.json")
        json = self.utils.getJsonObject(jsonPayload.open())
        jsonPayload.close()

        metadata = json.getObject("metadata")
        self.utils.add(self.index, "dc_identifier", metadata.get("dc.identifier"))

        data = json.getObject("data")
        #Appending OTHER_INVESTIGATORS to the description
        description = data.get("DESCRIPTION")
        otherInvestigators = data.get("OTHER_INVESTIGATORS")
        
        #Only do this once. 
        if not "Investigators from other institutions include:" in description:
            if  otherInvestigators is not None:
                if (len(otherInvestigators) > 0):
                    description = description + " Investigators from other institutions include: "
                    for i in range(len(otherInvestigators)):
                        otherInvestigator = otherInvestigators[i]
                        if (i == (len(otherInvestigators) - 1)):
                            description = description + otherInvestigator
                        else:
                            description = description + otherInvestigator + ", "
                    #update data payload
                    data["DESCRIPTION"] = description
                    json.getJsonObject().putAll(data)
                    self.__updatePayload(json.getObject())

        self.utils.add(self.index, "dc_description", description)         
                
        self.utils.add(self.index, "grant_number", data.get("ID"))
        self.utils.add(self.index, "dc_date_submitted", data.get("SUBMIT_YEAR"))
        self.utils.add(self.index, "dc_date", data.get("START_YEAR"))
        self.utils.add(self.index, "dc_date_end", data.get("END_YEAR"))
        self.utils.add(self.index, "dc_title", data.get("TITLE"))
        self.utils.add(self.index, "foaf_name", data.get("INSTITUTION"))
        self.utils.add(self.index, "dc_subject", data.get("DISCIPLINE"))
        self.utils.add(self.index, "dc_format", "application/x-mint-research-activity")
        self.__indexList("dc_contributor", data.get("INVESTIGATORS"))


        # Known IDs
        identifier = json.getString(None, ["metadata", "dc.identifier"])
        if identifier is not None:
            self.utils.add(self.index, "known_ids", identifier)

    def __security(self, oid, index):
        roles = self.utils.getRolesWithAccess(oid)
        if roles is not None:
            for role in roles:
                self.utils.add(index, "security_filter", role)
        else:
            # Default to guest access if Null object returned
            schema = self.utils.getAccessSchema("derby")
            schema.setRecordId(oid)
            schema.set("role", "guest")
            self.utils.setAccessSchema(schema, "derby")
            self.utils.add(index, "security_filter", "guest")

    def __indexList(self, name, values):
        if values is not None:
            for value in values:
                self.utils.add(self.index, name, value)
                
    def __updatePayload(self, data):
        # Get and parse
        payload = self.object.getPayload("metadata.json")
        json = JsonSimple(payload.open())
        payload.close()

        # Merge
        json.getJsonObject().putAll(data)

        # Store it
        inStream = IOUtils.toInputStream(json.toString(True), "UTF-8")
        try:
            self.object.updatePayload("metadata.json", inStream)
        except StorageException, e:
            self.log.error("Error updating 'metadata.json' payload for object '{}'", self.oid, e)
