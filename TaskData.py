global example_description = """
This is an example descrip-
tion text written to evaluate
the ability of a 254 charact-
ers long string to represent
enough information about a
cybercognitive entity such as
Task object within the
TSW-1.py application.
It seems almost enough.
"""	
from Storage import Storage
class TaskData():
    global example_description
    def __init__(self,task_item=None, storage=None):
		""" 
		    This class is designed for 
        development and implementation of 
        storage for information that is related 
        to a Task object.
            We want new fields in database, and probably new table for 
        storing data of particular tasks.
        
        Arguments:
		    storage
				a Storage object that is used within the application.
				If not - create new db interface, which must be bad for
				this kind of objects.
        Task data must have 
        """
        if not task_item:
            #there is no task argument given?
            print('WHAT')
            #logger.log('CHAOTIC', 'No task_item given to TaskData constructor!')
            sys.exit()
        else:
            task_uuid=task_item.dict['uuid']
            #task_uuid=task_item.__getattribute__('uuid')
			#task_uuid = task_item.uuid
			
        if not storage:
            self.storage = Storage()
        else
            self.storage = storage
	    #maybe check if a db-record with a description has been already created.
        self.task_item.description 



infos = """
This is an example descrip-
tion text written to evaluate
the ability of a 254 charact-
ers long string to represent
enough information about a
cybercognitive entity such as
Task object within the
TSW-1.py application.
It seems almost enough."""