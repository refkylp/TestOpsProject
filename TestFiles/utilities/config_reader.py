import os
from jproperties import Properties

class ConfigReader:
    _properties = None

    @classmethod
    def _load_properties(cls):
        """Load properties file if not already loaded"""
        if cls._properties is None:
            cls._properties = Properties()
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configuration.properties')
            try:
                with open(config_path, 'rb') as config_file:
                    cls._properties.load(config_file)
            except Exception as e:
                print(f"Error loading configuration file: {e}")
                raise

    @classmethod
    def get_property(cls, key):
        """Get property value by key"""
        cls._load_properties()
        value = cls._properties.get(key)
        return value.data if value else None
