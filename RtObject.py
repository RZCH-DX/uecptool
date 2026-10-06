class RtObject:
    rt_plus_data = None
    radio_text = None
    def __init__(self, rt_plus_data, radio_text):
        self.rt_plus_data = rt_plus_data
        self.radio_text = radio_text

    def __eq__(self, object_compare):
        if not isinstance(object_compare, RtObject):
            return False
        return self.rt_plus_data == object_compare.rt_plus_data and self.radio_text == object_compare.radio_text