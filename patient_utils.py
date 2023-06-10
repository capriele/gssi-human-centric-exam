def get_items_from_patient_configuration(configuration):
    
    def find_xml_item_by_name(tagName, attrName, objects, verbose=False):
        item = None
        try:
            item = next(filter(lambda object: object.name == attrName, getattr(objects, tagName)), None) if objects else None
            if verbose:
                Logger.i(f"Tag: {attrName}, Found: {True if item else False}, Value: {getattr(item, 'value', None)}")
        finally:
            return item
        
    #from alice
    #alice autonomy
    autonomy_accept_health_status_check_rule = find_xml_item_by_name('rule', 'accept_health_status_check', configuration.ethics.autonomy)
    autonomy_patient_shows_signs_of_distress_exception = find_xml_item_by_name('exception', 'patient_shows_signs_of_distress', autonomy_accept_health_status_check_rule)
    autonomy_do_call_legal_guardian_action = find_xml_item_by_name('action', 'do_call_legal_guardian', autonomy_patient_shows_signs_of_distress_exception)
    autonomy_legal_guardian_does_not_answer_exception = find_xml_item_by_name('exception', 'legal_guardian_does_not_answer', autonomy_do_call_legal_guardian_action)
    autonomy_do_call_nurse_action = find_xml_item_by_name('action', 'do_call_nurse', autonomy_legal_guardian_does_not_answer_exception)
    autonomy_do_move_away_action = find_xml_item_by_name('action', 'do_move_away', autonomy_legal_guardian_does_not_answer_exception)
    #alice dignity
    dignity_accept_ambulatory_support_rule = find_xml_item_by_name('rule', 'accept_ambulatory_support', configuration.ethics.dignity)

    #from bob
    #bob autonomy
    autonomy_accept_medication_reminder_rule = find_xml_item_by_name('rule', 'accept_medication_reminder', configuration.ethics.autonomy)
    autonomy_enough_repetition_exception = find_xml_item_by_name('exception', 'enough_repetition', autonomy_accept_medication_reminder_rule)
    autonomy_do_call_nurse_action = find_xml_item_by_name('action', 'do_call_nurse', autonomy_enough_repetition_exception)
    #bob privacy
    privacy_accept_recording_rule = find_xml_item_by_name('rule', 'accept_recording', configuration.ethics.privacy)
    privacy_patient_is_in_toilet_exception = find_xml_item_by_name('exception', 'patient_is_in_toilet', privacy_accept_recording_rule)
    privacy_accept_distribution_rule = find_xml_item_by_name('rule', 'accept_distribution', configuration.ethics.privacy)
    privacy_accept_storage_rule = find_xml_item_by_name('rule', 'accept_storage', configuration.ethics.privacy)
    privacy_data_is_health_sensitive_exception = find_xml_item_by_name('exception', 'data_is_health_sensitive', privacy_accept_storage_rule)
    #bob dignity
    dignity_accept_ambulatory_support_rule = find_xml_item_by_name('rule', 'accept_ambulatory_support', configuration.ethics.dignity)

    items = dict()
    items['autonomy_rule_accept_health_status_check'] = autonomy_accept_health_status_check_rule
    items['autonomy_exception_patient_shows_signs_of_distress'] = autonomy_patient_shows_signs_of_distress_exception
    items['autonomy_action_do_call_legal_guardian'] = autonomy_do_call_legal_guardian_action
    items['autonomy_exception_legal_guardian_does_not_answer'] = autonomy_legal_guardian_does_not_answer_exception
    items['autonomy_action_do_call_nurse'] = autonomy_do_call_nurse_action
    items['autonomy_action_do_move_away'] = autonomy_do_move_away_action
    items['dignity_rule_accept_ambulatory_support'] = dignity_accept_ambulatory_support_rule
    items['autonomy_rule_accept_medication_reminder'] = autonomy_accept_medication_reminder_rule
    items['autonomy_exception_enough_repetition'] = autonomy_enough_repetition_exception
    items['autonomy_action_do_call_nurse'] = autonomy_do_call_nurse_action
    items['privacy_rule_accept_recording'] = privacy_accept_recording_rule
    items['privacy_exception_patient_is_in_toilet'] = privacy_patient_is_in_toilet_exception
    items['privacy_rule_accept_distribution'] = privacy_accept_distribution_rule
    items['privacy_rule_accept_storage'] = privacy_accept_storage_rule
    items['privacy_exception_data_is_health_sensitive'] = privacy_data_is_health_sensitive_exception
    
    return items