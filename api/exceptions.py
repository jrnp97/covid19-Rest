""" Module to define custom exceptions """


class AlreadyProcessedFile(Exception):
    """ Exception to describe that a file was already imported on database """


class HeaderNotIdentifier(Exception):
    """ Exception to describe that was not completely identified headers of one file """


class DateFormatNotIdentifier(Exception):
    """ Exception describing that identify date format for string was not successfully """
