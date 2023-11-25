from codingAgent import Manager, CodingManager, DBManager
from workspace.tools.base import AgentTool
from workspace.toolbag.toolbag import Toolbag
from workspace.tools.codingagenttools import codingagenttools
import importlib


def main():
    codingmanager = codingagenttools()
    print(codingmanager.view_workspace())
    manager = Manager(agent_classes=[CodingManager, DBManager])
    tools = []
    toolbag = Toolbag()
    for tool in toolbag.toolbag:
        tools.append(tool)
    for tool in tools:
        module_name = tool['class']
        function_name = tool['func'].split('.')[-1] # function name
        # load the module
        module = importlib.import_module(f"workspace.tools.{module_name}")
        classe = getattr(module, module_name)
        instance = classe()
        func = getattr(instance, function_name)
        #print(tool)
        tool_instance = AgentTool(
            name=tool['name'],
            func=func,
            args=tool['args'],
            description=tool['description'],
            user_permission_required=tool['user_permission_required']
        )
        print(tool_instance)
        manager.procedural_memory.memorize_tools([tool_instance])
    try:
        while True:
            manager.run()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Exiting...")
    finally:
        print("Performing cleanup...")
        # ... (any other cleanup you might need)

    print("Application exited.")




if __name__ == "__main__":
    main()

