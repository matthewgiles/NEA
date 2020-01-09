import fileManagement
import entities
import datetime


class EntityHandler(object):
    """This object manages the interfacing between the entities module (i.e the database) and any other parts of the
    code"""
    def __init__(self):
        """The constructor has no input or output but gets the dictionary of entities from a local file"""
        # Creating an instance of a FileManager
        self.__fM = fileManagement.FileManager()
        try:
            # Trying to load the contents of entities.p into the self.__entities variable
            self.__entities = self.__fM.loadFile("entities.p")
        except FileNotFoundError:
            """If the file cannot be found, create a dictionary containing all the necessary entity types as keys and 
            set their values to an empty dictionary"""
            self.__entities = {"Teacher": {}, "Note": {}, "Assistant": {}, "Student": {}, "Class": {}, "Venue": {},
                               "Event": {}, "AssistantClass": {}, "AssistantEvent": {}, "TeacherClass": {},
                               "TeacherEvent": {}, "StudentClass": {}, "StudentEvent": {}, "VenueClass": {}, "VenueEvent": {},
                               "UniformType": {}, "UniformOrder": {}, "UniformOrderLine": {}, "User": {}}

    def updateRecord(self, entityType, ID, data):
        """This function updates a record in the database (this can be updating or creating). It takes an entityType,
        and ID and a list of data as its input. It then returns the ID of the record that has been dealt with."""
        if ID is None:
            """If there is the value of ID is None, then a new entity is being created. Create a temporary instance of 
            the object matching entityType and set its attributes to 'data' by calling update()."""
            tempEntity = getattr(entities, entityType)()
            tempEntity.update(data)
            # Hash the temporary entity object and convert this to a string to be used as the ID of the record
            ID = str(hash(tempEntity))
            """Add a new value to the dictionary at key entityType in self.__entities with ID as the key and the 
            temporary entity as the value"""
            self.__entities[entityType][ID] = tempEntity
        else:
            # If there is a value in self.__entities at key entityType and then key ID, update this value with 'data'
            self.__entities[entityType][ID].update(data)
        return ID

    def getUserAccess(self, username):
        """This function returns the user-access level of user with an ID matching 'username'"""
        if username in self.__entities["User"].keys():
            return self.__entities["User"][username].getAccess()

    def updateUser(self, username, data):
        """This function takes a username and a list of data as its input, updates the User account matching username and
        returns username. It follows a very similar procedure to updateRecord, however, username will not be None as this
        is user defined not automatically generated."""
        if username in self.__entities["User"].keys():
            self.__entities["User"][username].update(data)
        else:
            tempEntity = entities.User()
            tempEntity.update(data)
            self.__entities["User"][username] = tempEntity
        return username

    def getNoteRecordID(self, ID):
        """This function takes the ID of a Note and returns the corresponding note's foreign keys"""
        return self.__entities["Note"][ID].getIDs()

    def getData(self, entityType, ID):
        """This function takes an entityType and ID. It returns the attribute values (by calling returnValues) of the
        record of type 'entityType' matching ID"""
        return self.__entities[entityType][ID].returnValues()

    def getOrderLines(self, ID):
        """This function takes an ID as its input and returns all of the UniformOrderLine records that contain ID (the
        ID of an order) as one of their foreign keys"""
        output = []
        for record in self.__entities["UniformOrderLine"]:
            if self.__entities["UniformOrderLine"][record].getOrderID() == ID:
                output.append(record)
        return output

    def getEmail(self, entityType, ID):
        """This fucntion takes an entity type and ID as its input and returns the email address of a record with ID 'ID'
        and of type 'entityType'"""
        return self.__entities[entityType][ID].returnEmail()

    def getNumber(self, entityType, ID):
        return self.__entities[entityType][ID].returnNumber()

    def getEntities(self):
        """This function returns the dictionary of entities that is the private attribute of this class"""
        return self.__entities

    def getCost(self, ID):
        """This function takes an ID as its input and returns the hourly hire cost of a venue matching ID"""
        return self.__entities["Venue"][ID].returnCost()

    def getUsers(self):
        """This function returns the list of users in the database"""
        return self.__entities["User"]

    def deleteOrderLines(self, ID):
        """This function takes the ID of an order as input and deletes all UniformOrderLine records which contain ID
        in the foreign keys"""
        toDelete = []
        for record in self.__entities["UniformOrderLine"]:
            if self.__entities["UniformOrderLine"][record].getOrderID() == ID:
                # Creating a list of UniformOrderLine records that contain ID in their foreign key
                toDelete.append(record)
        """Proceeding to delete all the times in the toDelete list. This is done in a separate loop to stop dictionary 
        size changing mid iteration"""
        for item in toDelete:
            del self.__entities["UniformOrderLine"][item]

    def deleteRecord(self, entityType, ID):
        """This function takes an entity type and an ID as its input and deletes the record of type entityType matching
        ID"""
        toDelete = []
        # First any relationship type records containing ID in their foreign keys are added to a list of items to delete
        for key in ["AssistantClass", "AssistantEvent", "StudentClass", "StudentEvent", "TeacherClass", "TeacherEvent",
                    "VenueClass", "VenueEvent", "Note"]:
            if entityType in key or key == "Note":
                for record in self.__entities[key]:
                    if ID in self.__entities[key][record].getIDs():
                        toDelete.append([key, record])
        # Deleting any records which are relationships involving the record with key ID
        for item in toDelete:
            del self.__entities[item[0]][item[1]]
        # Deleting the record of type entityType matching ID
        del self.__entities[entityType][ID]

    def deleteEntityRelationship(self, entityType, ID, parentID):
        """This function takes an entity type (which will be a relationship) and the ID of a record and the ID of another
        parent record. It finds any relationships with both foreign keys ID and parentID then it deletes it"""
        toDelete = None
        for record in self.__entities[entityType]:
            if ID and parentID in self.__entities[entityType][record].getIDs():
                toDelete = record
        del self.__entities[entityType][toDelete]

    def saveFile(self):
        """This function saves the contents of the self.__entities dictionary back into the local entities file"""
        self.__fM.saveFile("entities.p", self.__entities)

    def createRelationship(self, relationship, parentID, ID):
        """This function takes a relationship, parentID and ID as its input and creates a new relationship of type
        'relationship' with foreign keys parentId and ID"""
        check = True
        # The following checks that such a relationship between parentID and ID does not already exist
        for record in self.__entities[relationship]:
            if parentID in self.__entities[relationship][record].getIDs() and ID in self.__entities[relationship][record].getIDs():
                check = False
        # If no relationship exists then a new one is created with a similar method to the updateRecord function
        if check:
            tempEntity = getattr(entities, relationship)()
            tempEntity.update(parentID, ID)
            ID = str(hash(tempEntity))
            self.__entities[relationship][ID] = tempEntity

    def getForeigns(self, relationship, ID):
        """This function takes a relationship and ID as its input and returns the ID and other foreign key of the
        record of type 'relationship' which contains 'ID' as one of its foreign keys"""
        output = []
        for record in self.__entities[relationship]:
            value = self.__entities[relationship][record]
            """If the first foreign key is ID then return a list containing the ID of the relationship and the second 
            foreign key"""
            if value.getIDs()[0] == ID:
                output.append([record, value.getIDs()[1]])
            """If the second foreign key is ID then reutrn a list containing the ID of the relationship and the first 
            foreign key"""
            if value.getIDs()[1] == ID:
                output.append([record, value.getIDs()[0]])
        return output

    def accountExists(self, username):
        """This function takes a username as its input and returns True if that username exists as the primary key of
        a User account object in the database and returns False if not"""
        if username in self.__entities["User"].keys():
            return True
        else:
            return False

    def todayClasses(self):
        """This function returns a list of classes that take place on the current day of the week"""
        IDList = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for aclass in self.__entities["Class"]:
            """If the current day of the week as an integer is the same as the index of the day of the week of the class
            in the list 'days' then append the ID of that class to IDList"""
            if datetime.datetime.today().weekday() == days.index(self.__entities["Class"][aclass].returnDay()):
                IDList.append(aclass)
        return IDList

    def monthEvents(self):
        """This function returns a list of events that start in the current month"""
        IDList = []
        for event in self.__entities["Event"]:
            eventDateObject = self.__entities["Event"][event].returnStartDate()
            # If the month and year of the event's start date is that of the current date then append event to IDList
            if eventDateObject.month == datetime.datetime.now().month and eventDateObject.year == datetime.datetime.now().year:
                IDList.append(event)
        return IDList


class Searcher(object):
    """This object provides the ability to search for data in the entities dictionary and uses an entityHandler instance
    to facilitate this"""
    def __init__(self, entityHandler):
        """The constructor takes an entityHanlder as its input. It creates an empty dictionary that will be the list of
        results of a search and also gets the entities dictionary from the entityHandler it is passed."""
        self.__results = {}
        self.__entities = entityHandler.getEntities()

    def getNotes(self, ID):
        """This function receives the ID of a record in the database as input (this a Person type) and returns any notes
        which are about the record of that ID"""
        IDList = []
        for n in self.__entities["Note"]:
            # Append n (the ID of the current note) to the output list if the input variable ID is its foreign key
            if ID == self.__entities["Note"][n].getIDs():
                IDList.append(n)
        return IDList

    def search(self, entry, types):
        """This function takes a user text entry and list of types as its input. It returns a dictionary of results
        containing records which may relate to the text in 'entry' and are of a type within the list 'types'."""
        # Clearing the results dictionary
        self.__results = {}
        # Iterating through the types in the passed variable 'types'
        for atype in types:
            IDList = []
            for record in self.__entities[atype]:
                # If the user did not input any text in the search bar then return all records of atype
                if entry == "":
                    IDList.append(record)
                else:
                    # Get the list of search related attributes from 'record'
                    searchList = self.__entities[atype][record].getSearch()
                    # Convert this list to a string with each item separated by a comma
                    key = ' '.join(searchList)
                    """If the lowercase version of the passed variable 'entry' is in the search related attributes, 
                    append the ID of that record to IDList"""
                    if entry.lower() in key.lower():
                        IDList.append(record)
            """Create an entry in the results dictionary with key of 'atype' and value of the list of matching record 
            IDs for that type"""
            self.__results[atype] = IDList
        return self.__results

    def getView(self, type, ID):
        """This function takes an entity type and an ID as its input and returns a string containing the attributes of
        the record matching ID that can identify it"""
        output = ""
        # If the type is UniformOrder get and return the list of view attributes as this will be handled separately
        if type == "UniformOrder":
            return self.__entities[type][ID].getView()
        # If the type is a User then return the ID (username) of that user
        elif type == "User":
            return ID
        else:
            """Get the list of attributes to identify the record of type 'type' matching ID and convert them to a string 
            with each value separated by a comma. Return this string with any excess spaces stripped."""
            for part in self.__entities[type][ID].getView():
                output += part + " "
            return output.strip(" ")


class Sorter(object):
    """This class facilitates the merge sort which can be used by the code to order a list of items alphabetically or
    numerically. This is, for example, used when displaying search results."""
    def __merge(self, x, y):
        """This function takes two ordered lists (x and y) as its inputs and returns an ordered list containing all the
        items from x and y."""
        output = []
        """While both lists don't have a length of zero, proceed to remove the lowest first item from one of the list 
        and append it to the output list"""
        while len(x) != 0 and len(y) != 0:
            if x[0] < y[0]:
                # If the first item in x is less than the first item in y, append the first item in x to output and remove it
                output.append(x[0])
                x.pop(0)
            else:
                # If the first item in y is less than the first item in x, append the first item in y to output and remove it
                output.append(y[0])
                y.pop(0)
        # Append the rest of the items in the non-empty list (either x and y) to output
        if len(x) != 0:
            output.extend(x)
        else:
            output.extend(y)
        return output

    def mergeSort(self, alist):
        """This function takes a list as its input returns a sorted list. It splits the input list in half and
        recursively calls instances of itself to mergeSort the new halves. It returns the two merged halves."""
        # If the length of the input list is 0 then return it straight away
        if len(alist) <= 1:
            return alist
        else:
            # Find the middle index of the list
            middle = len(alist)//2
            # Set x to the result of a recursive call when the items in 'alist' up to index 'middle' are passed
            x = self.mergeSort(alist[:middle])
            # Set y to the result of a recursive call when the items in 'alist' after index 'middle' are passed
            y = self.mergeSort(alist[middle:])
            # Return the result of a call to the merge function when x and y are passed
            return self.__merge(x, y)
