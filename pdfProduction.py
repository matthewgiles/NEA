import datetime as dt
import calendar
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import emailSender


class RegisterGenerator(object):
    """This class is used for the generation of a register by interfacing with the necessary modules and it ensures that
    it is subsequently sent"""
    def __init__(self):
        # This is a list of default column titles for any register
        self.__columnTitles = ["Name", "Contact Number"]
        self.__data = []
        # Creating an instance of an emailSender so that a generated register can be sent
        self.__sender = emailSender.emailSender()
        # Creating a default style for text in a register
        self.__style = ParagraphStyle(fontSize=15, name="Title", spaceAfter=20, alignment=TA_CENTER)

    def __reset(self):
        # This function resets the private class variables to their initial values
        self.__columnTitles = ["Name", "Contact Number"]
        self.__data = []

    def __generate(self, docName, emails, name, period):
        """This function takes the filename of a document, a list of emails for it to be sent to, the name of the class
        or event the register is for and the period of time the register is for"""
        # Generating a blank A4 pdf
        doc = SimpleDocTemplate(docName, pagesize=A4, rightMargin=25, leftMargin=25)
        elements = []
        # Adding an "Other" column heading to the list of headings
        self.__data[0].append("   Other   ")
        # Generating a table containing the contents of self.__data with the first items being row 1 etc.
        table = Table(self.__data)
        # Setting the borders of the table and the style of each row/column
        table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                                    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                                   ('FONT', (0, 0), (len(self.__data[0])-1, 0), 'Helvetica-Bold')]))
        # Appending a paragraph to the document with the same name as the document without .pdf and in the class defined style
        elements.append(Paragraph(docName.strip(".pdf"), style=self.__style))
        # Appending the generated table to the document
        elements.append(table)
        doc.build(elements)
        # Creating a message to be sent in the email with the register consisting of all the relevant details
        message = "Hi,\nAttached is the register for " + name + " to cover " + period + ".\nThank you, from Steph."
        """Calling sendEmail of the class self.__sender instance, with: a subject of the class/event name followed by register;
        the message above; the attachment of the document filename and the list of emails passed to this function"""
        self.__sender.sendEmail(name + " Register", message, docName, emails)


    def createClassRegister(self, month, year, day, students, className, emails):
        """This function receives the month and year of the class, the day of the week it is on as an integer, a list
        of students' names and numbers who are attending it, its name, and a list of emails for the register to be sent
        to. It then calculates the necessary information for a call to __generate that will produce the actual register"""
        self.__reset()
        # Getting the day of the week as an integer that the first day the month of the event is
        firstDay = dt.datetime(year, month, 1).weekday()
        # The following finds the date of the first class in the month
        if firstDay > day:
            aclass = 8 - (firstDay - day)
        else:
            aclass = 1 + (day - firstDay)
        classes = []
        # Converting the month of the class into a string form, adding a leading zero if the month is only one digit
        if month < 10:
            amonth = "0" + str(month)
        else:
            amonth = str(month)
        """The following finds all the dates of a class in a month by taking the start date and adding on seven days
        each iteration of the while loop - this continues until doing so goes outside the range of the month. Each date
        of the class is appended to a list called classes in a desired format"""
        while aclass <= calendar.monthrange(year, month)[1]:
            if aclass < 10:
                aclass = "0" + str(aclass)
            classes.append(str(aclass)+"/"+str(amonth)+"/"+str(year))
            aclass = int(aclass) + 7
        self.__columnTitles.extend(classes)
        # Appending all of the column titles to data as these will form the first row of the table in the pdf
        self.__data.append(self.__columnTitles)
        docName = className + " " + calendar.month_name[int(month)] + " " + str(year) + " Register.pdf"
        """For each student in students, append a list containing their name and number followed by as many empty strings
        as remaining column titles to self.__data as each of these forms a new row in the table"""
        for student in students:
            alist = [student[0], student[1]]
            for x in range(0, len(self.__columnTitles)-2):
                alist.append(" ")
            self.__data.append(alist)
        """Make a call to the generate function to produce the register with all the data that has now been calculated.
        Pass the name of the document, the list of emails to send it to, the class name, and the month and year the register
        is for"""
        self.__generate(docName, emails, className, (calendar.month_name[int(month)] + " " + str(year)))


    def createEventRegister(self, sDate, eDate, students, eventName, emails):
        """This function takes the start and end date of an event, along with the student's names and numbers who are
        attending it, and the name of the event and list of emails for the generated register to be sent to"""
        docName = eventName + " Register.pdf"
        self.__reset()
        """For each of the number of days of the event (which is one more than the difference in start and end date), append
        a new column heading for that day number"""
        for x in range(1, (eDate-sDate).days + 2):
            self.__columnTitles.append("Day " + str(x))
        self.__data.append(self.__columnTitles)
        # This following is the same as in the above function
        for student in students:
            alist = [student[0], student[1]]
            for x in range(0, len(self.__columnTitles)-2):
                alist.append(" ")
            self.__data.append(alist)
        """Make a call to the generate function to produce the register with all the data that has now been calculated.
        Pass the name of the document, the list of emails to send it to, the event name, and the period of dates the
        event is over in string form"""
        self.__generate(docName, emails, eventName, ("from " + sDate.strftime("%d/%m/%Y") + " to " + eDate.strftime("%d/%m/%Y")))

