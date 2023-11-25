import os
import json
class FileManager:
    def __init__(self, finnagi_instance):
        self.finnagi_instance = finnagi_instance

    
    def _get_absolute_path(self) -> None:
        return os.path.abspath(self.finnagi_instance.dir)

    def _create_dir_if_not_exists(self) -> None:
        absolute_path = self._get_absolute_path()
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)

            
    def _agent_data_exists(self) -> bool:
        absolute_path = self._get_absolute_path()
        return "agent_data.json" in os.listdir(absolute_path)


    def save_agent(self) -> None:
        episodic_memory_dir = f"{self.dir}/episodic_memory"
        semantic_memory_dir = f"{self.dir}/semantic_memory"
        filename = f"{self.dir}/agent_data.json"
        self.finnagi_instance.episodic_memory.save_local(path=episodic_memory_dir)
        self.finnagi_instance.semantic_memory.save_local(path=semantic_memory_dir)

        data = {"name": self.agent_name,
                "goal": self.agent_goal,
                "episodic_memory": episodic_memory_dir,
                "semantic_memory": semantic_memory_dir
                }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_agent(self) -> None:
        absolute_path = self._get_absolute_path()
        if not "agent_data.json" in os.listdir(absolute_path):
            self.finnagi_instance.ui.notify("ERROR", "Agent data does not exist.", title_color="red")

        with open(os.path.join(absolute_path, "agent_data.json")) as f:
            agent_data = json.load(f)
            self.agent_name = agent_data["name"]
            self.agent_goal = agent_data["goal"]

            try:
                self.finnagi_instance.semantic_memory.load_local(agent_data["semantic_memory"])
            except Exception as e:
                self.finnagi_instance.ui.notify(
                    "ERROR", "Semantic memory data is corrupted.", title_color="red")
                raise e
            else:
                self.finnagi_instance.ui.notify(
                    "INFO", "Semantic memory data is loaded.", title_color="GREEN")

            try:
                self.finnagi_instance.episodic_memory.load_local(agent_data["episodic_memory"])
            except Exception as e:
                self.finnagi_instance.ui.notify(
                    "ERROR", "Episodic memory data is corrupted.", title_color="RED")
                raise e
            else:
                self.finnagi_instance.ui.notify(
                    "INFO", "Episodic memory data is loaded.", title_color="GREEN")
