import bcrypt


class WrongPasswordException(Exception):
    # This exception is called when a password and username don't match
    def __init__(self, error):
        # This constructor for the exception takes an error message as its input
        self.__error = error

    def __str__(self):
        # This function returns a string representation of the exception in the form of the error message string
        return self.__error


class UsernameInvalidException(Exception):
    # This exception is called when a non-existent username is entered
    def __init__(self, error):
        # This constructor for the exception takes an error message as its input
        self.__error = error

    def __str__(self):
        # This function returns a string representation of the exception in the form of the error message string
        return self.__error


class PasswordManager(object):
    """This class manages all the password/user account related functionality. It acts an interface to the bcrypt module
    for all other parts of my code"""
    def __init__(self, handler):
        # This constructor takes the entityHandler as its input and stores it as a private variable
        self.__handler = handler
        """Creating a private variable containing a dictionary of all the usernames in the system and their User object,
        as found by a call to an entityHandler function"""
        self.__passwords = self.__handler.getUsers()

    def loginCheck(self, username, password):
        """This function takes a username and a password and determines if they are both valid. If there is any invalid
        data at any point, a relevant exception is raised. If the input is valid it returns the variable username passed
        to it.

        This if statement checks that the username exists"""
        if username in self.__passwords.keys():
            # Getting the password relating to the inputted username if it exists (by using username as dictionary key)
            storedPassword = self.__passwords[username].getPassword()
            """ Using bcrypt to check if the stored password hash matches a hash of the inputted password -> i.e. checking 
            if the password is correct"""
            if storedPassword == bcrypt.hashpw(password.encode('utf8'), storedPassword):
                return username
            else:
                # Raising an exception as the username and password don't match
                raise WrongPasswordException("Invalid Password")
        else:
            # Raising an exception as the username doesn't exist
            raise UsernameInvalidException("Invalid Username")

    def encrypt(self, password):
        """This function takes a password as plaintext password string as its input and returns the same password in a
        hashed form, after utilising the bcrypt module"""
        # Generating a random salt to be included as input in the hashing - to avoid patterns and protect from a dictionary attack
        salt = bcrypt.gensalt()
        # Using bcrypt to hash the password and salt
        password = bcrypt.hashpw(password.encode('utf8'), salt)
        return password
