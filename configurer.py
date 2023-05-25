import xmlschema
import os.path
from configuration import parse

class Configurer:
    base_schema_filename = "./configuration/schema_configuration.xsd"

    def __init__(self):
        if os.path.isfile(Configurer.base_schema_filename):
            self.schema = self.load_schema(Configurer.base_schema_filename)
            print(f"[Success] {Configurer.base_schema_filename} loaded...")
        else:
            print(f"[Error] {Configurer.base_schema_filename} doesn't exist...")

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def load_schema(self, xsd_filename):
        if os.path.isfile(Configurer.base_schema_filename):
            return xmlschema.XMLSchema(xsd_filename)
        else:
            print(f"[Error] {xsd_filename} doesn't exist...")

    def load_configuration(self, xml_filename):
        if os.path.isfile(xml_filename):
            if self.schema:
                if self.is_valid(xml_filename):
                    print(f"[Success] {Configurer.base_schema_filename} loaded...")
                    return parse(xml_filename, silence=True)
                else:
                    print(f"[Error] {xml_filename} is not valid...")
            else:
                print(f"[Error] XML schema not loaded...")
        else:
            print(f"[Error] {xml_filename} doesn't exist...")
            

    def is_valid(self, xml_filename):
        if self.schema:
            return self.schema.is_valid(xml_filename)
        else:
            print(f"[Error] XML schema not loaded...")