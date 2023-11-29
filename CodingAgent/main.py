from codingAgent import CodingAgent
from codingAgentclasses import code_gen, code_mod, code_run, test_unit_gen, test_unit_mod, test_unit_run, test_integration_gen, test_integration_mod, test_integration_run, test_e2e_gen, test_e2e_mod, test_e2e_run
from workspace.tools.base import AgentTool
from workspace.toolbag.toolbag import Toolbag
from workspace.tools.codingagenttools import codingagenttools
import importlib
import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    codingmanager = codingagenttools()
    print(codingmanager.view_workspace())
    #codingagent = CodingAgent(agent_classes=[code_gen, code_mod, code_run, test_unit_gen, test_unit_mod, test_unit_run, test_integration_gen, test_integration_mod, test_integration_run, test_e2e_gen, test_e2e_mod, test_e2e_run ])
    codingagent = CodingAgent()
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
        codingagent.procedural_memory.memorize_tools([tool_instance])
    try:
        while True:
            codingagent.run()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Exiting...")
    finally:
        print("Performing cleanup...")
        # ... (any other cleanup you might need)

    print("Application exited.")




if __name__ == "__main__":
    main()

