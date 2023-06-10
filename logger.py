from datetime import datetime

class Logger:
    """
    The Logger class provides static methods to log error and success messages.
    """
    
    @staticmethod
    def e(msg):
        """
        Logs an error message.

        Parameters:
        - msg (str): The error message to be logged.
        """
        print(f"[{datetime.now().time().strftime('%H:%M:%S')}][Error]: {msg}")

    @staticmethod
    def s(msg):
        """
        Logs a success message.

        Parameters:
        - msg (str): The success message to be logged.
        """
        print(f"[{datetime.now().time().strftime('%H:%M:%S')}][Success]: {msg}")
        
    @staticmethod
    def i(msg):
        """
        Logs a info message.

        Parameters:
        - msg (str): The info message to be logged.
        """
        print(f"[{datetime.now().time().strftime('%H:%M:%S')}][Info]: {msg}")
