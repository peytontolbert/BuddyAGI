class code_gen:
    CODE_GEN_SYSTEMPROMPT = """
[RULE]
As a 'code_gen' agent, your role is to generate new code snippets based on the given task. Use the available tools effectively to create code that meets the task requirements.

[YOUR TASK]
{task_description}

[AVAILABLE TOOLS]
- CodeGenerator: Generates new code snippets. Args: [language, requirements]
- SyntaxChecker: Checks the syntax of generated code. Args: [code]
- ...

[RESPONSE FORMAT]
Provide your response in the JSON format with the selected tool and necessary arguments:
{
    "tool_name": "Tool to use for code generation",
    "args": {
        "arg1": "value1",
        "arg2": "value2"
        // Additional arguments as needed
    }
}
"""
    def __init__(self):
        self.name = "code_gen"
        self.func = self.code_gen
        self.args = ["code"]
        self.description = "Generates code"
        self.user_permission_required = False


    def code_gen(self, code):
        return code_gen(code)
class code_mod:
    CODE_MOD_SYSTEMPROMPT = """
[RULE]
As a 'code_mod' agent, your role is to generate new code snippets based on the given task and existing code provided. Use the available tools effectively to create code that meets the task requirements.

[YOUR TASK]
{task_description}

[AVAILABLE TOOLS]
{toolinfo}

[RESPONSE FORMAT]
Provide your response in the JSON format with the selected tool and necessary arguments:
{
    "tool_name": "Tool to use for code generation",
    "args": {
        "arg1": "value1",
        "arg2": "value2"
        // Additional arguments as needed
    }
}
"""
    def __init__(self):
        self.name = "code_mod"
        self.func = self.code_mod
        self.args = ["code"]
        self.description = "Modifies code"
        self.user_permission_required = False

    def code_mod(self, code, task):
        prompt = self.code_modprompt(code)
        systemprompt = self.CODE_MOD_SYSTEMPROMPT.format(task_description=task.description, toolinfo=task.toolinfo)
        messages = [{"role": "system", "content": systemprompt}, {"role": "user", "content": prompt}]
        result = self.gpt.chat_with_gpt3(messages)

    def code_modprompt(self, code):
        template = """[CODE TO MODIFY]
        {code}"""
        prompt = template.format(code=code)
        return code_mod(prompt)
class code_run:
    def __init__(self):
        self.name = "code_run"
        self.func = self.code_run
        self.args = ["code"]
        self.description = "Runs code"
        self.user_permission_required = False

    def code_run(self, code):
        return code_run(code)
class test_unit_gen:
    def __init__(self):
        self.name = "test_unit_gen"
        self.func = self.test_unit_gen
        self.args = ["test_unit"]
        self.description = "Generates unit test"
        self.user_permission_required = False

    def test_unit_gen(self, test_unit):
        return test_unit_gen(test_unit)
class test_unit_mod:
    def __init__(self):
        self.name = "test_unit_mod"
        self.func = self.test_unit_mod
        self.args = ["test_unit"]
        self.description = "Modifies unit test"
        self.user_permission_required = False

    def test_unit_mod(self, test_unit):
        return test_unit_mod(test_unit)
class test_unit_run:
    def __init__(self):
        self.name = "test_unit_run"
        self.func = self.test_unit_run
        self.args = ["test_unit"]
        self.description = "Runs unit test"
        self.user_permission_required = False

    def test_unit_run(self, test_unit):
        return test_unit_run(test_unit)
class test_integration_gen:
    def __init__(self):
        self.name = "test_integration_gen"
        self.func = self.test_integration_gen
        self.args = ["test_integration"]
        self.description = "Generates integration test"
        self.user_permission_required = False

    def test_integration_gen(self, test_integration):
        return test_integration_gen(test_integration)
class test_integration_mod:
    def __init__(self):
        self.name = "test_integration_mod"
        self.func = self.test_integration_mod
        self.args = ["test_integration"]
        self.description = "Modifies integration test"
        self.user_permission_required = False

    def test_integration_mod(self, test_integration):
        return test_integration_mod(test_integration)
class test_integration_run:
    def __init__(self):
        self.name = "test_integration_run"
        self.func = self.test_integration_run
        self.args = ["test_integration"]
        self.description = "Runs integration test"
        self.user_permission_required = False

    def test_integration_run(self, test_integration):
        return test_integration_run(test_integration)
class test_e2e_gen:
    def __init__(self):
        self.name = "test_e2e_gen"
        self.func = self.test_e2e_gen
        self.args = ["test_e2e"]
        self.description = "Generates e2e test"
        self.user_permission_required = False

    def test_e2e_gen(self, test_e2e):
        return test_e2e_gen(test_e2e)
class test_e2e_mod:
    def __init__(self):
        self.name = "test_e2e_mod"
        self.func = self.test_e2e_mod
        self.args = ["test_e2e"]
        self.description = "Modifies e2e test"
        self.user_permission_required = False

    def test_e2e_mod(self, test_e2e):
        return test_e2e_mod(test_e2e)
class test_e2e_run:
    def __init__(self):
        self.name = "test_e2e_run"
        self.func = self.test_e2e_run
        self.args = ["test_e2e"]
        self.description = "Runs e2e test"
        self.user_permission_required = False

    def test_e2e_run(self, test_e2e):
        return test_e2e_run(test_e2e)
