from container import *
from threading import Thread

container = Container()
script = container.get_service(ScriptBougies)
log = container.get_service(Log)


#thread_MAJ = threading.Thread(None, Thread_MAJ.boucle(), None, (), {})
#thread_MAJ.start()