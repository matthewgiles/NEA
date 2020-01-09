import pickle
import os


class FileManager(object):
    """"This class acts as an interface for the rest of my code to access the contents of any pickled files"""
    def saveFile(self, filename, data):
        """"This function takes a filename and some data to store in a file and does so in a pickled form"""
        file = open(filename, 'wb')
        pickle.dump(data, file)
        file.close()

    def loadFile(self, filename):
        """The function takes a filename and attempts to return the contents of that file, if no such file is found then
        a FileNotFoundError is raised"""
        if os.path.exists(filename):
            file = open(filename, 'rb')
            # Getting the contents of a pickled file and storing them in data
            data = pickle.load(file)
            file.close()
            return data
        else:
            raise FileNotFoundError
