import tkinter as tk
from tkinter import messagebox
import datetime
import entityHandler
import pdfProduction
import passwordManagememt
import emailSender
import validator
from decimal import Decimal


class StackEmptyException(Exception):
    # This exception is called when trying to pop from an empty stack
    def __init__(self, error):
        # This constructor for the exception takes an error message as its input
        self.__error = error

    def __str__(self):
        # This function returns a string representation of the exception in the form of the error message string
        return self.__error


class GUIController(tk.Tk):
    """This class is the main tkinter root and is responsible for managing all of the other tkinter widgets and windows"""
    def __init__(self, *args, **kwargs):
        """This constructor takes any number of arguments as input (as it typical with a tkinter root class). It also
        creates any required attributes and sets up the tkinter root to handle all of my windows."""
        tk.Tk.__init__(self, *args, **kwargs)
        # Creating a canvas as this is necessary for a scrollbar
        self.__canvas = tk.Canvas(self)
        # Putting a frame inside the canvas
        self.__frame = tk.Frame(self.__canvas)
        # Creating a vertical scrollbar
        vsb = tk.Scrollbar(self, orient="vertical", command=self.__canvas.yview)
        self.__canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        # Packing the canvas into the root window
        self.__canvas.pack(side="left", fill="both", expand=True)
        # Putting the toolbar in the canvas
        self.__toolbar = Toolbar(self.__canvas, self)
        # Ensuring the toolbar is at the top of the canvas and the frame is below
        self.__canvas.create_window((0, 0), window=self.__toolbar, anchor="n")
        self.__canvas.create_window((0, 30), window=self.__frame, anchor="n")
        # Creating a Stack object instance in which frames can be stored
        self.__frameStack = Stack()
        # Each time the frame is configured , there is a call to the onFrameConfigure function
        self.__frame.bind('<Configure>', self.__onFrameConfigure)
        # When the red button (to close the window) is pressed, the function closingSave is called
        self.protocol("WM_DELETE_WINDOW", self.__closingSave)
        self.__user = None
        self.__handler = entityHandler.EntityHandler()
        # Creating a dictionary called self.__frames containing all the possible tkinter window objects (the pages)
        self.__frames = {"Teacher": TeacherForm(self.__frame, self), "Note": NoteForm(self.__frame, self),
                       "Assistant": AssistantForm(self.__frame, self), "NewRecord": NewRecordPage(self.__frame, self), "UserAccountList": UserAccountList(self.__frame, self),
                       "Student": StudentForm(self.__frame, self), "Class": ClassForm(self.__frame, self),
                       "Event": EventForm(self.__frame, self), "Venue": VenueForm(self.__frame, self), "EmailSender": EmailSender(self.__frame, self, self.__handler),
                       "FinanceCalculator": FinanceCalculator(self.__frame, self), "UniformTypeForm": UniformTypeForm(self.__frame, self), "UniformPage": UniformPage(self.__frame, self),
                       "UniformOrderForm": UniformOrderForm(self.__frame, self), "UniformOrderList": UniformOrderList(self.__frame, self),
                       "Home": Home(self.__frame, self), "UserForm": UserForm(self.__frame, self), "AccountsPage": AccountsPage(self.__frame, self)}
        self.__accessLevel = None
        # Creating an instance of the Login window object which determines whether the software can be accessed
        Login(self)
        self.__currentframe = self.__frames["Home"]
        self.showPage("Home")

    def setAccessLevel(self, level):
        self.__accessLevel = level

    def setUser(self, user):
        self.__user = user

    def getUser(self):
        return self.__user

    def fail(self):
        """When this function is called it goes on to call the private __closingSave function which then terminates the
        software"""
        self.__closingSave()

    def __closingSave(self):
        """This function destroys the tkinter instance (closes the GUI) and makes a call to the entityHandler to save the
        database to a file."""
        self.destroy()
        self.__handler.saveFile()

    def showPage(self, page):
        """This public function takes a text string 'page' as its input and makes a call to the private setPage function
        (to which is passes the value in the self.__frames dictionary with key 'page') which changes the tkinter window"""
        self.__setPage(self.__frames[page])

    def checkAdmin(self):
        """This function checks if the current user is an admin by calling isAdmin and if they are, returns True, and if
        not produces a message box to inform the user and returns False."""
        if self.isAdmin():
            return True
        else:
            tk.messagebox.showinfo("Admin Error", "This is not an administrator account. You are not permitted to do that")
            return False

    def isAdmin(self):
        """This function checks if the current user is an admin by comparing the access level to 1. If it is a one (they
        are an admin) True is returned, otherwise False is returned."""
        if self.__accessLevel == 1:
            return True
        else:
            return False

    def recordSearch(self):
        """"This function opens a search window and displays the record in its view state that is the result of the search"""
        # Creating an instance of a SearchWidget
        searcher = SearchWidget(self)
        # Storing the result of a search in single selection mode in the variable output
        output = searcher.setMode(tk.SINGLE, 0)
        for i in output:
            self.showPage(i)
            self.viewCurrentPage(output[i][0])

    def __setPage(self, frame):
        """This function takes a tkinter object as an input and displays it"""
        # If the frame currently being shown contains a NoteList - remove it
        if hasattr(self.__currentframe, "getNoteList"):
            if self.__currentframe.getNoteList() is not None:
                self.__currentframe.removeNoteList()
        # Remove the tkinter object currently being shown
        self.__currentframe.grid_remove()
        # Display the tkinter frame that was passed to the function and push it onto the frameStack
        frame.grid(row=0, column=0)
        self.__frameStack.push(frame)
        self.__currentframe = frame
        # Update the title along the top of the window
        tk.Tk.wm_title(self, frame.windowTitle())

    def back(self):
        """This function displays the tkinter window that was being viewed previously"""
        try:
            # Remove the current frame from the stack
            self.__frameStack.pop()
            # Pop from the stack and this will be the frame that was viewed previously
            next = self.__frameStack.pop()
            self.__setPage(next)
        except StackEmptyException as e:
            # If the stack is empty display an error to say that you cannot go back any further
            tk.messagebox.showinfo("Error", "You cannot go back " + str(e))

    def showPrevious(self):
        self.back()

    def getCurrentPage(self):
        return self.__currentframe

    def editCurrentPage(self, recordID):
        """This function takes a recordID as its input and displays that record's values in the current form (with the
        form in edit mode)"""
        self.__currentframe.editForm(recordID)

    def viewCurrentPage(self, recordID):
        """This function takes a recordID as its input and displays that record's values in the current form (with the
        form in view mode)"""
        self.__currentframe.viewForm(recordID)

    def createCurrentPage(self):
        """This function makes the current form in its create mode"""
        self.__currentframe.createForm()

    def createNotePage(self, ID):
        """This function takes an ID of a record and puts the NoteForm into a create state with a note being made for
        the record matching ID"""
        self.__currentframe.createForm(ID)

    def getEntityHandler(self):
        return self.__handler

    def __onFrameConfigure(self, event):
        """This function takes the event of the frame being configures as its input and resizes the canvas to fit it exactly"""
        self.__canvas.configure(scrollregion=self.__canvas.bbox('all'))
        h = event.height
        # If the toolbar is wider than the frame then make the canvas as wide as the toolbar (or vice versa)
        if event.width > self.__toolbar.winfo_width():
            w = event.width
        else:
            w = self.__toolbar.winfo_width()
        # Make the canvas taller than the frame to account for the toolbar
        self.__canvas.config(width=w, height=h+29)


class Stack(object):
    """This class is for the implementation of a stack (without a size as this is most desireable for its intended purpose)"""
    def __init__(self):
        """This constructor sets a TopOfStackPointer to 0 (the next empty index) and creates an empty list to represent
        the stack"""
        self.__TopOfStackPointer = 0
        self.__stackList = []

    def push(self, item):
        """This function takes an item as its input and appends it to the stack along with incrementing the TopOfStack pointer"""
        self.__stackList.append(item)
        self.__TopOfStackPointer += 1

    def pop(self):
        """This function returns the item in the stack that was most recently added"""
        if len(self.__stackList) > 0:
            self.__TopOfStackPointer -= 1
            # Return and remove the value of the item at the index of (the now decremented) TopOfStackPointer
            item = self.__stackList.pop(self.__TopOfStackPointer)
            return item
        else:
            # If the stack is empty then raise a relevant exception
            raise StackEmptyException("--> Stack is empty")


class Toolbar(tk.Frame):
    """This tkinter object is a toolbar for navigation that goes along the top of the software"""
    def __init__(self, container, master):
        """This constructor takes a container for the Toolbar and its master controller as input and then produces all
        of the GUI elements of the toolbar"""
        tk.Frame.__init__(self, container)
        self.config(bg="grey")
        self.__master = master
        # The following is the creation of all the buttons in the toolbar
        back = tk.Button(self, text="Back <--", highlightbackground="grey", command=master.back)
        back.grid(row=0, column=0, padx=3)
        new = tk.Button(self, text="New Record", highlightbackground="grey", command=lambda: master.showPage("NewRecord"))
        new.grid(row=0, column=1, padx=3)
        """Lambda is used where the button is required to call multiple functions and/or needs to pass varaibles to the 
        functions it calls"""
        email = tk.Button(self, text="E-Mail", highlightbackground="grey",
                            command=lambda: [master.showPage("EmailSender"), master.getCurrentPage().reset()])
        email.grid(row=0, column=2, padx=3)
        search = tk.Button(self, text="Searcn", highlightbackground="grey", command=master.recordSearch)
        search.grid(row=0, column=3, padx=3)
        finance = tk.Button(self, text="Finance", highlightbackground="grey", command=self.__finance)
        finance.grid(row=0, column=4, padx=3)
        uniform = tk.Button(self, text="Uniform", highlightbackground="grey", command=lambda: master.showPage("UniformPage"))
        uniform.grid(row=0, column=5, padx=3)
        accounts = tk.Button(self, text="Accounts", highlightbackground="grey", command=self.__accounts)
        accounts.grid(row=0, column=6, padx=3)

    def __finance(self):
        """This function displays the finance calculator page and rests it to default if the user is an admin"""
        if self.__master.checkAdmin():
            self.__master.showPage("FinanceCalculator")
            self.__master.getCurrentPage().reset()

    def __accounts(self):
        """This function displays the accounts page if the user is an admin"""
        if self.__master.checkAdmin():
            self.__master.showPage("AccountsPage")


class Form(tk.Frame):
    """This class provides a tkinter window in the style of a form for data entry. This is the parent class of many
    other styles of Form."""
    def __init__(self, container, master):
        """This constructor takes a container for the widget and its master controller as input and then creates all of
        the GUI elements and necessary attributes for a Form."""
        tk.Frame.__init__(self, container)
        # Creating a dynamic tkinter variable in which can be changed to set the main title at the top of the Form
        self.titleText = tk.StringVar()
        # Setting the primary key for the record the Form is showing to None
        self.__ID = None
        """Getting the type of the object less the string "Form" (this will be different for child classes) - this is 
        the type of entity the form is collecting data for"""
        self.__type = self.__class__.__name__[:-4]
        self.entityHandler = master.getEntityHandler()
        title = tk.Label(self, font=('Arial', 24, 'bold'), textvariable=self.titleText)
        title.grid(row=0, padx=10, pady=(10, 0), columnspan=2)
        self.__saveButton = tk.Button(self, text="Save", command=self.validate)
        self.__deleteButton = tk.Button(self, text="Delete", command=self.__confirm)
        self.__editButton = tk.Button(self, text="Edit", command=lambda: master.editCurrentPage(self.__ID))
        self.__values = []
        self.__entries = []
        self.errors = []
        self.__master = master
        # By default noteList is None as some Forms do not have one
        self.__noteList = None

    def __confirm(self):
        """This function is called by the delete button and ensures that the user intends to delete the current record
        before proceeding to do so"""
        if messagebox.askyesno("Warning", "Are you sure you want to delete this record?") is True:
            # If the user has selected 'Yes' from a confirm dialogue box then delete the record
            self.entityHandler.deleteRecord(self.__type, self.__ID)
            # If the record was of type Note then return to the page the Note was about, otherwise go to NewRecord page
            if self.__type == "Note":
                self.__master.showPrevious()
            else:
                self.__master.showPage("NewRecord")

    def updateObject(self, data):
        """This function takes a list of data and its input and then uses the entityHanlder to update the record in
        the database that the current form is showing"""
        return self.entityHandler.updateRecord(self.getType(), self.getID(), data)

    def setNoteList(self, noteList):
        """This function receives a noteList object as its input and sets the private attribute to that"""
        self.__noteList = noteList

    def removeNoteList(self):
        """This function removes any noteList from the form"""
        self.__noteList.grid_remove()

    def getNoteList(self):
        return self.__noteList

    def getType(self):
        return self.__type

    def uniqueSetter(self, existing, view):
        """This function is used if a child class of a Form requires some special behaviour when setting the state of
        a Form and the data within it. It takes variable existing, which contains a list of data to include in the Form,
        and a boolean variable view which determines whether or not the Form should be in the view state."""
        pass

    def setState(self, existing, view):
        """This function is used to set the state of a form and put data into it.  It takes variable existing, which
        contains a list of data to include in the Form, and a boolean variable view which determines whether or not the
        Form should be in the view state."""
        for i in self.errors:
            i.set("")
        count = 0
        # Call the uniqueSetter function and pass the same variables this function received as a child class may have special behaviour
        self.uniqueSetter(existing, view)
        for i in self.__entries:
            # Itertating through all of the entry fields in the form
            if isinstance(i, Date) or isinstance(i, Time) or isinstance(i, Day) or isinstance(i, EntityPicker):
                # If the entry field is one of the above types then it is treated differently
                if existing is None:
                    # If the there is no data to put into the form then set entry field i to its default values and state to normal
                    i.default()
                    i.setState("normal")
                else:
                    if isinstance(i, EntityPicker):
                        # If the entry field is an entity picker then pass it the ID of the record being displayed by the form
                        i.setValue(self.getID())
                        count -= 1
                    else:
                        # Set the value of entry field i to the item in existing at index count
                        i.setValue(existing[count])
                    # If the form should be in view state then set entry field i to disabled, otherwise to normal
                    if view:
                        i.setState("disabled")
                    else:
                        i.setState("normal")
            else:
                i.config(state="normal")
                """The following ensures that the entry fields are cleared but the code for doing this for different
                types of text entry fields is different. The try except clause catches errors when doing this"""
                try:
                    i.delete(0, tk.END)
                except tk.TclError:
                    i.delete("0.0", tk.END)
                if existing is not None:
                    """If there is data to insert into the form, insert the item in existing and index count into entry 
                    field i"""
                    i.insert(tk.END, existing[count])
                    if view:
                        i.config(state="disabled")
            count += 1
        # The following ensures that the current buttons do or don't appear in the form depending on whether or not it is in view state
        if view:
            self.__saveButton.grid_remove()
            self.__editButton.grid(row=200, column=0)
            self.__deleteButton.grid(row=200, column=1)
        else:
            self.__editButton.grid_remove()
            self.__deleteButton.grid_remove()
            self.__saveButton.grid(row=200, columnspan=2)

    def editForm(self, ID):
        """The following function takes a record ID as its input and causes the form to display the corresponding record
        in ithe edit state"""
        self.__ID = ID
        # Get the values of record matching ID and of the type of the current form
        values = self.entityHandler.getData(self.getType(), self.__ID)
        self.setState(values, False)

    def viewForm(self, ID):
        """The following function takes a record ID as its input and causes the form to display the corresponding record
        in its view state"""
        self.__ID = ID
        values = self.entityHandler.getData(self.getType(), self.__ID)
        # Pass in true as the form should be in view state
        self.setState(values, True)

    def getEntries(self):
        """This function iterates through all of the entry fields in the form and returns their values in a list"""
        self.__values = []
        for i in self.__entries:
            if isinstance(i, Date) or isinstance(i, Time) or isinstance(i, Day):
                # If the entry field is one of the above custom classes, call the function to get its value
                self.__values.append(i.getValue())
            elif isinstance(i, EntityPicker):
                pass
            else:
                self.__values.append(i.get())
        return self.__values

    def createForm(self):
        """This function allows a new record to be created in the form. It sets the ID to None and the setState function
        is passed no exisiting data and the view state is False."""
        self.setID(None)
        self.setState(None, False)

    def getID(self):
        return self.__ID

    def setID(self, ID):
        self.__ID = ID

    def validate(self):
        """This is a function for validation that all Forms have but will be unique to each child"""
        pass

    def appendEntries(self, field):
        """The following takes a tkinter string variable and appends it as a new field in self.__entries"""
        self.__entries.append(field)

    def getEntryFields(self):
        return self.__entries

    def windowTitle(self):
        return "Form"


class PersonForm(Form):
    """This object is a child of the Form class and is the parent of any forms which require data to be stored about a
    real-life person"""
    def __init__(self, container, master):
        """This constructor takes the container of the window as its input along with the master controller. It also
        creates any GUI elements for the PersonForm and attributes required."""
        Form.__init__(self, container, master)
        labels = ["First Name", "Last Name", "DoB", "E-Mail", "Contact Number", "Postcode", "House Number",
                  "Medical Details"]
        _row = 100
        count = 0
        # This form will have a NoteList as notes can be stored about a person
        self.setNoteList(NoteList(container, master, self))
        # The following is for the GUI creation of the entry fields and their labels
        for i in labels:
            label = tk.Label(self, text=i)
            label.grid(row=_row, column=0, padx=10, pady=10)
            # Above each entry field is an error label; here an error message can appear to display invalid data
            self.errors.append(tk.StringVar())
            self.errors[count].set("")
            error = tk.Label(self, textvariable=self.errors[count], fg="red")
            error.grid(row=_row-1, column=1, padx=1, pady=0)
            # On this row the entry field should be a date picker as opposed to a text entry field
            if _row == 104:
                date = Date(self, 70, 0)
                date.grid(row=_row, column=1, padx=1, pady=10)
                self.appendEntries(date)
            else:
                entry = tk.Entry(self)
                entry.config(state="normal", disabledforeground="black")
                entry.grid(row=_row, column=1, padx=10, pady=10)
                self.appendEntries(entry)
            _row += 2
            count += 1

    def uniqueSetter(self, existing, view):
        """This function takes variables existing and view and, if view is True, displays the NoteList widget"""
        if view:
            self.getNoteList().setList(self.getID())
            self.getNoteList().grid(row=500, columnspan=2, pady=20)

    def updateObject(self, data):
        """This function takes a list of data as its input and updates the record the form is displaying with this data
        by calling the entityHandler. If there was a NoteList displayed, this is now removed."""
        if self.getNoteList() is not None:
            self.removeNoteList()
        return self.entityHandler.updateRecord(self.getType(), self.getID(), data)

    def __validateHouseNumber(self, string):
        """This function takes a string as its input and returns a string 'message' which determines whether or not the input
        is a valid house number"""
        message = ""
        # Ensuring the number is no longer than 5 digits
        if len(string) > 5:
            message = "House number too long"
        # Ensuring the number contains only numerical characters or is blank
        if not string.isdigit() and string != "":
            message = "This is not a number"
        return message

    def __validateMedicalDetails(self, string):
        """This function takes a string as its input and returns a string 'message' which determines whether or not the input
        is valid medical details"""
        message = ""
        # Ensuring the input is not longer than 250 characters
        if len(string) > 250:
            message = "Description too long"
        return message

    def validate(self):
        """This function validates the data that has been entered into the entry fields. If it is valid then the record
        is updates, otherwise error messages appear."""
        data = self.getEntries()
        # Creating as many blank error messages as there are data fields
        errors = [""] * len(data)
        # Setting the value of each message in errors to the result of the corresponding validation function (if required)
        errors[0] = validator.validateName(data[0])
        errors[1] = validator.validateName(data[1])
        errors[2] = ""
        errors[3] = validator.validateEmail(data[3])
        errors[4] = validator.validateContactNumber(data[4])
        errors[5] = validator.validatePostcode(data[5])
        errors[6] = self.__validateHouseNumber(data[6])
        errors[7] = self.__validateMedicalDetails(data[7])
        validated = True
        # Checking if any messages in errors are not an empty string (i.e. an error has been found)
        for i in errors:
            if i is not "":
                validated = False
        # If no errors then update the object and put the form in view state
        if validated:
            self.setID(self.updateObject(data))
            self.viewForm(self.getID())
       # If there are errors then display the error messages in the corresponding error field (created in the constructor)
        else:
            count = 0
            for i in errors:
                self.errors[count].set(i)
                count += 1


class Time(tk.Frame):
    """This tkinter widget allows for a time to be picked from a 24 hour format"""
    def __init__(self, container):
        """This constructor takes the container of the widget as input. It also creates all of the GUI elements and
        required attributes"""
        tk.Frame.__init__(self, container)
        self.__hours = tk.StringVar(self)
        self.__minutes = tk.StringVar(self)
        self.__hours.set('12')
        self.__minutes.set('00')
        hours = []
        minutes = []
        # Adding minutes and hours to the list of options - adding a leading 0 where the time is one digit
        for i in range(0, 24):
            if i < 10:
                i = "0" + str(i)
            hours.append(str(i))
        for i in range(0, 60):
            if i < 10:
                i = "0" + str(i)
            minutes.append(str(i))
        """Creating option menus (dropdown menus) with option to select from define by the hours and minutes lists, these 
        menus have their value determined by the tkinter string variables above"""
        self.__theHours = tk.OptionMenu(self, self.__hours, *hours)
        self.__theHours.grid(row=0, column=0)
        colon = tk.Label(self, text=":")
        colon.grid(row=0, column=1)
        self.__theMinutes = tk.OptionMenu(self, self.__minutes, *minutes)
        self.__theMinutes.grid(row=0, column=2)

    def setValue(self, time):
        """This function receives a time string as its input and sets the corresponding tkinter variables to these values"""
        self.__hours.set(time[:2])
        self.__minutes.set(time[-2:])

    def default(self):
        """This function sets the time to its defaul (noon)"""
        self.__hours.set("12")
        self.__minutes.set("00")

    def setState(self, _state):
        """This function takes a variable _state as its input and sets the state of the option menus to this (it could be
        normal or disabled)"""
        self.__theHours.config(state=_state)
        self.__theMinutes.config(state=_state)

    def getValue(self):
        """This function returns the value of the user inputted time (the values of the option menus)"""
        return str(self.__hours.get()) + str(self.__minutes.get())


class Day(tk.Frame):
    """This tkinter widget allows for a day of the week to be picked from an option menu. It is very similar to the
    above time object so no further commenting is required"""
    def __init__(self, container):
        tk.Frame.__init__(self, container)
        self.__day = tk.StringVar(self)
        self.__day.set('Monday')
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.__theDay = tk.OptionMenu(self, self.__day, *days)
        self.__theDay.grid(row=0, column=0)

    def setValue(self, value):
        self.__day.set(value)

    def default(self):
        self.__day.set("Monday")

    def setState(self, _state):
        self.__theDay.config(state=_state)

    def getValue(self):
        return str(self.__day.get())


class Date(tk.Frame):
    """This tkinter widget allows a date (day, month, year) to be picked. It is very similar to the above time object so
    little further commenting is required."""
    def __init__(self, container, before, after):
        """This constructor also receives before and after variables to determine the numbers of years before and after
        the current that the widget should show"""
        tk.Frame.__init__(self, container)
        self.__theDay = tk.StringVar(self)
        self.__theMonth = tk.StringVar(self)
        self.__theYear = tk.StringVar(self)
        days = []
        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        years = []
        # Below the current year is found using the datetime module
        for i in range(int(datetime.date.today().year)-before, int(datetime.date.today().year)+after+1):
            years.append(str(i))
        for i in range(1, 32):
            day = str(i)
            if len(day) == 1:
                day = ("0" + day)
            days.append(day)
        self.__day = tk.OptionMenu(self, self.__theDay, *days)
        self.__day.grid(row=0, column=0)
        self.__month = tk.OptionMenu(self, self.__theMonth, *months)
        self.__month.grid(row=0, column=1)
        self.__year = tk.OptionMenu(self, self.__theYear, *years)
        self.__year.grid(row=0, column=2)
        self.default()

    def setValue(self, date):
        """This function takes a datetime object as input and converts it to string values which are used to set the
        values in the dropdown menus"""
        self.__theYear.set(date.strftime("%Y"))
        self.__theMonth.set(date.strftime("%m"))
        self.__theDay.set(date.strftime("%d"))

    def default(self):
        """This function sets the option menus to their default values of the current date"""
        self.__theYear.set(str(datetime.date.today().year))
        self.__theMonth.set(str(datetime.date.today().month))
        self.__theDay.set(str(datetime.date.today().day))

    def setState(self, _state):
        self.__day.config(state=_state)
        self.__month.config(state=_state)
        self.__year.config(state=_state)

    def getValue(self):
        """This function returns the values in the option menus as a datetime object"""
        return datetime.datetime.strptime(self.__theDay.get()+self.__theMonth.get()+self.__theYear.get(), "%d%m%Y").date()


class TeacherForm(PersonForm):
    """This TeacherForm tkinter object is a child class of PersonForm. It is used to collect data for a Teacher type
    record in the database."""
    def __init__(self, container, master):
        """This constructor takes the container of the form and the master controller as input. It also sets the value of
        the forms title."""
        PersonForm.__init__(self, container, master)
        self.titleText.set("Teacher")

    def windowTitle(self):
        """This function sets the title of the window"""
        return "Teacher"


class AssistantForm(PersonForm):
    """This AssistantForm tkinter object is a child class of PersonForm. It is used to collect data for a Assistant type
    record in the database. Please see the TeacherForm for further comments."""
    def __init__(self, container, master):
        PersonForm.__init__(self, container, master)
        self.titleText.set("Assistant")

    def windowTitle(self):
        return "Assistant"


class StudentForm(PersonForm):
    """This StudentForm tkinter object is a child class of PersonForm. It is used to collect data for a Student type
    record in the database. Please see the TeacherForm for further comments."""
    def __init__(self, container, master):
        PersonForm.__init__(self, container, master)
        self.titleText.set("Student")

    def windowTitle(self):
        return "Student"


class NoteForm(Form):
    """The NoteForm is a tkinter object and child class of the Form object. It is used to collect data for a record of
    type Note.

    Some commenting for this form would be the same as for a PersonForm so please see above."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as input. It also creates all of
        the GUI elements and necessary attributes. Most of the functionality of this constructor can be seen commented for
        a PersonForm."""
        Form.__init__(self, container, master)
        _row = 0
        self.__master = master
        # The following is the generation of GUI elements
        title = tk.Label(self, text="Title")
        title.grid(row=101, padx=10, columnspan=2)
        titleEntry = tk.Entry(self)
        titleEntry.config(state="normal", disabledforeground="black")
        titleEntry.grid(row=103, padx=10, columnspan=2, pady=(0,10))
        self.appendEntries(titleEntry)
        note = tk.Label(self, text="Note")
        note.grid(row=104, padx=10, columnspan=2)
        # Creating a larger entry box with a border style of ridge
        noteEntry = tk.Text(self, height=10, width=50, borderwidth=3, relief="ridge", highlightcolor="white")
        noteEntry.grid(row=106, padx=10, columnspan=2)
        self.__dateCreated = tk.StringVar()
        self.__dateEdited = tk.StringVar()
        dateCLabel = tk.Label(self, textvariable=self.__dateCreated, fg="#737982")
        dateCLabel.grid(row=107, column=0)
        dateELabel = tk.Label(self, textvariable=self.__dateEdited, fg="#737982")
        dateELabel.grid(row=107, column=1)
        self.errors.append(tk.StringVar())
        self.errors[0].set("")
        self.errors.append(tk.StringVar())
        self.errors[1].set("")
        titleError = tk.Label(self, textvariable=self.errors[0], fg="red")
        titleError.grid(row=102, columnspan=2, padx=1)
        noteError = tk.Label(self, textvariable=self.errors[1], fg="red")
        noteError.grid(row=105, columnspan=2, padx=1)
        self.__back = tk.Button(self, text="<-", command=lambda: self.__master.showPrevious())
        self.titleText.set("Note")
        self.appendEntries(noteEntry)
        self.setNoteList(None)
        # Creating the recordID. This is the ID of the record the notes are being stored about.
        self.__recordID = 0

    def windowTitle(self):
        return "Note"

    def updateObject(self, data):
        """This function takes a list of data as its input and updates the note that the form is showing with it."""
        # If this is a new note then set the date created to the current date, otherwise use the old value
        if self.getID() is None:
            data.append(datetime.datetime.now())
        else:
            data.append(self.entityHandler.getData(self.getType(), self.getID())[2])
        # Set the date edited to the current date
        data.append(datetime.datetime.now())
        # Append the ID of the record the note is about (this becomes a foreign key)
        data.append(self.__recordID)
        return self.entityHandler.updateRecord(self.getType(), self.getID(), data)

    def createForm(self, ID):
        """This function takes the ID of the record the note is to be about as input and sets the NoteForm to create state."""
        self.__recordID = ID
        self.__dateCreated.set("")
        self.__dateEdited.set("")
        self.setID(None)
        self.setState(None, False)

    def editForm(self, ID):
        self.__ID = ID
        values = self.entityHandler.getData(self.getType(), self.__ID)
        self.__recordID = self.entityHandler.getNoteRecordID(ID)
        self.setState(values, False)

    def uniqueSetter(self, existing, view):
        """This function takes the same input as the setState parent function. If there is already a note, it setd the date
        created and edited to the values provided. If the NoteForm is to be in view state then the back button is shown."""
        if existing is not None:
            self.__dateCreated.set("Date Created: \n" + existing[2].strftime("%d") + "/" + existing[2].strftime("%m") + "/" + existing[2].strftime("%Y"))
            self.__dateEdited.set("Date Edited: \n" + existing[3].strftime("%d") + "/" + existing[3].strftime("%m") + "/" + existing[3].strftime("%Y"))
            if view:
                self.__back.grid(row=201, column=0, columnspan=2)
            else:
                self.__back.grid_remove()

    def validate(self):
        data = self.getEntries()
        errors = [""] * 2
        errors[0] = validator.presenceCheck(data[0])
        errors[1] = validator.presenceCheck(data[1])
        validated = True
        for i in errors:
            if i is "":
                pass
            else:
                validated = False
        if validated:
            self.setID(self.updateObject(data))
            self.__master.showPrevious()

        else:
            count = 0
            for i in errors:
                self.errors[count].set(i)
                count += 1

    def getEntries(self):
        """This function returns the values within the entry fields of the form"""
        self.__values = []
        entries = self.getEntryFields()
        return [entries[0].get(), entries[1].get("1.0", tk.END).strip("\n")]


class anEventForm(Form):
    """The anEventForm object is a child class of the Form tkinter object. It is used to collect date for a record that
    might be a Class or Event (the child classes of this object).

    Some commenting for this form would be the same as for a PersonForm so please see above."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as input. It also creates all of
                the GUI elements and necessary attributes."""
        Form.__init__(self, container, master)
        # The following is the creation of the GUI elements
        labels = ["Name", "Venue", "Start Time", "End Time", "Cost (£)", "Teacher Wage (£)", "Assistant Wage (£)",
                  "Teacher(s)", "Assistant(s)", "Students"]
        _row = 102
        count = 0
        for i in labels:
            label = tk.Label(self, text=i)
            label.grid(row=_row, column=0, padx=10, pady=10)
            _row += 2
            count += 1

        self.errors.append(tk.StringVar())
        self.errors[0].set("")
        nameError = tk.Label(self, textvariable=self.errors[0], fg="red")
        nameError.grid(row=101, column=1, padx=1, pady=0)
        nameEntry = tk.Entry(self)
        nameEntry.config(state="normal", disabledforeground="black")
        nameEntry.grid(row=102, column=1, padx=10, pady=10)
        self.appendEntries(nameEntry)

        _row = 110
        for cost in range(0,3):
            costEntry = tk.Entry(self)
            costEntry.config(state="normal", disabledforeground="black")
            costEntry.grid(row=_row, column=1, padx=10, pady=10)
            self.appendEntries(costEntry)
            var = tk.StringVar()
            var.set("")
            self.errors.append(var)
            error = tk.Label(self, textvariable=self.errors[1], fg="red")
            error.grid(row=_row-1, column=1, padx=1, pady=0)
            _row += 2

        _row = 116
        for item in ["Teacher", "Assistant", "Student"]:
            picker = EntityPicker(self, master, str(item+self.getType()), self.getType(), tk.MULTIPLE)
            picker.grid(row=_row, column=1, padx=10, pady=10)
            self.appendEntries(picker)
            _row += 2
        venuePicker = EntityPicker(self, master, "Venue" + self.getType(), self.getType(), tk.SINGLE)
        venuePicker.grid(row=104, column=1, padx=10, pady=10)
        self.appendEntries(venuePicker)

        startTime = Time(self)
        startTime.grid(row=106, column=1, padx=10, pady=10)
        self.appendEntries(startTime)
        endTime = Time(self)
        endTime.grid(row=108, column=1, padx=10, pady=10)
        self.appendEntries(endTime)
        self.__registerButton = tk.Button(self, text="Register", command=self.register)

    def validate(self):
        """Please see the PersonForm for an explanation of this function"""
        data = self.getEntries()
        errors = [""] * 4
        errors[0] = validator.validateName(data[0])
        errors[1] = validator.validateCost(data[1])
        errors[2] = validator.validateCost(data[2])
        errors[3] = validator.validateCost(data[3])
        validated = True
        for i in errors:
            if i is "":
                pass
            else:
                validated = False
        if validated:
            self.setID(self.updateObject(data))
            self.viewForm(self.getID())
        else:
            count = 0
            for i in errors:
                self.errors[count].set(i)
                count += 1

    def register(self):
        """This function is required by all child classes but is unique to each of them. It facilitates the generation of
        a register for the event/class"""
        pass

    def uniqueSetter(self, existing, view):
        """This function takes a list of existing data and a boolean view variable. If existing is None and view is
        False, the register button is removed; otherwise it is shown."""
        if existing is None or view is False:
            self.__registerButton.grid_remove()
        else:
            self.__registerButton.grid(row=500, columnspan=2)


class ClassForm(anEventForm):
    """This object is a tkinter widget and child class of anEventForm. It is used to collect data for a Class record.

    Any similarities with PersonForm have not been re-commented."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as input. It also creates all of
        the GUI elements and necessary attributes that are not shared with the parent class."""
        anEventForm.__init__(self, container, master)
        self.__master = master
        # Creating a field for the day of the week of the class
        day = tk.Label(self, text="Day")
        day.grid(row=150, column=0, padx=10, pady=10)
        self.__dayEntry = Day(self)
        self.__dayEntry.grid(row=150, column=1, padx=10, pady=10)
        self.appendEntries(self.__dayEntry)
        self.titleText.set("Class")

    def windowTitle(self):
        return "Class"

    def register(self):
        """This function creates an instance of a ClassRegisterSender and passes it the master controller, entityHandler,
        the day of the week of the class, ID of the class and name of the class. This allows a register to be generated
        for the class currently being displayed."""
        ClassRegisterSender(self.__master, self.__master.getEntityHandler(), self.__dayEntry.getValue(), self.getID(),
                                   self.getEntries()[0])


class EventForm(anEventForm):
    """This object is a tkinter widget and child class of anEventForm. It is used to collect data for an Event record.

    Any similarities with PersonForm have not been re-commented."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as input. It also creates all of
        the GUI elements and necessary attributes that are not shared with the parent class."""
        anEventForm.__init__(self, container, master)
        self.__master = master
        # Creating fields for the start and end date of the event
        startDate = tk.Label(self, text="Start Date")
        startDate.grid(row=150, column=0, padx=10, pady=10)
        self.__startEntry = Date(self, 2, 5)
        self.__startEntry.grid(row=150, column=1, padx=1, pady=10)
        self.appendEntries(self.__startEntry)
        endDate = tk.Label(self, text="End Date")
        endDate.grid(row=151, column=0, padx=10, pady=10)
        self.__endEntry = Date(self, 2, 5)
        self.__endEntry.grid(row=151, column=1, padx=1, pady=10)
        self.appendEntries(self.__endEntry)
        self.titleText.set("Event")

    def windowTitle(self):
        return "Event"

    def register(self):
        """This function creates an instance of an EventRegisterSender and passes it the master controller, entityHandler,
        start and end date of the event, ID of the event and name of the event. This allows a register to be generated
        for the event currently being displayed."""
        EventRegisterSender(self.__master, self.__master.getEntityHandler(),
                                   self.__startEntry.getValue(), self.__endEntry.getValue(), self.getID(), self.getEntries()[0])


class NewRecordPage(tk.Frame):
    """The NewRecordPage is a tkinter frame for navigating to different types of form and putting them in create mode
    so that new records can be added to the database."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as the input. It also creates
        all of the buttons and GUI elements required along with any necessary attributes."""
        self.__master = master
        tk.Frame.__init__(self, container)
        count = 0
        # The following is the creation of the buttons for each record type
        for i in ["Teacher", "Assistant", "Student", "Class", "Event", "Venue"]:
            if i == "Teacher":
                # If the record is a Teacher then the button cannot be used by a non-admin
                button = tk.Button(self, font=('Arial', 14), text=i,
                                   command=lambda i=i: [self.__master.showPage(i), self.__master.createCurrentPage()]
                                   if self.__master.checkAdmin() else None)
            else:
                """Each button opens the relevant form and puts it in the create state. Lambda is used to pass the page 
                name to show. Using i=i, means that the value of i in the current iteration reamains."""
                button = tk.Button(self, font=('Arial', 14), text=i,
                                   command=lambda i=i: [self.__master.showPage(i), self.__master.createCurrentPage()])
            button.grid(row=2, column=count, padx=10, pady=10)
            count += 1
        title = tk.Label(self, font=('Arial', 24, 'bold'), text="New Record")
        title.grid(row=0, padx=10, pady=(10, 0), columnspan=count)

    def windowTitle(self):
        return "New Record"


class UniformPage(tk.Frame):
    """The UniformPage is a tkinter frame for navigating to different parts of the uniform management side of the
    software."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as the input. It also creates
        all of the buttons and GUI elements required along with any necessary attributes."""
        self.__master = master
        tk.Frame.__init__(self, container)
        # The following is the creation of the GUI buttons
        addButton = tk.Button(self, text="Create Uniform Item", command=self.__uniformType)
        addButton.grid(row=2, column=0, padx=10, pady=10)
        viewButton = tk.Button(self, text="View Uniform Orders", command=lambda: [self.__master.showPage("UniformOrderList"),
                                                                                  self.__master.getCurrentPage().getCurrent()])
        viewButton.grid(row=2, column=1, padx=10, pady=10)
        orderButton = tk.Button(self, text="Order Uniform", command=lambda: [self.__master.showPage("UniformOrderForm"),
                                                                             self.__master.createCurrentPage()])
        orderButton.grid(row=2, column=2, padx=10, pady=10)
        title = tk.Label(self, font=('Arial', 24, 'bold'), text="Uniform")
        title.grid(row=0, padx=10, pady=(10, 0), columnspan=3)

    def windowTitle(self):
        return "Uniform"

    def __uniformType(self):
        """This function shows the UniformTypeForm and puts it in the create state if the user is an admin."""
        if self.__master.checkAdmin():
            self.__master.showPage("UniformTypeForm")
            self.__master.createCurrentPage()


class UniformOrderForm(tk.Frame):
    """The UniformOrderForm is a tkinter window which facilitates the user ordering uniform from a list of possible
    options."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as the input. It also creates
        all of required GUI elements along with any necessary attributes."""
        tk.Frame.__init__(self, container)
        title = tk.Label(self, text="Uniform Order", font=('Arial', 24, 'bold'))
        title.grid(row=0, column=0, columnspan=3)
        # Creating the variable to store the ID of the order
        self.__ID = None
        # Creating the variable to store the ID of the student the order is for (foreign key)
        self.__studentID = None
        self.__master = master
        self.__handler = self.__master.getEntityHandler()
        self.__searcher = entityHandler.Searcher(self.__handler)
        self.__type = "UniformOrder"
        self.__fields = []
        _row = 10
        # Creating the GUI data fields
        for text in ["Student", "Date", "Cost (£)"]:
            label = tk.Label(self, text=text)
            label.grid(row=_row, column=0, padx=10, pady=10)
            var = tk.StringVar()
            var.set("")
            label = tk.Label(self, textvariable=var)
            label.grid(row=_row, column=1, padx=10, pady=10)
            self.__fields.append(var)
            _row += 1
        # Creating the other GUI elements
        self.__setButton = tk.Button(self, text="Set", command=self.__setStudent)
        self.__saveButton = tk.Button(self, text="Save", command=self.__save)
        itemLabel = tk.Label(self, text="Items", font=('Arial', '15', 'bold'))
        itemLabel.grid(row=20, column=0, columnspan=2, padx=10, pady=10)
        self.__addButton = tk.Button(self, text="+", command=self.__add)
        self.__rows = []
        self.__buttons = []
        self.__currentRow = 30

    def windowTitle(self):
        return "Uniform Order"

    def __add(self):
        """This function adds a uniform type to the order"""
        searcher = SearchWidget(self.__master)
        """Calling the search window with selection mode single and filter type "UniformType" - the result of the search 
        is stored in the variable item"""
        item = searcher.setMode(tk.SINGLE, ["UniformType"])
        if len(item) == 1: # This ensures the user has selected a UniformType
            theItem = item["UniformType"][0]
            # Adding a new UniformOrderLine to on the next row to show this UniformType and appending it to self.__rows
            row = UniformOrderLine(self.__master, self, theItem)
            self.__rows.append(row)
            row.grid(row=self.__currentRow, column=0, columnspan=2)
            # Adding a delete button so that this UniformOrderLine can be deleted and appending it to self.__buttons
            deleteButton = tk.Button(self, text="X")
            deleteButton.config(command=lambda _deleteButton=deleteButton: self.__deleteRow(_deleteButton))
            deleteButton.grid(row=self.__currentRow, column=2)
            self.__buttons.append(deleteButton)
            self.__currentRow += 1
            # Recalculating the overall order cost by calling refreshCost
            self.refreshCost()

    def refreshCost(self, *args):
        """This function takes any number of arguments it is passed. It uses the Decimal module to calculate the total
        cost of other order by adding all of the individual row (UniformOrderLine) costs"""
        totalCost = Decimal(00.00)
        for row in self.__rows:
            # Getting the cost of a row by calling getTotalCost on the UniformOrderLine
            totalCost += row.getTotalCost()
        # Rounding the answer up to two decimal places
        totalCost = totalCost.quantize(Decimal('0.01'), rounding="ROUND_UP")
        # Setting the cost tkinter variable to the value of totalCost
        self.__fields[2].set(str(totalCost))

    def __deleteRow(self, button):
        """This function takes a tkinter delete button as its input and deletes the UniformOrderLine and delete button
         on that row"""
        # Finding the index of the passed button
        index = self.__buttons.index(button)
        # Removing the UniformOrderLine on the same row as the button
        self.__rows[index].grid_remove()
        self.__rows.pop(index)
        # Removing the button
        self.__buttons[index].grid_remove()
        self.__buttons.pop(index)
        # Recalculating the cost without this UniformOrderLine
        self.refreshCost()

    def __save(self):
        """This function saves the uniform order and displays an error message if the order is not valid"""
        message = ""
        # Checking a student has been selected
        if self.__fields[0].get() == "":
            message = "No Student"
        # Checking there are items in the order
        if len(self.__rows) == 0:
            message = "No Items"
        # If no error message has been generated then create a UniformOrder record and the UniformOrderLine records for each row
        if message == "":
            # Setting the ID of the order to the result of calling update record where the type, current ID, and list of data is passed
            self.__ID = self.__handler.updateRecord("UniformOrder", self.__ID, [self.__studentID, self.__fields[1].get(), self.__fields[2].get()])
            for row in self.__rows:
                # Getting the values from a UniformOrderLine and creating a matching record with this data
                values = row.getValues()
                self.__handler.updateRecord("UniformOrderLine", None, [self.__ID, values[0], values[3], values[2], values[1], values[4]])
            self.__master.showPage("UniformPage")
        else:
            # If an error message has been generated then show this in a pop-up tkinter box
            tk.messagebox.showinfo("Error", message)

    def __setStudent(self):
        """This function allows the user to select the student to link the order to from a search window"""
        searcher = SearchWidget(self.__master)
        # Opening a search window in single selection mode with filter type Student. The returned value is stored in variable 'result'
        result = searcher.setMode(tk.SINGLE, ["Student"])
        if len(result) > 0:
            # If the user has selected a record in the search then set __studentID to this recordID
            self.__studentID = result["Student"][0]
            # Display the name of the student by setting the tkinter string variable to the result of a call to getView
            self.__fields[0].set(self.__searcher.getView("Student", self.__studentID))

    def createForm(self):
        """This function puts the UniformOrderForm in its create state"""
        self.__saveButton.grid(row=100, column=0, columnspan=3, padx=10, pady=10)
        self.__setButton.grid(row=10, column=2, padx=5, pady=10)
        self.__ID = None
        self.__addButton.grid(row=20, column=2, padx=10, pady=10, sticky='W')
        self.__reset()

    def __reset(self):
        """This function resets the UniformOrderForm to its default values"""
        self.__currentRow = 30
        self.__fields[0].set("")
        # Setting the date of the order to current date (by converting datetime object for today to string)
        self.__fields[1].set(datetime.datetime.now().strftime("%d/%m/%Y"))
        self.__fields[2].set("00.00")
        self.__buttons = []
        # Removing any UniformOrderLines
        for row in self.__rows:
            row.grid_remove()
        self.__rows = []

    def viewForm(self, ID):
        """This function receives the ID of a UniformOrder as input puts the UniformOrderForm in its view state to display
        the corresponding order."""
        self.__setButton.grid_remove()
        self.__saveButton.grid_remove()
        self.__addButton.grid_remove()
        self.__reset()
        self.__ID = ID
        # Getting the values for the order matching the passed variable ID by calling getData
        values = self.__handler.getData("UniformOrder", self.__ID)
        # Setting the tkinter string variables to the necessary values
        self.__fields[0].set(self.__searcher.getView("Student", values[0]))
        self.__fields[1].set(values[1])
        self.__fields[2].set(values[2])
        # Getting the UniformOrderLines which contain the order ID passed to the function as a foreign key
        rows = self.__handler.getOrderLines(self.__ID)
        for row in rows:
            """For all of the UniformOrderLines, get the data contained within them and storing this in values. Then a 
            new instance of a tkinter OrderLineView object is created and values is passed to it. This is shown on a new row."""
            values = self.__handler.getData("UniformOrderLine", row)
            # Getting the view string for the student matching the foreign key (ID) within values
            values[1] = self.__searcher.getView("UniformType", values[1])
            lineView = OrderLineView(self, values)
            lineView.grid(row=self.__currentRow, column=0, columnspan=3, padx=10)
            self.__rows.append(lineView)
            self.__currentRow += 1


class OrderLineView(tk.Frame):
    """This tkinter frame is for viewing the details of a UniformOrderLine in an order"""
    def __init__(self, container, data):
        """This constructor takes the container of the tkinter widget as its input along with a list of data for an order
        line. It then displays the values in data using tkinter labels."""
        tk.Frame.__init__(self, container)
        nameLabel = tk.Label(self, text=data[1])
        nameLabel.grid(row=1, column=0, padx=10, pady=10)
        colourLabel = tk.Label(self, text=data[4])
        colourLabel.grid(row=1, column=1, padx=10, pady=10)
        sizeLabel = tk.Label(self, text=data[3])
        sizeLabel.grid(row=1, column=2, padx=10, pady=10)
        quantityLabel = tk.Label(self, text=data[2])
        quantityLabel.grid(row=1, column=3, padx=10, pady=10)


class UniformOrderLine(tk.Frame):
    """The UniformOrderLine is a tkinter widget which is used to show the selection of a UniformType in a UniformOrder.
    It allows the user to select the attributes for the UniformType that they want (such as  colour, quantity etc.)"""
    def __init__(self, master, container, itemID):
        """This constructor takes the container of the widget, the master controller and the ID of a UniformType record
        as the input. It also creates all of GUI elements required along with any necessary attributes."""
        tk.Frame.__init__(self, container)
        self.__master = master
        self.__form = container
        self.__handler = master.getEntityHandler()
        values = self.__handler.getData("UniformType", itemID)
        self.__itemID = itemID
        name = values[0]
        colours = values[1]
        sizes = values[2]
        self.__cost = values[3]
        # Creating the GUI elements
        nameLabel = tk.Label(self, text=name)
        nameLabel.grid(row=0, column=0, padx=10, pady=10)
        costLabel = tk.Label(self, text=("£" + self.__cost))
        costLabel.grid(row=0, column=3, padx=10, pady=10)
        self.__sizesVar = tk.StringVar()
        self.__sizesVar.set(sizes[0])
        self.__coloursVar = tk.StringVar()
        self.__coloursVar.set(colours[0])
        coloursMenu = tk.OptionMenu(self, self.__coloursVar, *colours)
        coloursMenu.grid(row=0, column=1, padx=10, pady=10)
        sizesMenu = tk.OptionMenu(self, self.__sizesVar, *sizes)
        sizesMenu.grid(row=0, column=2, padx=10, pady=10)
        self.__quantityVar = tk.StringVar()
        # Tracing the quantity tkinter string variable so that when it changes, the cost of the order is refreshed
        self.__quantityVar.trace("w", self.__form.refreshCost)
        self.__quantityVar.set("1")
        quantities = []
        for x in range(1,11):
            quantities.append(x)
        quantityMenu = tk.OptionMenu(self, self.__quantityVar, *quantities)
        quantityMenu.grid(row=0, column=4, padx=10, pady=10)

    def getValues(self):
        """This function returns the values of the attributes of the object"""
        return [self.__itemID, self.__coloursVar.get(), self.__sizesVar.get(), self.__quantityVar.get(), self.__cost]

    def getCost(self):
        """This function returns the value of the cost object as a Decimal object"""
        return Decimal(self.__cost)

    def getTotalCost(self):
        """This function returns the total cost of the UniformOrderLine by multiplying the cost of the UniformType by
        the quantity. It returns a Decimal object."""
        return Decimal(self.__cost) * Decimal(self.__quantityVar.get())


class RecordList(tk.Frame):
    """The RecordList tkinter object provides a list of all the records of a certain type which can be viewed or deleted."""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as the input. It also creates
        all of the GUI elements required along with any necessary attributes."""
        tk.Frame.__init__(self, container)
        self.__master = master
        self.__handler = master.getEntityHandler()
        self.__searcher = entityHandler.Searcher(self.__handler)
        self.__type = None
        self.__name = ""
        self.__text = ""
        # Creating rhe GUI elements
        self.__title = tk.Label(self, text=self.__name, font=('Arial', 24, 'bold'))
        self.__title.grid(row=0, column=0, columnspan=2)
        self.__box = tk.Listbox(self, selectmode=tk.MULTIPLE, height=25, width=25)
        self.__box.grid(row=10, rowspan=2, column=0, padx=10, pady=10)
        self.__items = []
        deleteButton = tk.Button(self, text="X", command=self.__delete)
        deleteButton.grid(row=11, column=1, padx=10, pady=10, sticky='N')
        viewButton = tk.Button(self, text="*", command=self.__view)
        viewButton.grid(row=10, column=1, padx=10, pady=10, sticky='S')

    def getCurrent(self):
        """This function gets all of the records matching the type (self.__type) and shows them in the list"""
        self.__items = []
        self.__box.delete(0, tk.END)
        # Getting all the records matching type (self.__type) and storing the returned values in the variable records
        records = self.__searcher.search("", [self.__type])
        if len(records) > 0:
            records = records[self.__type]
        for record in records:
            # Appending record (the ID of a record) to self.__items
            self.__items.append(record)
            # Get the string to visually identify record by calling getView
            values = self.__searcher.getView(self.__type, record)
            if self.__type == "UniformOrder":
                """If the record is of type UniformOrder then the view string consists of the name of the student the 
                order is for and the date of the order"""
                view = str(self.__searcher.getView("Student", values[0])) + " - " + values[1]
            else:
                view = values
            # Inserting the view string into the list of records
            self.__box.insert(tk.END, view)

    def set(self, type, name):
        """This function takes variables type and string as its input and sets the corresponding private attributes to these"""
        self.__type = type
        self.__name = name
        # Setting the title of the list to the variable name
        self.__title.config(text=self.__name)

    def windowTitle(self):
        """This function sets the window title"""
        return self.__name + " List"

    def __view(self):
        """If one record is selected in the list of records, then the form matching the record type shown in this object
        is displayed. The form displays the record that was selected in the list."""
        if len(self.__box.curselection()) == 1:
            self.__master.showPage(self.__type + "Form")
            # The ID of the record selected is the value in self.__items at the same index as the selected record in the list
            self.__master.viewCurrentPage(self.__items[self.__box.curselection()[0]])

    def __delete(self):
        """This function deletes the selected records in the list from the database."""
        selected = self.__box.curselection()
        for index in selected:
            self.__box.delete(index, index)
            # Removing the record at index in the list of records
            item = self.__items[index]
            self.__items.pop(index)
            self.__handler.deleteRecord(self.__type, item)
            """Calling customDelete which may be necessary for child classes to delete all database records relating to 
            the selected record in this widget"""
            self.customDelete(item)

    def customDelete(self, item):
        """This function takes the input of variable item. It is required by some child classes."""
        pass


class UniformOrderList(RecordList):
    """The UniformOrderList is a tkinter window and child class of RecordList. It allows a list of all the UniformOrder
    records in the database to be viewed and deleted."""
    def __init__(self, container, master):
        """This constructor takes the container of the tkinter window and the master controller as an input."""
        RecordList.__init__(self, container, master)
        # Setting the type to "UniformOrder" and the name of the record type displayed to "Uniform Order"
        self.set("UniformOrder", "Uniform Order")
        # Refreshing the list of records
        self.getCurrent()

    def customDelete(self, item):
        """This function takes the input of variable item (the ID of a UniformOrder) and deletes any UniformOrderLines
        containing item as a foreign key."""
        self.__handler.deleteOrderLines(item)


class UserAccountList(RecordList):
    """The UserAccountList is a tkinter window and child class of RecordList. It allows a list of all the User records
    in the database to be viewed and deleted."""
    def __init__(self, container, master):
        RecordList.__init__(self, container, master)
        # Setting the type to "User" and the name of the record type displayed to "User"
        self.set("User", "User")
        # Refreshing the list of records
        self.getCurrent()


class NoteList(tk.Frame):
    """The NoteList tkinter frame provides a list of notes that exist for a record"""
    def __init__(self, container, master, form):
        """This constructor takes the container of this tkinter frame, the master controller and the form the NoteList is
        in"""
        tk.Frame.__init__(self, container)
        self.__form = form
        self.__master = master
        self.__handler = master.getEntityHandler()
        self.__searcher = entityHandler.Searcher(self.__handler)
        # Creating the GUI objects
        title = tk.Label(self, text="Notes", font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2)
        self.__buttons = []
        addButton = tk.Button(self, text="+", command=lambda: [self.__addNote(), self.__form.removeNoteList()])
        addButton.grid(row=0, column=2, columnspan=2)
        # Creating a variable to store the ID of the record the notes are stored about
        self.__recordID = None

    def setList(self, ID):
        """This function takes the ID of the record to find Note records for as an input. It then displays these notes
        in a list of buttons."""
        self.__recordID = ID
        # Getting all of the notes with foreign key of self.__recordID
        notesList = self.__searcher.getNotes(self.__recordID)
        _row = 10
        _column = 0
        # Deleting any previous buttons that navigated to a note
        for i in self.__buttons:
            i.destroy()
        for note in notesList:
            """For all of the notes in notesList, get the values of the note and create a button that opens the NoteForm 
            displaying that note. The button will have text with the name of the note and the date is was created"""
            values = self.__handler.getData("Note", note)
            date = (values[2].strftime("%d") + "/" + values[2].strftime("%m") + "/" + values[2].strftime("%Y"))
            button = tk.Button(self, text=(str(values[0]) + ": " + date), command=lambda a_note=note:
            [self.__master.showPage("Note"), self.__master.viewCurrentPage(a_note), self.__form.removeNoteList()])
            self.__buttons.append(button)
            button.grid(row=_row, column=0, padx=10, pady=10)
            _row += 1
            _column += 1

    def __addNote(self):
        """This function allows the user to add a new Note record to the database by opening the NoteForm tkinter window
        in its create state"""
        self.__master.showPage("Note")
        # Passing self.__recordID to specify which record the new note is for
        self.__master.createNotePage(self.__recordID)


class UniformTypeForm(Form):
    """The UniformTypeForm is a child of the Form class and is used to collect data for a UniformType record.

    This class has many similarities with a PersonForm so there is no repeated commenting."""
    def __init__(self, container, master):
        Form.__init__(self, container, master)
        self.titleText.set("Uniform Type")
        # Creating the GUI elements
        instruction = tk.Label(self, text="Please separate colours and sizes with a comma (,)")
        instruction.grid(row=10, column=0, padx=10, columnspan=2, pady=(10, 0))
        count = 0
        _row = 11
        for text in ["Name", "Colours", "Sizes", "Cost (£)"]:
            label = tk.Label(self, text=text)
            label.grid(row=_row+1, column=0, padx=10, pady=10)
            entry = tk.Entry(self, state="normal", disabledforeground="black")
            entry.grid(row=_row+1, column=1, padx=10, pady=10)
            self.appendEntries(entry)
            var = tk.StringVar()
            var.set("")
            self.errors.append(var)
            error = tk.Label(self, textvariable=self.errors[count], fg="red")
            error.grid(row=_row, column=1, padx=1, pady=0)
            _row += 2
            count += 1

    def validate(self):
        """This function validates the entries to the form and follows a similar style to the function of the same name
        in PersonForm. Commenting is not repeated."""
        data = self.getEntries()
        errors = [""] * 4
        errors[0] = validator.validateName(data[0])
        errors[1] = ""
        errors[2] = ""
        errors[3] = validator.validateCost(data[3])
        validated = True
        for i in errors:
            if i is "":
                pass
            else:
                validated = False
        if validated:
            self.setID(self.updateObject(data))
            self.viewForm(self.getID())
        else:
            count = 0
            for i in errors:
                self.errors[count].set(i)
                count += 1

    def updateObject(self, data):
        """This function takes a list of data as its input and updates the UniformType record matching self.getID with
        the values in data. It returns the result of a call to updateRecord."""
        # If data[1] is an empty string (no colours entered) then replace data[1] with a list containing "N/A"
        if data[1] == "":
            data[1] = ["N/A"]
        else:
            data[1] = data[1].split(",")
            aList = []
            for x in data[1]:
                x = x.strip(",")
                x = x.strip()
                aList.append(x)
            data[1] = aList
        # If data[2] is an empty string (no sizes entered) then replace data[2] with a list containing "N/A"
        if data[2] == "":
            data[2] = ["N/A"]
        else:
            """Split the string data[2] at every comma and create a new list containing each item either side of the 
            comma with excess spaces removes. Store this list in data[2]"""
            data[2] = data[2].split(",")
            aList = []
            for x in data[2]:
                # Removing excess commas and spaces from each item in data[2]
                x = x.strip(",")
                x = x.strip()
                aList.append(x)
            data[2] = aList
        """Returning the result of a call to updateRecord where the type of record this object shows is passed, along with 
        the ID of the record currently being displayed and the list data"""
        return self.entityHandler.updateRecord(self.getType(), self.getID(), data)

    def viewForm(self, ID):
        """This function takes ID (the ID or primary key of a UniformType record) as its input and displays this in this
        tkinter object in its view state"""
        self.__ID = ID
        # Getting the data of UniformType record matching ID
        values = self.entityHandler.getData(self.getType(), self.__ID)
        data = values
        string = ""
        """The following takes the items in lists values[1] and values[2] and turns them into strings seperated by 
        commas (with excess commas removed). These lists are then used in dropdown menus for colours and sizes."""
        for value in values[1]:
            string += value + (", ")
        string = string.strip(", ")
        data[1] = string
        string = ""
        for value in values[2]:
            string += value + (", ")
        string = string.strip(", ")
        data[2] = string
        # Set this tkinter UniformType object to its view state and display the values in the list data
        self.setState(data, True)

    def editForm(self, ID):
        """This function takes ID (the ID or primary key of a UniformType record) as its input and displays this in this
        tkinter object in its edit state"""
        self.__ID = ID
        values = self.entityHandler.getData(self.getType(), self.__ID)
        data = values
        string = ""
        for value in values[1]:
            string += value + (", ")
        string = string.strip(", ")
        data[1] = string
        string = ""
        for value in values[2]:
            string += value + (", ")
        string = string.strip(", ")
        data[2] = string
        # Set this tkinter UniformType object to its edit state and display the values in the list data
        self.setState(data, False)

    def windowTitle(self):
        return "Uniform Type"


class UserForm(Form):
    """The UserForm tkinter frame is a child class of the Form object. This is used to gather data about a User record
    in the database"""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as the input. It also creates
        all of required GUI elements along with any necessary attributes."""
        Form.__init__(self, container, master)
        self.titleText.set("User Account")
        _row = 50
        count = 0
        self.__master = master
        self.__handler = self.__master.getEntityHandler()
        # Defining a boolean variable to determine whether the form is in the create state
        self.__create = False
        # Creating all of the GUI elements
        for text in ["Username", "Password", "Confirm Password", "E-Mail", "Admin"]:
            label = tk.Label(self, text=text)
            label.grid(row=_row, column=0, padx=10, pady=10)
            var = tk.StringVar()
            var.set("")
            self.errors.append(var)
            error = tk.Label(self, textvariable=self.errors[count], fg="red")
            error.grid(row=_row-1, column=1, padx=1, pady=0)
            _row += 2
            count += 1
        usernameEntry = tk.Entry(self)
        self.appendEntries(usernameEntry)
        # Creating password entry fields where the text is hidden and only a '•' symbol is shown
        passwordEntry = tk.Entry(self, show="•")
        self.appendEntries(passwordEntry)
        confirmEntry = tk.Entry(self, show="•")
        self.appendEntries(confirmEntry)
        emailEntry = tk.Entry(self)
        self.appendEntries(emailEntry)
        _row = 50
        for entry in self.getEntryFields():
            entry.grid(row=_row, column=1, padx=10, pady=10)
            _row += 2
        self.__admin = tk.IntVar()
        adminButton = tk.Checkbutton(self, variable=self.__admin)
        adminButton.grid(row=58, column=1, padx=10, pady=10)

    def windowTitle(self):
        return "User Account Form"

    def validate(self):
        """This function validates the data entered into the form and updates the record in the database if it is
        valid. This very similar in style to the function of the same name in the PersonForm class - therefore commenting
        is not repeated."""
        data = self.getEntries()
        data.append(self.__admin.get())
        errors = [""] * 5
        errors[0] = self.__validateUsername(data[0])
        errors[1] = self.__validatePassword(data[1])
        errors[2] = self.__validateConfirm(data[1], data[2])
        errors[3] = validator.validateEmail(data[3])
        errors[4] = ""
        validated = True
        for i in errors:
            if i is "":
                pass
            else:
                validated = False
        if validated:
            self.__create = False
            del data[2]
            # Storing in data[1] the password in a hashed form by calling the passwordManager's encrypt method and passing data[1]
            data[1] = passwordManagememt.PasswordManager(self.__master.getEntityHandler()).encrypt(data[1])
            self.setID(self.updateObject(data))
            self.viewForm(self.getID())
        else:
            count = 0
            for i in errors:
                self.errors[count].set(i)
                count += 1

    def __validatePassword(self, password):
        """This function takes a string as its input and returns a string 'message' which determines whether or not the input
        is a valid password"""
        # Ensuring the password is longer than 5 characters
        if len(password) > 5:
            message = ""
        else:
            message = "Password too short"
        return message

    def __validateUsername(self, username):
        """This function takes a string as its input and returns a string 'message' which determines whether or not the input
        is a valid username"""
        # If the UserForm is in create state, ensure the username doesn't already exist
        if self.__create:
            if self.__handler.accountExists(username):
                message = "This username already exists"
            else:
                message = ""
            # Enforce a presence check on the username
            if len(username) == 0:
                message = "Field required"
        else:
            message = ""
        return message

    def __validateConfirm(self, first, second):
        """This function takes two strings as its input and returns a string 'message' which determines whether or not
        the two input strings (passwords) match"""
        # Ensure the two strings passed to the function are the same
        if first == second:
            message = ""
        else:
            message = "Passwords do not match"
        return message

    def editForm(self, ID):
        """This function takes the ID (username) of a User record as its input and displays that record in the UserForm.
        It also sets the UserForm to its edit state."""
        values = self.entityHandler.getData(self.getType(), self.__ID)
        values.insert(0, self.__ID)
        # Set the password to a blank string
        values[1] = ""
        # Insert another blank string (to fill the password confirm field)
        values.insert(2, "")
        # Set the admin tickbox
        self.__admin.set(values.pop(4))
        self.setState(values, False)

    def createForm(self):
        """This function puts the UserForm in its create state and allows a new User record to be created"""
        self.setID(None)
        self.setState(None, False)
        self.__create = True

    def viewForm(self, ID):
        """This function takes the ID (username) of a User record as its input and displays that record in the UserForm.
        It also sets the UserForm to its view state."""
        self.__ID = ID
        values = self.entityHandler.getData(self.getType(), self.__ID)
        values.insert(0, ID)
        values[1] = ""
        values.insert(2, "")
        self.__admin.set(values.pop(4))
        self.setState(values, True)

    def updateObject(self, data):
        return self.entityHandler.updateUser(data[0], data[1:])


class SearchWidget(tk.Toplevel):
    """The SearchWidget is a tkinter Toplevel widget (a window that appears about the rest of the tkinter window) and it
    allows the user to search for records in the database"""
    def __init__(self, master):
        """This constructor takes the master controller as the input. It also creates all of required GUI elements
        along with any necessary attributes."""
        tk.Toplevel.__init__(self)
        self.__master = master
        # Prevent the window from being resized
        self.resizable(0, 0)
        # Set the title of the window
        tk.Tk.wm_title(self, "Search")
        # Hide the main window below this
        self.__master.withdraw()
        self.__boxes = []
        self.__sorter = entityHandler.Sorter()
        self.__values = []
        self.__currentTypes = []
        self.__map = []
        self.__selection = {}
        # Creating the GUI elements
        title = tk.Label(self, text="Search", font=('Arial', 24, 'bold'))
        title.grid(row=0, column=0, columnspan=3)
        self.__bar = tk.Entry(self)
        self.__bar.grid(row=2, column=0, columnspan=1)
        self.__button = tk.Button(self, text="Go", command=self.search)
        self.__button.grid(row=2, column=1)
        # Creating a box to contain the list of search results which allows multiple items to be selected at once
        self.__output = tk.Listbox(self, selectmode=tk.MULTIPLE, width=40, height=30)
        self.__output.grid(row=3, column=0, pady=10, padx=10)
        self.__searcher = entityHandler.Searcher(master.getEntityHandler())
        submitButton = tk.Button(self, text="Submit", command=self.submit)
        submitButton.grid(row=4, column=0, columnspan=2)

    def search(self):
        """This function takes the user inputted search key and finds any records matching this (within the constraints
        of the filter types). It then displays these records in a list."""
        # Clear any current results
        self.__output.delete(0, tk.END)
        self.__currentTypes = []
        # Append to currentTypes any of the filter options that have been ticked
        for i in range(0, len(self.__order)):
            if self.__values[i].get() == 1:
                self.__currentTypes.append(self.__order[i])
        """Store in results a dictionary of search results after a call to the search function (having passed the text 
        in the search bar and a list of currentTypes"""
        results = self.__searcher.search(self.__bar.get(), self.__currentTypes)
        temporary = {}
        """Take all of the results of the search and map them to a dictionary with key of the string records are viewed 
        by and value of a list containing the record's type and ID"""
        for currentType in self.__currentTypes:
            for entity in results[currentType]:
                temporary[self.__searcher.getView(currentType, entity)] = [currentType, entity]
        # Ordering the results by the merge sort
        ordered = self.__sorter.mergeSort(list(temporary.keys()))
        for record in ordered:
            # Putting the ordered results in the listbox
            self.__output.insert(tk.END, record)
            # Mapping each result in the listbox to a record ID
            self.__map.append(temporary[record])

    def setMode(self, mode, order):
        """This function takes variable mode and a list order as its input and returns the user selection (from the list
        of their search results)"""

        """If the value of order is 0 then a default order of filter types is used (and if the user is an admin 
        the type Teahcer is also included"""
        if order == 0:
            self.__order = ["Student", "Assistant", "Class", "Venue", "Event"]
            if self.__master.isAdmin():
                self.__order.insert(1, "Teacher")
        else:
            self.__order = order
        _row = 0
        # Creating a frame and including in it labels for each item in order and a corresponding tick box
        frame = tk.Frame(self)
        for key in self.__order:
            label = tk.Label(frame, text=key)
            label.grid(row=_row, column=0)
            var = tk.IntVar()
            box = tk.Checkbutton(frame, variable=var)
            box.grid(row=_row, column=1)
            box.select()
            self.__boxes.append(box)
            self.__values.append(var)
            _row += 1
        frame.grid(row=3, column=1)
        # Hide the main master window below this
        self.__master.withdraw()
        # Set all the other attributes to their default values
        self.__bar.delete(0, tk.END)
        self.__output.delete(0, tk.END)
        self.__selection = {}
        self.__map = []
        # Set the selection mode for the list of results to the passed mode variable
        self.__output.config(selectmode=mode)
        self.wait_window(self) # Do not execute the code after this line until the SearchWidget has been destroyed
        # Make the main master window below this visible again and return the user selection
        self.__master.deiconify()
        return self.__selection

    def submit(self):
        """This function gets the records selected by the user and stores them in self.__selection. It then destroys
        the SearchWidget (itself)."""
        indexes = list(self.__output.curselection())
        output = {}
        """For each of the selected records in the list, store its ID and type in output (with type as a key and the value 
        as a list of records of that type"""
        for index in indexes:
            if self.__map[index][0] in output:
                output[self.__map[index][0]].append(self.__map[index][1])
            else:
                output[self.__map[index][0]] = [self.__map[index][1]]
        self.__selection = output
        self.destroy()


class EntityPicker(tk.Frame):
    """An EntityPicker is a  tkinter frame object. It provides a list of records which can be used to represent a
    relationship in the database. Records can be added, deleted or viewed."""
    def __init__(self, container, master, relationship, parentType, state):
        """This constructor takes the container of the EntityPicker, master controller, relationship it represents,
        type of record the form the picker is contained within represents, and selection mode as inputs. It also creates
        all of the GUI elements and necessary attributes."""
        tk.Frame.__init__(self, container)
        self.__relationship = relationship
        self.__parentID = None
        self.__master = master
        self.__state = state
        self.__handler = master.getEntityHandler()
        # Search type is the part of the relationship that is not the parentType
        self.__searchType = self.__relationship[:-len(parentType)]
        self.__searcher = entityHandler.Searcher(master.getEntityHandler())
        # Creating the GUI elements
        self.__box = tk.Listbox(self, selectmode=state)
        if state == tk.SINGLE:
            # The EntityPicker will be smaller if selection mode is single
            self.__box.config(width=16, height=2)
        else:
            self.__box.config(width=16, height=8)
        self.__box.grid(row=0, column=0, rowspan=3, padx=(0, 10))
        self.__list = []
        self.__addButton = tk.Button(self, text="+", command=self.__add)
        self.__addButton.grid(row=0, column=1)
        self.__viewButton = tk.Button(self, text="*", command=self.__view)
        self.__viewButton.grid(row=2, column=1)
        self.__deleteButton = tk.Button(self, text="X", command=self.__delete)
        self.__deleteButton.grid(row=1, column=1)

    def __view(self):
        """This function allows the record selected in the picker to be show in its corresponding form. With the form
        in its view state."""
        # Get the indexes of selected items in the picker
        indexes = list(self.__box.curselection())
        if len(indexes) == 1:
            # If only one item is selected then show its corresponding Form widge
            self.__master.showPage(self.__searchType)
            # Get the ID of the record in the EntityPicker that is selected
            ID = self.__list[indexes[0]]
            # View the selected record in its Form by calling viewCurrentPage and passing ID
            self.__master.viewCurrentPage(ID)

    def default(self):
        """This function sets the default values of the EntityPicker"""
        # Clearing the list of records
        self.__box.delete(0, tk.END)
        self.__list = []

    def setValue(self, ID):
        """This function takes a value ID as its input and sets the parentID attribute to that (this is the ID of the record
        the EntityPicker is creating relationships with)"""
        self.__parentID = ID
        # Refresh the list of records in the picker
        self.__getCurrent()

    def __getCurrent(self):
        """This function gets all of the records that should be in the EntityPicker and displays them"""
        self.default()
        """Iterate through all the sets of foreign IDs which are from a record of type self.__relationship and contain 
        self.__parentID"""
        for record in self.__handler.getForeigns(self.__relationship, self.__parentID):
            # Display the record in the returned value of getForeigns that is not the __parentID in the EntityPicker
            self.__box.insert(tk.END, self.__searcher.getView(self.__searchType, record[1]))
            self.__list.append(record[1])

    def __add(self):
        """This function adds a record to the EntityPicker"""
        check = True
        """This checks if it is permitted to add another record. If the EntityPicker has state tk.SINGLE and a record 
        already, then no more can be added"""
        if self.__state == tk.SINGLE:
            if self.__box.size() == 1:
                check = False
        if check:
            # Creating an instance of a search widget
            searchWidget = SearchWidget(self.__master)
            # The result of a search in selection mode self.__state with filter type self.__searchType is stored in new
            new = searchWidget.setMode(self.__state, [self.__searchType])
            if len(new) > 0:
                # If the user has returned records from the search, create a relationship between each and self.__parentID
                for record in new[self.__searchType]:
                    self.__handler.createRelationship(self.__relationship, self.__parentID, record)
            # Refresh the list of records in the EntityPicker
            self.__getCurrent()

    def __delete(self):
        """This funnction deletes any selected records from the EntityPicker"""
        indexes = list(self.__box.curselection())
        for index in indexes:
            # Delete the relationship of type self.__relationship involving the record of ID at self.__list[index] and self.__parentID
            self.__handler.deleteEntityRelationship(self.__relationship, self.__list[index], self.__parentID)
        self.__getCurrent()

    def setState(self, state):
        """This function takes a string variable state as its input and sets the state of the EntityPicker's buttons
        to the opposite"""
        if state == "disabled":
            state = "normal"
        elif state == "normal":
            state = "disabled"
        self.__addButton.config(state=state)
        self.__deleteButton.config(state=state)
        self.__viewButton.config(state=state)


class RegisterSender(tk.Toplevel):
    """The RegisterSender is a tkinter Toplevel widget (a window that appears about the rest of the tkinter window) and
    it allows the user to generate a register for a class/event"""
    def __init__(self, master, handler, ID, name, entityType):
        """This constructor takes the master controller, an entityHandler, ID of a class/event, name of a class/event
        and the type class/event as its input. It then generates all of the necessary GUI elements and required
        attributes."""
        tk.Toplevel.__init__(self)
        self.__type = entityType
        self.__ID = ID
        # If the red 'X' is clicked to close the window, the call the function self.__close
        self.protocol("WM_DELETE_WINDOW", self.__close)
        self.__name = name
        self.__master = master
        self.resizable(0, 0)
        self.__searcher = entityHandler.Searcher(handler)
        self.__handler = handler
        self.__students = []
        self.__emails = []
        # Generating GUI elements
        tk.Tk.wm_title(self, self.__type + " Register Sender")
        title = tk.Label(self, text= self.__type + " Register Sender", font=('Arial', 24, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        _row = 1
        self.__vars = []
        for item in ["self", "teacher"]:
            alabel = tk.Label(self, text="Send to " + item + "?")
            alabel.grid(row=_row, column=0)
            var = tk.IntVar()
            check = tk.Checkbutton(self, variable=var)
            check.grid(row=_row, column=1)
            self.__vars.append(var)
            _row += 1
        submitButton = tk.Button(self, text="Generate & Send", command=self.__check)
        submitButton.grid(row=10, columnspan=2)

    def generateRegister(self, students, name, emails):
        """This function takes a list of student IDs attending the class/event, the name of the class/event and a list
        of emails to send the register to. This function is unique to each child class."""
        pass

    def __check(self):
        """This function is executed when the button to send a register is pressed, it requires all of the gathered
        information and passed this to a call to generateRegister"""
        self.__students = []
        # Getting the user input as to whether to send the input to themselves or the class/event teacher(s)
        answers = [self.__vars[0].get(), self.__vars[1].get()]
        if 1 in answers:
            if answers[0] == 1:
                # If send to self is ticked then get the email of the current user
                self.__emails.append(self.__handler.getData("User", self.__master.getUser())[1])
            if answers[1] == 1:
                """If send to teacher(s) is ticked then get the email address for each of the teachers. The IDs of these 
                teachers are found by looking at relevant relationships the class/event matching self.__ID"""
                for value in self.__handler.getForeigns("Teacher" + self.__type, self.__ID):
                    self.__emails.append(self.__handler.getEmail("Teacher", value[1]))
            """Getting the ID of any student records who attend this event/class and using this to get their name and 
            contact number"""
            for value in self.__handler.getForeigns("Student" + self.__type, self.__ID):
                self.__students.append(
                    [self.__searcher.getView("Student", value[1]), self.__handler.getNumber("Student", value[1])])
            self.generateRegister(self.__students, self.__name, self.__emails)
        self.__close()

    def __close(self):
        """This function makes the main master window visible again and destroys this RegisterSender object"""
        self.__master.deiconify()
        self.destroy()


class ClassRegisterSender(RegisterSender):
    """The ClassRegisterSender is a child of a RegisterSender. It is used to generate the register for a Class type record."""
    def __init__(self, master, handler, day, ID, name):
        """This constructor takes the master controller, entityHandler, day of the week of the class, ID of the class and
        name of the class as its input. It initialises the parent class and creates any other GUI elements or
        attributes required."""
        RegisterSender.__init__(self, master, handler, ID, name, "Class")
        # Generating GUI elements (drop-down menus) to pick the month and year the register should be for
        self.__day = day
        self.__days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.__month = tk.StringVar(self)
        self.__month.set("1")
        self.__year = tk.StringVar(self)
        self.__year.set(int(datetime.date.today().year))
        months = []
        years = []
        for i in range(int(datetime.date.today().year), int(datetime.date.today().year)+2):
            years.append(str(i))
        for i in range(1, 13):
            months.append(str(i))
        monthPicker = tk.OptionMenu(self, self.__month, *months)
        monthPicker.grid(row=5, column=0)
        yearPicker = tk.OptionMenu(self, self.__year, *years)
        yearPicker.grid(row=5, column=1)
        master.withdraw()

    def generateRegister(self, students, name, emails):
        """This function takes a list of student IDs attending the class, the name of the class and a list
        of emails to send the register to."""
        # Getting the day of the week of the class an an integer
        day = self.__days.index(self.__day)
        producer = pdfProduction.RegisterGenerator()
        # Make a call to createClassRegister to generate the register
        producer.createClassRegister(int(self.__month.get()), int(self.__year.get()), day, students, name, emails)


class VenueForm(Form):
    """The VenueForm is a child class of the Form parent class. It is used to gather data for a Venue record in the
    database.

    This is similar in structure to a PersonForm so commenting is not repeated unnecessarily"""
    def __init__(self, container, master):
        """This constructor takes the container of the form object and the master constroller as input. It also creates
        all of the GUI elements and any other necessary attributes."""
        Form.__init__(self, container, master)
        labels = ["Name", "Contact Name", "Contact Number", "E-Mail", "Address Line 1", "Address Line 2", "Postcode", "Hourly Cost (£)"]
        self.titleText.set("Venue")
        _row = 102
        count = 0
        for i in labels:
            self.errors.append(tk.StringVar())
            self.errors[count].set("")
            error = tk.Label(self, textvariable=self.errors[count], fg="red")
            error.grid(row=_row-1, column=1, padx=1, pady=0)
            label = tk.Label(self, text=i)
            label.grid(row=_row, column=0, padx=10, pady=10)
            entry = tk.Entry(self, state="normal", disabledforeground="black")
            entry.grid(row=_row, column=1, padx=10, pady=10)
            self.appendEntries(entry)
            _row += 2
            count += 1

    def validate(self):
        """This function is similar to the one of the same name in the PersonForm object and validates the data that
        has been inputted into the form"""
        data = self.getEntries()
        errors = [""] * 8
        errors[0] = validator.validateName(data[0])
        errors[1] = validator.validateName(data[1])
        errors[2] = validator.validateContactNumber(data[2])
        errors[3] = validator.validateEmail(data[3])
        errors[4] = ""
        errors[5] = ""
        errors[6] = validator.validatePostcode(data[6])
        if errors[6] == "":
            errors[6] = validator.presenceCheck(data[6])
        errors[7] = validator.validateCost(data[7])
        validated = True
        for i in errors:
            if i is "":
                pass
            else:
                validated = False
        if validated:
            self.setID(self.updateObject(data))
            self.viewForm(self.getID())
        else:
            count = 0
            for i in errors:
                self.errors[count].set(i)
                count += 1

    def windowTitle(self):
        return "Venue"


class EventRegisterSender(RegisterSender):
    """The EventRegisterSender is a child of a RegisterSender. It is used to generate the register for a Event type record."""
    def __init__(self, master, handler, sDate, eDate, ID, name):
        """This constructor takes the master controller, entityHandler, start and end date of the event, ID of the event and
        name of the event as its input. It initialises the parent class and creates any other attributes required."""
        RegisterSender.__init__(self, master, handler, ID, name, "Event")
        self.__sDate = sDate
        self.__eDate = eDate
        self.__master = master
        self.__handler = handler
        self.__master.withdraw()

    def generateRegister(self, students, name, emails):
        """This function takes a list of student IDs attending the event, the name of the event and a list
        of emails to send the register to."""
        producer = pdfProduction.RegisterGenerator()
        # Make a call to createEventRegister to generate the register and pass the start date, end date and variables passed to this function
        producer.createEventRegister(self.__sDate, self.__eDate, students, name, emails)


class EmailSender(tk.Frame):
    """The EmailSender is a tkinter frame object. It provides the user with a GUI to send an email from the software."""
    def __init__(self, container, master, handler):
        """This constructor takes the container of the EmailSender, master controller and entityHandler as its input. It
        also creates the GUI elements and required attributes."""
        tk.Frame.__init__(self, container)
        # Creating GUI elements
        title = tk.Label(self, text="Email Sender", font=('Arial', 24, 'bold'))
        title.grid(row=0, column=0, columnspan=2)
        rec = tk.Label(self, text="Recipients", font=("Calibri", 15))
        rec.grid(row=1, column=0, padx=10, pady=(10, 3), sticky='W')
        self.__master = master
        self.__searcher = entityHandler.Searcher(handler)
        self.__handler = handler
        self.__box = tk.Listbox(self, selectmode=tk.MULTIPLE, width=25, height=6)
        self.__box.grid(row=10, column=0, rowspan=2, padx=10)
        self.__items = []
        # Creating labels containing possible error messages
        self.__recipientError = tk.Label(self, text="Recipient required", fg="red")
        self.__subjectError = tk.Label(self, text="Subject required", fg="red")
        self.__messageError = tk.Label(self, text="Message required", fg="red")
        addButton = tk.Button(self, text="+", command=self.__add)
        addButton.grid(row=10, column=1, padx=10)
        deleteButton = tk.Button(self, text="X", command=self.__delete)
        deleteButton.grid(row=11, column=1, padx=10)
        subjectLabel = tk.Label(self, text="Subject", font=("Calibri", 15))
        subjectLabel.grid(row=19, columnspan=2, column=0, padx=10, pady=(10, 3), sticky='W')
        self.__subjectEntry = tk.Text(self, height=1, width=40, borderwidth=3, relief="ridge", highlightcolor="white")
        self.__subjectEntry.grid(row=21, columnspan=2, column=0, padx=5)
        messageLabel = tk.Label(self, text="Message", font=("Calibri", 15))
        messageLabel.grid(row=29, columnspan=2, column=0, padx=10, pady=(10, 3), sticky='W')
        self.__messageEntry = tk.Text(self, height=22, width=40, borderwidth=3, relief="ridge", highlightcolor="white")
        self.__messageEntry.grid(row=31, columnspan=2, column=0, padx=5)
        sendButton = tk.Button(self, text="Send", command=self.__send)
        sendButton.grid(row=40, column=0, columnspan=2, pady=(10, 2))

    def __add(self):
        """This function allows the user to add recipients to a listbox"""
        searchWidget = SearchWidget(self.__master)
        # Storing in new the output of a search window with multiple selection mode and providing the list of filters passed below
        new = searchWidget.setMode(tk.MULTIPLE, ["Class", "Event", "Student", "Teacher", "Assistant"])
        for key in new:
            for record in new[key]:
                # Display each returned record from the search as a string in the listbox and store a reference to its ID and type
                self.__items.append([key, record])
                self.__box.insert(tk.END, self.__searcher.getView(key, record))

    def __delete(self):
        """This function allows the user to delete recipients from the list box"""
        indexes = list(self.__box.curselection())
        for index in indexes:
            # Remove any selected records from the box and the reference to them
            self.__box.delete(index, index)
            self.__items.pop(index)

    def __removeErrors(self):
        """This function clears any error messages"""
        self.__recipientError.grid_remove()
        self.__subjectError.grid_remove()
        self.__messageError.grid_remove()

    def __send(self):
        """This function takes all the data that has been entered and, if valid, makes a call for the email to be sent.
        If any data is invalid it displays the necessary error messages."""
        self.__removeErrors()
        subject = self.__subjectEntry.get(0.0, tk.END)
        check = True
        # Checking if there is a subject and displaying error if not
        if len(subject.strip()) == 0:
            self.__subjectError.grid(row=20, pady=1)
            check = False
        message = self.__messageEntry.get(0.0, tk.END)
        # Checking if there is a message and displaying error if not
        if len(message.strip()) == 0:
            self.__messageError.grid(row=30, pady=1)
            check = False
        # Checking if there are any recipients and displaying error if not
        if len(self.__items) == 0:
            self.__recipientError.grid(row=9, pady=1)
            check = False
        if check:
            """If all checks have passed then get the email addresses for all of the records in the list box. If the 
            record is a class or event then iterate through all the students in the class/event and find their email 
            addresses. Do not add duplicate emails."""
            emails = []
            for item in self.__items:
                if item[0] == "Class" or item[0] == "Event":
                    # Get the IDs of all the students in the class/event
                    foreigns = self.__handler.getForeigns("Student"+item[0], item[1])
                    for foreign in foreigns:
                        # Get the email address of the student
                        email = self.__handler.getEmail("Student", foreign[1])
                        if email not in emails and email != "" and email is not None:
                            # If the student has an email address and it is not already in the list of emails then append it
                            emails.append(email)
                else:
                    # Getting the email address of the record
                    email = (self.__handler.getEmail(item[0], item[1]))
                    if email not in emails and email != "" and email is not None:
                        emails.append(email)
            sender = emailSender.emailSender()
            """Make a call to sendEmail and pass the subject, message, None as the attachment and list of emails so that 
            an email is sent with the data the user inputted in this GUI widget"""
            sender.sendEmail(subject, message, None, emails)
            self.__master.showPage("NewRecord")

    def reset(self):
        """This function clears all the fields and resets the EmailSender widget to its default values"""
        self.__items = []
        self.__messageEntry.delete(0.0, tk.END)
        self.__subjectEntry.delete(0.0, tk.END)
        self.__box.delete(0, tk.END)
        self.__removeErrors()

    def windowTitle(self):
        return "Email Sender"


class FinanceCalculator(tk.Frame):
    """The FinanceCalculator is a tkinter frame object. It provides a window to view the financial report for a class
    or event."""
    def __init__(self, container, master):
        """This constructor takes the container of the FinanceCalculator object and master controller as its input. It
        also creates all of the GUI elements and necessary attributes."""
        tk.Frame.__init__(self, container)
        self.__master = master
        self.__handler = master.getEntityHandler()
        self.__searcher = entityHandler.Searcher(self.__handler)
        self.__vars = []
        # Creating the GUI elements
        title = tk.Label(self, text="Finance Calculator", font=('Arial', 24, 'bold'))
        title.grid(row=0, column=0, columnspan=2)
        picker = tk.Button(self, text="Pick Class/Event", command=self.__showCalculation)
        picker.grid(row=10, column=0, columnspan=2, padx=10, pady=10)
        count = 0
        for field in ["Name:", "Outgoings:", "Income:", "Current Student No:", "Required Student No:", "Profitable: "]:
            titleLabel = tk.Label(self, text=field)
            titleLabel.grid(row=count+11, column=0, padx=10, pady=10)
            # Each field consists of a tkinter string variable. This value can be dynamically changed when finance is calculated
            self.__vars.append(tk.StringVar())
            valueLabel = tk.Label(self, textvariable=self.__vars[count])
            if count == 5:
                # Creating a private variable for the profit label as the colour of this will need to be changed
                self.__profitLabel = valueLabel
            valueLabel.grid(row=count+11, column=1, padx=10, pady=10)
            count += 1

    def __showCalculation(self):
        """This function allows the user to select a class or event and then calculates and displays the finance for it"""
        searcher = SearchWidget(self.__master)
        """This stores the value returned from a SearchWidget (with selection mode single and filters for class and event 
        passed) in output"""
        output = searcher.setMode(tk.SINGLE, ["Class", "Event"])
        theKey = None
        data = []
        ID = None
        """This takes the dictionary output and finds the value of the first key in it (the type of record the user picked) 
        and the value of it (the ID of the record the user picks. It then gets the data for this record by calling 
        getData and passing the type and ID."""
        for key in output:
            for record in output[key]:
                theKey = key
                ID = record
                data = self.__handler.getData(key, record)
        name = data[0]
        cost = data[1]
        # Getting the length of the event in hours by finding the difference between the start and end time
        time = (datetime.datetime.strptime((data[5][:2]+":"+data[5][-2:]), '%H:%M') -
                datetime.datetime.strptime((data[4][:2]+":"+data[4][-2:]), '%H:%M')).total_seconds()/3600
        """If the record is of type Event then find the number of days it is over by finding one more than the difference 
        between the start and end date"""
        if theKey == "Event":
            days = (data[7]-data[6]).days + 1
        else:
            # If the record is of type Class then it will only be on one day
            days = 1
        # Getting the ID of the Venue the class/event takes place in by passing getForeigns the type 'Venue' and the class/event ID
        venue = self.__handler.getForeigns(("Venue" + theKey), ID)
        check = False
        # Checking if the class/event actually has an event stored for it
        if len(venue) > 0:
            theVenue = venue[0][1]
            check = True
        if check:
            # If the class/event has a Venue foreign key, then calculate and display the finance for the class/event
            venueCost = self.__handler.getCost(theVenue) # Getting the hourly hire cost of the venue
            # Getting the number of hours the class/event takes place over by multipying the period of time by number of days
            period = time * days
            """Getting the number of teacher and assistants in the class by finding the number of Teacher(Class/Event) 
            and Assistant(Class/Event) relationships that exist involving the class/event matching ID."""
            teacherNo = len(self.__handler.getForeigns(("Teacher" + theKey), ID))
            assistantNo = len(self.__handler.getForeigns(("Assistant" + theKey), ID))
            """Calculating the outgoings by the sum of the product of the number of teachers and teacher wage; the product 
            of the number of assistants and assistant wage along with the product of the number of hours the class/event 
            is over and the hourly venue hire cost."""
            outgoings = (Decimal(data[2]) * teacherNo) + (Decimal(data[3]) * assistantNo) + (Decimal(venueCost) * Decimal(period))
            # Round up the outgoings as a Decimal object to two decimal places
            outgoingsFormatted = "£" + str(outgoings.quantize(Decimal('0.01'), rounding="ROUND_UP"))
            # Get the number of students required by a negative floor division (thus ceiling) of the outgoings by the class/event cost
            requiredNo = int(-(-float(outgoings)//float(cost)))
            """Get the number of students in the class by finding the number of Student(Class/Event) relationships 
            that exist in the database involving the event/class matching ID."""
            noStudents = len(self.__handler.getForeigns(("Student" + theKey), ID))
            # Find the income of the class/event by the product of the number of students and class cost
            income = noStudents * Decimal(cost)
            # Display all of the data that has been calculated
            self.__vars[0].set(name)
            self.__vars[1].set(outgoingsFormatted)
            # Display the income as string form of a python Decimal object rounded to two decimal places
            self.__vars[2].set("£" + str(income.quantize(Decimal('0.01'), rounding="ROUND_UP")))
            self.__vars[3].set(str(noStudents))
            self.__vars[4].set(str(requiredNo))
            """If there are more students than required then set the profitable label to 'Yes' and make it green. 
            Otherwise set it to 'No' and make it red"""
            if noStudents >= requiredNo:
                self.__vars[5].set("Yes")
                self.__profitLabel.config(fg="lime green")
            else:
                self.__vars[5].set("No")
                self.__profitLabel.config(fg="red")

    def reset(self):
        """This function resets all of the tkinter string variables in self.__vars (the text content of the labels) to
        blank strings."""
        for value in self.__vars:
            value.set("")

    def windowTitle(self):
        return "Finance Calculator"


class Home(tk.Frame):
    """Home is a tkinter frame object, it provides the GUI window for the home page of the software and the function to
    gather the data to be shown in it."""
    def __init__(self, container, master):
        """This constructor takes the container of the Home object and the master controller as input. It also creates
        the necessary GUI elements and private attributes."""
        tk.Frame.__init__(self, container)
        self.__handler = master.getEntityHandler()
        self.__searcher = entityHandler.Searcher(self.__handler)
        self.__labels = []
        # Creating the GUI elements
        title = tk.Label(self, font=('Arial', 24, 'bold'), text="Dance Admin System")
        title.grid(row=0, padx=10, pady=(10, 0), columnspan=2)
        homeTitle = tk.Label(self, font=('Arial', 22), text="Home")
        homeTitle.grid(row=1, padx=10, pady=(10, 0), columnspan=2)
        todayLabel = tk.Label(self, text="Today's Classes", font=('TkDefaultFont', 13, 'bold'))
        todayLabel.grid(row=3, column=0, padx=10, sticky='w')
        eventLabel = tk.Label(self, text="Upcoming Events", font=('TkDefaultFont', 13, 'bold'))
        eventLabel.grid(row=3, column=1, padx=10, sticky='w')
        # Resetting the Home screen and then populating it with data
        self.__reset()
        self.set()

    def set(self):
        """This function gets the classes that take place on the current data and event that takes place in the current
        month and displays them on the home screen using labels."""
        classList = self.__handler.todayClasses()  # Getting the classes on the current day and storing their IDs in a list
        _row = 10
        for aclass in classList:
            # Getting the data values for aclass by calling getData and passing it the ID 'aclass'
            values = self.__handler.getData("Class", aclass)
            # Using the foreign key for the Venue of aclass and finding the Venue Class relationship that involves it
            venueID = self.__handler.getForeigns("VenueClass", aclass)[0][1]
            # Finding the name of the Venue by passing getData its ID
            venue = self.__handler.getData("Venue", venueID)[0]
            # Displaying the name of the class, the venue and date of the class
            string = (values[0] + " | " + venue + " | " + values[1])
            label = tk.Label(self, text=string)
            label.grid(column=0, row=_row, padx=10, sticky='w')
            # Keep a track of the label by appending it to a list
            self.__labels.append(label)
            _row += 1
        _row = 10
        eventList = self.__handler.monthEvents()  # Getting the event in the current month and storing their IDs in a list
        for event in eventList:
            # Getting the data values for event by calling getData and passing it the ID 'event'
            values = self.__handler.getData("Event", event)
            venueID = self.__handler.getForeigns("VenueEvent", event)[0][1]
            venue = self.__handler.getData("Venue", venueID)[0]
            string = (values[0] + " | " + venue + " | " + str(values[6]))
            label = tk.Label(self, text=string)
            label.grid(column=1, row=_row, padx=10, sticky='w')
            self.__labels.append(label)
            _row += 1

    def __reset(self):
        """This function clears the Home screen of any classes or event (i.e. it resets it to its default values)"""
        for label in self.__labels:
            label.grid_remove()
        self.__labels = []

    def windowTitle(self):
        return "Home"


class Login(tk.Toplevel):
    """The Login class is a tkinter Toplevel object (a window that appears about the rest of the tkinter window) and it
    facilitates a secure login into the system and determining the current account"""
    def __init__(self, master):
        """This constructor takes the master controller as the input. It also creates all of required GUI elements
        along with any necessary attributes."""
        tk.Toplevel.__init__(self)
        self.__master = master
        # Set the window title
        tk.Tk.wm_title(self, "Login")
        # Create the GUI elements
        title = tk.Label(self, font=('Arial', 24, 'bold'), text="Dance Admin System")
        title.grid(row=0, padx=10, pady=(10, 0))
        usernameLabel = tk.Label(self, text="Username")
        usernameLabel.grid(row=1, padx=10, pady=(10,0))
        self.__error = tk.StringVar()
        errorLabel = tk.Label(self, textvariable=self.__error, fg="red")
        errorLabel.grid(row=5, pady=0, padx=1)
        self.__usernameEntry = tk.Entry(self)
        self.__usernameEntry.grid(row=2, pady=(2, 0))
        passwordLabel = tk.Label(self, text="Password")
        passwordLabel.grid(row=3, padx=10, pady=(10, 0))
        # Ensure the password entry box only shows a '•' symbol
        self.__passwordEntry = tk.Entry(self, show="•")
        self.__passwordEntry.grid(row=4, pady=(2, 2))
        loginButton = tk.Button(self, text="Login", command=self.__login)
        loginButton.grid(row=6, pady=(0, 10))
        # If the window is closed the call the master function fail (to stop the program)
        self.protocol("WM_DELETE_WINDOW", self.__master.fail)
        self.__count = 0
        # Create a PasswordManager instance and pass it the master's entityHandler
        self.__passwordManager = passwordManagememt.PasswordManager(self.__master.getEntityHandler())
        # Hide the main master window
        self.__master.withdraw()

    def __close(self):
        """This function closes the current window by destroying the Login object and makes the main master window
        visible again"""
        self.__master.deiconify()
        self.destroy()

    def __login(self):
        """This function checks the user input against valid data from the database and allows access to the system if
        it is valid. If there are 5 incorrect attempts it quits the software."""
        if self.__count < 5:
            # Getting the user entry
            username = self.__usernameEntry.get()
            password = self.__passwordEntry.get()
            try:
                # Comparing the password and username to data stored in the database by making a call to loginCheck
                self.__passwordManager.loginCheck(username, password)
                # Storing the value returned by a call to getUserAccess (having passed username) in the variable accessLevel
                accessLevel = self.__master.getEntityHandler().getUserAccess(username)
                # Setting the master controller's access level and current user account
                self.__master.setAccessLevel(accessLevel)
                self.__master.setUser(username)
                self.__close()
            except passwordManagememt.WrongPasswordException as e:
                # Excepting a wrong password exception and displaying the error message produced to the user
                self.__error.set(e)
                # Incrementing count due to an incorrect attempt
                self.__count += 1
                # Clearing the password entry
                self.__passwordEntry.delete(0, tk.END)
            except passwordManagememt.UsernameInvalidException as e:
                # Excepting a non-existent username exception and displaying the error message produced to the user
                self.__count += 1
                self.__error.set(e)
                self.__passwordEntry.delete(0, tk.END)
        else:
            # If 5 incorrect attempts have occurred then call the fail function to quite the software
            self.__master.fail()


class AccountsPage(tk.Frame):
    """The AccountsPage tkinter frame object is for navigating to all the accounts related sections of the software"""
    def __init__(self, container, master):
        """This constructor takes the container of the widget and the master controller as the input. It also creates
        all of the buttons and GUI elements required along with any necessary attributes."""
        self.__master = master
        tk.Frame.__init__(self, container)
        addButton = tk.Button(self, text="Create Account", command=lambda: [self.__master.showPage("UserForm"),
                                                                            self.__master.createCurrentPage()])
        addButton.grid(row=2, column=0, padx=10, pady=10)
        viewButton = tk.Button(self, text="View Account", command=lambda: [self.__master.showPage("UserAccountList"),
                                                                           self.__master.getCurrentPage().getCurrent()])
        viewButton.grid(row=2, column=1, padx=10, pady=10)
        title = tk.Label(self, font=('Arial', 24, 'bold'), text="Accounts")
        title.grid(row=0, padx=10, pady=(10, 0), columnspan=3)

    def windowTitle(self):
        return "Accounts Page"

# This creates an instance of the main tkinter root
app = GUIController()
# Ensuring that the tkinter window cannot be resized (as this is handled automatically)
app.resizable(0, 0)
app.mainloop()
