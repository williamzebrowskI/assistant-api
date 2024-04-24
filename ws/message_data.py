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
    def conversation_uuid(self):
        return self._get_value_or_unknown('conversationId')

    @property
    def page_url(self):
        return self._get_value_or_unknown('currentPageUrl')

    @property
    def referral_url(self):
        return self._get_value_or_unknown('referralUrl')

    @property
    def partner_id(self):
        return self._get_value_or_unknown('partnerId')

    @property
    def session_id_ga(self):
        return self._get_value_or_unknown('sessionId')

    @property
    def client_ip(self):
        ip = self.request.headers.get('X-Forwarded-For', self.request.remote_addr)
        return ip.split(",")[0].strip() if ip else 'Unknown'
