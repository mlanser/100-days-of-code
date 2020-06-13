import os
from tinydb import TinyDB
from abc import abstractmethod

from cement import App, Interface, Handler, TestApp, init_defaults

from cement.utils import fs
from cement.core.exc import CaughtSignal

from .core.exc import TodoError
from .controllers.base import Base
from .controllers.items import Items


# ===============================================
#               I N T E R F A C E S
# ===============================================
class GreetingInterface(Interface):
    class Meta:
        interface = 'greeting'

    @abstractmethod
    def _get_greeting(self):
        """
        Get a greeting message for the end-user.

        Returns:
            greeting (str): The greeting string to present to
                the end-user.
        """
        pass

    @abstractmethod
    def greet(self):
        """
        Display a greeting message for the end-user.

        Returns: None
        """
        pass

    
    
# ===============================================
#                 H A N D L E R S
# ===============================================
class GreetingHandler(GreetingInterface, Handler):

    def greet(self, name=None):
        self.app.log.debug('about to greet end-user')
        msg = self._get_greeting(name)
        assert isinstance(msg, str), "The message is not a string!"
        print('\n-----\n{}\n-----'.format(msg))


class Hello(GreetingHandler):
    class Meta:
        label = 'hello'

    def _get_greeting(self, name):
        msg = 'Hello {}!'.format(str(name)) if name != None else 'Hi there!'
        return  msg  


class Goodbye(GreetingHandler):
    class Meta:
        label = 'goodbye'

    def _get_greeting(self, name):
        msg = 'Goodbye {}!'.format(str(name)) if name != None else 'See ya!'
        return msg
    
    
    


# ===============================================
#        M I S C .   E X T E N S I O N S
# ===============================================
def extend_tinydb(app):
    #app.log.info('extending todo application with tinydb')
    db_file = app.config.get('todo', 'db_file')
    
    # ensure that we expand the full path
    db_file = fs.abspath(db_file)
    #app.log.info('tinydb database file is: %s' % db_file)
    
    # ensure our parent directory exists
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.extend('db', TinyDB(db_file))


def my_hook_function(app):
    print('Hooky Mac Hookster!')

    
def another_hook_function():
    return 'Boink!'


def one_more_function():
    return 'Second boink!'

    
    
    
# ===============================================
#   C O N F I G U R A T I O N   D E F A U L T S
# ===============================================
CONFIG = init_defaults('todo', 'log.logging')
CONFIG['todo']['db_file'] = '~/.todo/db.json'
CONFIG['todo']['email'] = 'martinlanser@gmail.com'
CONFIG['log.logging']['level'] = 'info'




# ===============================================
#   M A I N   A P P L I C A T I O N   C L A S S
# ===============================================
class Todo(App):
    """My totally awesome TODO application."""

    class Meta:
        label = 'todo'

        define_hooks = [
            'my_example_hook',
            'my_second_hook',
        ]
        
        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # configuration handler
        #config_handler = 'yaml'

        # configuration file suffix
        #config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers, hooks, and interfaces
        handlers = [
            Base,
            Items,
            Hello,
            Goodbye,
        ]
        
        hooks = [
            ('pre_setup', my_hook_function),
            ('post_setup', extend_tinydb),
            ('my_example_hook', another_hook_function),
        ]
        
        interfaces = [
            GreetingInterface,
        ]        



        
# ===============================================
#   A P P L I C A T I O N   T E S T   C L A S S
# ===============================================
class TodoTest(TestApp,Todo):
    """A sub-class of Todo that is better suited for testing."""

    class Meta:
        label = 'todo'



        
# ===============================================
#         M A I N   A P P L I C A T I O N
# ===============================================
def main():
    with Todo() as app:
        app.hook.register('my_second_hook', one_more_function)
        
        print(app.config.get('todo', 'db_file'))
        print(app.config.get('todo', 'email'))
        print(app.config.keys('todo'))
        
        try:
            app.handler.get('greeting', 'hello', setup=True).greet('Martin')
            
            for res in app.hook.run('my_example_hook'):
                print(res)
            for res in app.hook.run('my_second_hook'):
                print(res)
                
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except TodoError as e:
            print('TodoError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0
            
        finally:    
            app.handler.get('greeting', 'goodbye', setup=True).greet()

if __name__ == '__main__':
    main()
