"""
chatbot constants
"""
import logging
import os

"""
application veriosn
"""
APP_VERSION = '2.5'

"""
application name
"""
APP_NAME = 'chatbot'

"""
log level
"""
LOG_LEVEL = logging.INFO

"""
log file name
"""
LOG_FILE_NAME = 'chatbot.log'

"""
The maximum amount of similarity between two statement that is required
before the search process is halted. The search for a matching statement
will continue until a statement with a greater than or equal similarity
is found or the search set is exhausted.
"""
MAXIMUM_SIMILARITY_THRESHOLD = 0.85

"""
The minimum amount of similarity between two statement, below this value, 
the robot cannot answer questions from the user.
"""
MINIMUM_SIMILARITY_THRESHOLD = 0.2

"""
the number of answers each adapter has to answer
"""
NUMBER_OF_ANSWERS = 5


"""
project path,build paths inside the project like this: os.path.join(BASE_DIR, ...)
"""
PROJECT_DIR_PATH = os.path.dirname((os.path.abspath(__file__)))

"""
database address
"""
DEFAULT_DATABASE_URI = 'sqlite:///db.sqlite3'

"""
Get the maximum number of errors allowed by the context parameter. 
If the number of times exceeds, the problem is terminated.
"""
CONTEXT_PARAMETER_MAX_ERROR_COUNT = 3
