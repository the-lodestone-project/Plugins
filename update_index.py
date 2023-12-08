import glob
import os
import json

with open("plugin_index.json", "r+") as plugin_index:
    plugin_data = json.load(plugin_index)
    
    os.chdir("plugins")
    
    for plugin in glob.glob("*.py"):
        if "__init__" not in plugin:
            
            
            name = plugin.replace(".py", "")
            
            if name not in plugin_data:
                print(plugin)
                plugin_data[name] = {
                    "name": name,  
                    "description": "No description provided",
                    "author": "",
                    "version": "1.0",
                    "dependencies": [],
                    "commands": [],
                    "files": [plugin],
                }
            
    plugin_index.seek(0) 
    json.dump(plugin_data, plugin_index, indent=4)
    plugin_index.truncate()
