class AuditRegistry:
    

    def __init__(self):

        self._audits = []

    def register(
        self,
        audit
    ):

        self._audits.append(audit)

    def get_audits(self):

        return self._audits

    def clear(self):

        self._audits = []