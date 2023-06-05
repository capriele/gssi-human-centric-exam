import xmlschema
import os.path
from logger import Logger

class Configurer:
    
    def __init__(self, xsd_filename):
        self.schema = self.load_schema(xsd_filename)
    
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def load_schema(self, xsd_filename):
        if os.path.isfile(xsd_filename):
            self.schema = xmlschema.XMLSchema(xsd_filename)
            return self.schema
        else:
            Logger.e(f"{xsd_filename} doesn't exist...")
    
    def load(self, xml_filename, parse):
        if os.path.isfile(xml_filename):
            if self.schema:
                if self.is_valid(xml_filename):
                    Logger.s(f"{xml_filename} loaded...")
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