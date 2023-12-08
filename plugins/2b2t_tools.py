import lodestone
from rich.console import Console
from rich.progress import Progress
import ast
import inspect
from javascript import require
import math

class plugin:
    """
    Mine a chunk
    """
    def __init__(self, bot: lodestone.Bot):
        "The injection method"
        self.bot:lodestone.Bot = bot
        self.console = Console(force_terminal=True)
        self.code = inspect.getsource(inspect.getmodule(self.__class__))
        self.tree = ast.parse(self.code)
        self.events = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'on':
                event = node.args[0].s
                self.events.append(event)
        events_loaded = list(bot.loaded_events.keys())
        events_loaded.append(self.events) # add the event to the list
        bot.emit('event_loaded', *events_loaded)
        plugins_loaded = list(bot.loaded_plugins.keys())
        plugins_loaded.append(self.__class__.__name__) # add the plugin to the list
        bot.emit('plugin_loaded', *plugins_loaded)
        self.building_up = False
        # self.bot.mine_chunk:callable = self.start
    def start(self):
        pass