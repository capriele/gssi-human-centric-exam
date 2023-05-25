from configurer import Configurer


configurer = Configurer()
configuration = configurer.load_configuration('./configuration/basic_configuration.xml')

print(f"Robot name: {configuration.get_name()}")