from app.utils.yaml_loader import load_yaml


class ConfigManager:
    @staticmethod
    def load_yaml(file_path: str) -> dict:
        """
        Generic YAML loader.
        """
        return load_yaml(file_path)

    @staticmethod
    def get_prompt(agent_name: str) -> dict:
        """
        Load prompt configuration.
        """
        return load_yaml(
            f"app/config/prompts/{agent_name}.yaml"
        )

    @staticmethod
    def get_agent_config(agent_name: str) -> dict:
        """
        Load agent configuration.
        """
        return load_yaml(
            f"app/config/agents/{agent_name}.yaml"
        )