class Table:
    def __init__(self,config,log):
        self.config = config
        self.log = log

class TableSimulateur(Table):
    def __init__(self,config,log):
        Table.__init__(self,config,log)