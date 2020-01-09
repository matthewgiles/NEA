class Person(object):
    """This is an object in my database to store any record that is a person type. This has child classes Student,
    Teacher and Assistant"""
    def __init__(self):
        """This constructor creates all of the private variables (attributes) of this object and sets their value to
        None"""
        self.__firstName = self.__lastName = self.__DoB = self.__email = self.__contactNumber = self.__postcode = \
            self.__houseNumber = self.__medical = None

    def update(self, data):
        """This function is for updating the attribute values of the object. It takes a list 'data' as its input and
        sets each private attribute of the object to the corresponding value in 'data'"""
        self.__firstName = data[0]
        self.__lastName = data[1]
        self.__DoB = data[2]
        self.__email = data[3]
        self.__contactNumber = data[4]
        self.__postcode = data[5]
        self.__houseNumber = data[6]
        self.__medical = data[7]

    def returnValues(self):
        """This function returns the values of the attributes of this person object as a list"""
        return [self.__firstName, self.__lastName, self.__DoB, self.__email, self.__contactNumber, self.__postcode,
                self.__houseNumber, self.__medical]

    def getSearch(self):
        """This function returns the values of the attributes of this person object that can be used to identify it
        when searching"""
        return [self.__firstName, self.__lastName, self.__email, self.__contactNumber]

    def returnNumber(self):
        """This function returns the contact number of the person"""
        return self.__contactNumber

    def getView(self):
        """This function returns the values of the attributes of this person object that can be used to identify it
        when it is displayed in a list"""
        return [self.__firstName, self.__lastName]

    def returnEmail(self):
        """This function returns the email address of the person"""
        return self.__email


class Student(Person):
    """This Student class is a child of a Person class. It has the same data values and is one child of person that can
    be handled in the system"""
    def __init__(self):
        Person.__init__(self)


class Assistant(Person):
    """This Assistant class is a child of a Person class. It has the same data values and is one child of person that
    can be handled in the system"""
    def __init__(self):
        Person.__init__(self)


class Teacher(Person):
    """This Teacher class is a child of a Person class. It has the same data values and is one child of person that can
    be handled in the system"""
    def __init__(self):
        Person.__init__(self)


class Venue(object):
    """This is an object in my database. The Venue is used to store data about a location in which events/classes can
    be held"""
    def __init__(self):
        self.__name = self.__postcode = self.__contactName = self.__email = self.__contactNumber = self.__hourlyCost \
            = self.__addressLine1 = self.__addressLine2 = None

    def getSearch(self):
        return [self.__name, self.__postcode, self.__contactNumber, self.__contactName]

    def getView(self):
        return [self.__name]

    def update(self, data):
        self.__name = data[0]
        self.__contactName = data[1]
        self.__contactNumber = data[2]
        self.__email = data[3]
        self.__addressLine1 = data[4]
        self.__addressLine2 = data[5]
        self.__postcode = data[6]
        self.__hourlyCost = data[7]

    def returnCost(self):
        """This function returns the value of the hourly hire cost for the venue"""
        return self.__hourlyCost

    def returnValues(self):
        return [self.__name, self.__contactName, self.__contactNumber, self.__email, self.__addressLine1,
                self.__addressLine2, self.__postcode, self.__hourlyCost]


class anEvent(object):
    """This is an object in my database to store any record that is of anEvent type. This has child classes Event and
    Class"""
    def __init__(self):
        self.__name = self.__cost = self.__sTime = self.__eTime = None

    def updateParent(self, data):
        """This function is to be used by a child for updating values in this parent class. It takes a list 'data' as
        its input and sets each private attribute of the object to the corresponding value in 'data'"""
        self.__name = data[0]
        self.__sTime = data[1]
        self.__eTime = data[2]
        self.__cost = data[3]
        self.__teacherWage = data[4]
        self.__assistantWage = data[5]

    def getSearch(self):
        return [self.__name]

    def getView(self):
        return [self.__name]

    def parentValues(self):
        """This function returns the values of the private attributes in this parent class as a list. It is called by
        a child."""
        return [self.__name, self.__sTime, self.__eTime, self.__cost, self.__teacherWage, self.__assistantWage]


class Event(anEvent):
    """This Event class is a child of anEvent class. This is used to store data about an Event that is being held."""
    def __init__(self):
        """This constructor initialises the parent class. It creates all the necessary attributes of this child class
        and sets their value to None."""
        anEvent.__init__(self)
        self.__sDate = self.__eDate = None

    def update(self, data):
        """This function is for updating the attribute values of the object. It takes a list 'data' as its input and
        sets each private attribute of this child object and its parent object to the corresponding value in 'data'"""
        # Setting the values of the parent class by calling updateParent and passing 'data'
        self.updateParent(data)
        # Updating the attributes of this child class
        self.__sDate = data[6]
        self.__eDate = data[7]

    def returnValues(self):
        """This function returns all the values of the attributes of this Event object and its parent as a list"""
        # Getting the private attribute values of the parent class
        values = self.parentValues()
        # Also appending the private attribute value of this child class (the start and end date of the event)
        values.extend([self.__sDate, self.__eDate])
        return values

    def returnStartDate(self):
        """This function returns the start date of the Event"""
        return self.__sDate


class Class(Event):
    def __init__(self):
        anEvent.__init__(self)
        self.__day = None

    def update(self, data):
        self.updateParent(data)
        self.__day = data[6]

    def returnDay(self):
        """This function returns the day of the week of the class"""
        return self.__day

    def returnValues(self):
        values = self.parentValues()
        # Also appending the private attribute value of this child class (the day of the week of the class)
        values.append(self.__day)
        return values


class UniformType(object):
    """This is an object in my database. The UniformType is used to store data about different uniform items that can be
    ordered"""
    def __init__(self):
        self.__name = self.__colours = self.__sizes = self.__cost = None

    def returnValues(self):
        return [self.__name, self.__colours, self.__sizes, self.__cost]

    def update(self, data):
        self.__name = data[0]
        self.__colours = data[1]
        self.__sizes = data[2]
        self.__cost = data[3]

    def getView(self):
        return [self.__name]

    def getSearch(self):
        return [self.__name]


class UniformOrder(object):
    """This is an object in my database. The UniformOrder is used to store data about an order for uniform that has been
    made"""
    def __init__(self):
        self.__studentID = self.__date = self.__totalCost = None

    def returnValues(self):
        return [self.__studentID, self.__date, self.__totalCost]

    def getView(self):
        return [self.__studentID, self.__date]

    def getSearch(self):
        return [self.__studentID]

    def update(self, data):
        self.__studentID = data[0]
        self.__date = data[1]
        self.__totalCost = data[2]


class UniformOrderLine(object):
    """This is an object in my database necessary to avoid many-to-many relationships. The UniformOrderLine links an
    order to a specific item (including its quantity and attribute choices). It contains foreign keys relating to a
    UniformType object (uniformID) and a UniformOrder object (orderID)"""
    def __init__(self):
        self.__orderID = self.__uniformID = self.__quantity = self.__size = self.__colour = self.__cost = None

    def returnValues(self):
        return [self.__orderID, self.__uniformID, self.__quantity, self.__size, self.__colour, self.__cost]

    def update(self, data):
        self.__orderID = data[0]
        self.__uniformID = data[1]
        self.__quantity = data[2]
        self.__size = data[3]
        self.__colour = data[4]
        self.__cost = data[5]

    def getOrderID(self):
        """This function returns the foreign key of orderID"""
        return self.__orderID


class Note(object):
    """This is an object in my database. The Note is used to store data for a note that has been written about a
    person (this could be a reminder, behavioural records etc."""
    def __init__(self):
        self.__title = self.__note = self.__dateCreated = self.__dateEdited = self.__recordID = None

    def update(self, data):
        self.__title = data[0]
        self.__note = data[1]
        self.__dateCreated = data[2]
        self.__dateEdited = data[3]
        self.__recordID = data[4]

    def returnValues(self):
        return [self.__title, self.__note, self.__dateCreated, self.__dateEdited]

    def getIDs(self):
        """This function returns the foreign IDs of the object. In this case it is recordID"""
        return self.__recordID


class AssistantEvent(object):
    """This is an object in my database necessary to avoid many-to-many relationships. The AssistantEvent shows the
    relationship of an assistant attending an event. It contains foreign keys relating to an Assistant object
    (assistantID) and an Event object (eventID)"""
    def __init__(self):
        self.__assistantID = None
        self.__eventID = None

    def update(self, parentID, ID):
        """This function updates the foreign IDs of the object. It takes two strings as input and stores them in
        the corresponding variable"""
        self.__eventID = parentID
        self.__assistantID = ID

    def getIDs(self):
        """This function returns the foreign IDs of the object. In this case it is assistantID and eventID"""
        return [self.__assistantID, self.__eventID]


class AssistantClass(object):
    """This is an object in my database necessary to avoid many-to-many relationships. The AssistantClass shows the
    relationship of an assistant attending a class. It contains foreign keys relating to an Assistant object
    (assistantID) and a Class object (classID)"""
    def __init__(self):
        self.__assistantID = None
        self.__classID = None

    def update(self, parentID, ID):
        self.__classID = parentID
        self.__assistantID = ID

    def getIDs(self):
        return [self.__assistantID, self.__classID]


# The following very similar relationship objects should be self explanatory based upon the comments above
class StudentEvent(object):
    def __init__(self):
        self.__studentID = None
        self.__eventID = None

    def update(self, parentID, ID):
        self.__eventID = parentID
        self.__studentID = ID

    def getIDs(self):
        return [self.__studentID, self.__eventID]


class StudentClass(object):
    def __init__(self):
        self.__studentID = None
        self.__classID = None

    def update(self, parentID, ID):
        self.__classID = parentID
        self.__studentID = ID

    def getIDs(self):
        return [self.__studentID, self.__classID]


class TeacherEvent(object):
    def __init__(self):
        self.__teacherID = None
        self.__eventID = None

    def update(self, parentID, ID):
        self.__eventID = parentID
        self.__teacherID = ID

    def getIDs(self):
        return [self.__teacherID, self.__eventID]


class TeacherClass(object):
    def __init__(self):
        self.__teacherID = None
        self.__classID = None

    def update(self, parentID, ID):
        self.__classID = parentID
        self.__teacherID = ID

    def getIDs(self):
        return [self.__teacherID, self.__classID]


class VenueClass(object):
    def __init__(self):
        self.__venueID = None
        self.__classID = None

    def update(self, parentID, ID):
        self.__classID = parentID
        self.__venueID = ID

    def getIDs(self):
        return [self.__venueID, self.__classID]


class VenueEvent(object):
    def __init__(self):
        self.__venueID = None
        self.__eventID = None

    def update(self, parentID, ID):
        self.__eventID = parentID
        self.__venueID = ID

    def getIDs(self):
        return [self.__venueID, self.__eventID]


class User(object):
    """This is an object in my database. The User is used to store data for a user of the software - this is a password,
    email and admin status. The username of this object is its primary ID (which is handled elsewhere)."""
    def __init__(self):
        """This constructor creates the private attributes of the object and sets their values to empty strings"""
        self.__password = self.__email = self.__admin = ""

    def update(self, data):
        self.__password = data[0]
        self.__email = data[1]
        self.__admin = data[2]

    def getPassword(self):
        """This function returns the password of the user (this is stored as a hashed value which is performed by the
        passwordManagement module"""
        return self.__password

    def getAccess(self):
        """This function returns the value of the admin status of the User"""
        return self.__admin

    def returnValues(self):
        return [self.__password, self.__email, self.__admin]
