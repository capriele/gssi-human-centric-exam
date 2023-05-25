from configurer import Configurer


configurer = Configurer()
configuration = configurer.load_configuration('./configuration/base_configuration.xml')

print(f"Robot name: {configuration.get_name()}")
#print(configuration.get_properties().get_property()[0].from_)


filtered_properties = [property for property in configuration.get_properties().get_property() if property.key in ["patient_humor_good", "patient_humor_bad"]]


for i in filtered_properties:
    print(i.from_, i.to)
    
    
print([behaviour for behaviour in configuration.get_behaviours().get_behaviour() if behaviour.key in ["if_patient_humor_good"]][0].medicine_attempts)

