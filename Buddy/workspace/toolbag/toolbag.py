import os
import json
import importlib.util
class Toolbag:
    def __init__(self):
        self.toolbag = []
        self.load_tools()
    def load_tools(self):
        tools_path = os.path.join(os.getcwd(), 'workspace', 'tools')
        with open(os.path.join('workspace/toolbag/tools.json'), 'r') as f:
            tool_metadata = json.load(f)
        for tool in tool_metadata:
            module_name = tool['class']  # remove .py extension
            module_file = f'{module_name}.py'
            module_path = os.path.join(tools_path, module_file)
            print(module_path)
            if os.path.exists(module_path):
                # Load the module from file and import it
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Initialize the class (assuming it has the same name as the file)
                cls = getattr(module, module_name)
                tool_instance = cls()

                # Add the tool instance to the toolbag
                self.toolbag.append(tool)
            else:
                print(f'Warning: Tool module file {module_file} not found.')