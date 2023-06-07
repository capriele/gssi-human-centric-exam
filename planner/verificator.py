from logger import Logger

class PlanVerificator:
    def __init__(self, configuration):
        self.configuration = configuration

    def verify(self, properties, patient_value, robot_value):
        filtered_properties = [property for property in self.configuration.get_properties(
        ).get_property() if property.key in properties]
        for property in filtered_properties:
            if property.from_ <= patient_value and patient_value <= property.to:
                Logger.i(f"Verifying the property if_{property.key}...")
                Logger.i(f"Patient value (humour): {patient_value}...")
                Logger.i(f"Robot value (attempts): {robot_value}...")
                max_attempts =  [behaviour for behaviour in self.configuration.get_behaviours().get_behaviour() if behaviour.key in ["if_" + property.key]][0].value
                Logger.i(f"Maximum attempts for this humor is: {max_attempts}...")
                return robot_value < max_attempts

    def __str__(self):
        return
