class MessageData:
    def __init__(self, message, request):
        self.message = message
        self.request = request

    @property
    def user_input(self):
        return self.message.get('text', 'Unknown')

    @property
    def user_id(self):
        return self.message.get('userId', 'Unknown')

    @property
    def conversation_uuid(self):
        return self.message.get('conversationId', 'Unknown')

    @property
    def page_url(self):
        return self.message.get('currentPageUrl', 'Unknown')

    @property
    def referral_url(self):
        return self.message.get('referralUrl', 'Unknown')

    @property
    def partner_id(self):
        return self.message.get('partnerId', 'Unknown')

    @property
    def session_id_ga(self):
        return self.message.get('sessionId', 'Unknown')

    @property
    def client_ip(self):
        return self.request.headers.get('X-Forwarded-For', self.request.remote_addr).split(",")[0].strip()
