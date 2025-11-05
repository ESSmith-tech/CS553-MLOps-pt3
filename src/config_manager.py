import json, os
from typing import Dict, Any

class ConfigManager:
    """Handles loading and managing configuration files"""
    
    def __init__(self, script_dir: str = None):
        """
        Initialize the ConfigManager.
        
        Args:
            script_dir (str): Optional directory path override. If None, will
                            resolve paths relative to this module file.
        """
        if script_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(script_dir, '..'))
        self._config = None
        self._prompts = None
        self._css = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load and cache configuration"""
        if self._config is None:
            config_path = os.path.abspath(os.path.join(self.project_root, 'cm', 'app_config.json'))
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"Config not found at {config_path}. "
                    "Ensure the file exists in the container and was copied into the image."
                )
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        return self._config
    
    def load_prompts(self) -> Dict[str, Any]:
        """Load and cache prompts"""
        if self._prompts is None:
            prompts_path = os.path.abspath(os.path.join(self.project_root, 'cm', 'app_prompts.json'))
            if not os.path.exists(prompts_path):
                raise FileNotFoundError(
                    f"Prompts not found at {prompts_path}. "
                    "Ensure the file exists in the container and was copied into the image."
                )
            with open(prompts_path, 'r', encoding='utf-8') as f:
                self._prompts = json.load(f)
        return self._prompts
    
    def load_css(self) -> str:
        """Load and cache CSS"""
        if self._css is None:
            css_path = os.path.abspath(os.path.join(self.project_root, 'cm', 'app_ui.css'))
            if not os.path.exists(css_path):
                raise FileNotFoundError(
                    f"CSS file not found at {css_path}. "
                    "Ensure the file exists in the container and was copied into the image."
                )
            with open(css_path, 'r', encoding='utf-8') as f:
                self._css = f.read()
        return self._css
