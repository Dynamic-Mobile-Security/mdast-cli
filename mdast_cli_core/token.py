from .base import mDastBase


class mDastToken(mDastBase):
    """
    Class for interact with mDast system through ci/cd token
    """

    def __init__(self, base_url, ci_token, company_id):
        super().__init__(base_url)
        self.company_id = company_id
        self.current_context = {"company": company_id}
        self.headers = {'Authorization': 'Token {0}'.format(ci_token),
                        'Content-Type': 'application/json'}

    def set_headers(self, ci_token):
        self.headers = {'Authorization': 'Token {0}'.format(ci_token)}
