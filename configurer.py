import xmlschema
import os.path
from configuration import parse
from constants import Constants
from logger import Logger

class Configurer:
    base_schema_filename = Constants.CONFIGURER_BASE_XSD_SCHEMA
    
    def __init__(self):
        if os.path.isfile(Configurer.base_schema_filename):
            self.schema = self.load_schema(Configurer.base_schema_filename)
            Logger.s(f"{Configurer.base_schema_filename} loaded...")
        else:
            Logger.e(f"{Configurer.base_schema_filename} doesn't exist...")

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def load_schema(self, xsd_filename):
        if os.path.isfile(Configurer.base_schema_filename):
            return xmlschema.XMLSchema(xsd_filename)
        else:
            Logger.e(f"{xsd_filename} doesn't exist...")
    
    def load_base_configuration(self):
        return self.load_configuration(Constants.CONFIGURATION_BASE_XML_FILE)

    def load_configuration(self, xml_filename):
        if os.path.isfile(xml_filename):
            if self.schema:
                if self.is_valid(xml_filename):
                    Logger.s(f"{Configurer.base_schema_filename} loaded...")
                    return parse(xml_filename, silence=True)
                else:
                    Logger.e(f"{xml_filename} is not valid...")
            else:
                Logger.e(f"XML schema not loaded...")
        else:
            Logger.e(f"{xml_filename} doesn't exist...")
            

    def is_valid(self, xml_filename):
        if self.schema:
            return self.schema.is_valid(xml_filename)
        else:
            Logger.e(f"XML schema is not valid loaded...")