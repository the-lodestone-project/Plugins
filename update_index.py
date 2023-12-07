import glob
import os
import json

with open("plugin_index.json", "r+") as plugin_index:

    plugin_data = json.load(plugin_index)

    os.chdir("plugins")

    for plugin in glob.glob("*.py"):
        if "__init__" not in plugin:
            print(plugin)
            name = plugin.replace(".py", "")
            plugin_data[name] = {
                "name": name,
                "description": "",
                "author": "", 
                "version": "",
                "dependencies": [],
                "commands": [],
                "files": [plugin],
            }

    plugin_index.seek(0)
    json.dump(plugin_data, plugin_index, indent=4)
    plugin_index.truncate()

print(plugin_index)