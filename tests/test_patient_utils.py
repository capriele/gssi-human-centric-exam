            
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import patient
from logger import Logger
from constants import Constants
from configurer import Configurer
from patient_utils import get_items_from_patient_configuration

patient_configurer = Configurer(Constants.SCHEMA_XSD_PATIENT)

alice_config = patient_configurer.load('configurations/patients/alice.xml', patient.parse)
bob_config = patient_configurer.load('configurations/patients/bob.xml', patient.parse)

print("Alice:")
print(get_items_from_patient_configuration(alice_config))
print("------------------------------------------")
print("Bob:")
print(get_items_from_patient_configuration(bob_config))

print(get_items_from_patient_configuration(alice_config)['dignity_rule_accept_ambulatory_support'].value)
print(get_items_from_patient_configuration(bob_config)['dignity_rule_accept_ambulatory_support'].value)