class MessageData:
    """Class to extract data from the message and request object. """
    def __init__(self, message, request):
        self.message = message
        self.request = request

    def _get_value_or_unknown(self, key):
        return self.message.get(key) or 'Unknown'

    @property
    def user_input(self):
        return self._get_value_or_unknown('text')

    @property
    def user_id(self):
        return self._get_value_or_unknown('userId')

    @property
    def conversation_id(self):
        return self._get_value_or_unknown('conversationId')

