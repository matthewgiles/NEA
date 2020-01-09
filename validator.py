import re


def validateEmail(string):
    """This function takes a string as its input and returns a string 'message' which determines whether or not the input
    is a valid email"""
    message = ""
    # Create a regular expression matching a valid email
    pattern = re.compile("^([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*@[a-zA-Z0-9]+\.[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$")
    # If the string does not match the regular expression set 'message' to a corresponding error
    if not pattern.match(string):
        message = "This is not a valid E-Mail address"
    return message


def validatePostcode(string):
    """This function takes a string as its input and returns a string 'message' which determines whether or not the input
    is a valid postcode"""
    message = ""
    # Create a regular expression matching a valid postcode
    pattern = re.compile("^([a-zA-Z][a-zA-Z_]?[0-9][0-9]?[/ /]?[0-9][a-zA-Z]{2})?$")
    # If the string does not match the regular expression set 'message' to a corresponding error
    if not pattern.match(string):
        message = "This is not a valid postcode"
    return message


def validateCost(string):
    """This function takes a string as its input and returns a string 'message' which determines whether or not the input
    is a valid cost"""
    message = ""
    pattern = re.compile("^[0-9]*((.)[0-9]{2})?$")
    if not pattern.match(string):
        message = "This is not a valid cost"
    # A presence check is required, if the string is blank then set 'message' to a corresponding error
    if string == "":
        message = "Field required"
    return message


def validateContactNumber(string):
    """This function takes a string as its input and returns a string 'message' which determines whether or not the input
    is a valid contact number"""
    message = ""
    # A presence check is required, if the string is blank then set 'message' to a corresponding error
    if string == "":
        message = "Field required"
        return message
    # If the length of the string is not 11 digits (the length of a phone number) then it set 'message' to an error
    if len(string) != 11:
        message = "Number should be 11 digits long"
    # If the string contains characters other than a number then it is not valid so set 'message' to an error
    if not string.isdigit():
        message = "This is not a number"
    return message


def validateName(string):
    """This function takes a string as its input and returns a string 'message' which determines whether or not the input
    is a valid name"""
    message = ""
    if string == "":
        message = "Field required"
    # If the string is longer than 30 characters then it is too long so set 'message' to a corresponding error
    if len(string) > 30:
        message = "Name too long"
    return message


def presenceCheck(string):
    """This function takes a string as its input and returns a string 'message' which determines whether or not the input
    is a valid presence check"""
    message = ""
    # If the string is blank then set 'message' to a corresponding error
    if string == "":
        message = "Field required"
    return message