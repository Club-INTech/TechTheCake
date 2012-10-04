from threading import Lock

class Mutex():
    """
    Classe de mutex permettant de factoriser leur utilisation dans des blocs with
    """
    def __init__(self):
        self.mutex = Lock()
        
    def __enter__(self):
        self.mutex.acquire()
    
    def __exit__(self, type, value, tb):
        self.mutex.release()