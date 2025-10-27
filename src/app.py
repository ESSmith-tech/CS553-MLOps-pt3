import os, sys
from prometheus_client import start_http_server


# Add the src directory to Python path to ensure imports work
# This handles cases where app.py might be moved during deployment by Hugging Face
# current_dir = os.path.dirname(os.path.abspath(__file__))
# src_dir = os.path.join(current_dir) 
# if src_dir not in sys.path:
#     sys.path.insert(0, src_dir)


from config_manager import ConfigManager
from model_manager import ModelManager
from chat_handler import ChatHandler
from ui_factory import UIFactory

class ChatApp:
    """Main application class"""
    
    def __init__(self, script_dir: str = None):
        self.config_manager = ConfigManager(script_dir)
        self.config = self.config_manager.load_config()
        self.prompts = self.config_manager.load_prompts()
        self.css = self.config_manager.load_css()
        
        self.model_manager = ModelManager(self.config)
        self.chat_handler = ChatHandler(self.model_manager, self.config, self.prompts)
        
        self.chatbot = UIFactory.create_chatbot_interface(self.chat_handler, self.config)
        self.demo = UIFactory.create_main_interface(self.chatbot, self.config, self.css)
    
    def launch(self, **kwargs):
        """Launch the application"""
        # Start background model loading
        self.model_manager.start_model_loading()
        
        # Launch the demo
        self.demo.launch(**kwargs)

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    # Start the chat application
    app = ChatApp()
    app.launch()
