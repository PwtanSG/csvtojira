import re


class JiraIssue:
    def __init__(self, key: str, summary: str, qn_no: str, description: str):
        self.key = key
        self.summary = summary
        self.qn_no = qn_no
        self.description = description

    @property
    def summary(self):
        return self._summary

    @property
    def qn_no(self):
        return self._qn_no

    @summary.setter
    def summary(self, summary_text):
        if not summary_text:
            raise Exception("summary cannot be empty")
        self._summary = summary_text

    @qn_no.setter
    def qn_no(self, desc_text):
        regex = r"^[Qq][Nn][0-9]{7}$"
        if not desc_text:
            raise Exception("qn_no cannot be empty")
        if not re.match(regex, desc_text):
            raise Exception("qn_no invalid")
        self._qn_no = desc_text

    # def __str__(self):
    #     return f'Issue {self.key} has age {self.title}'
    #
    def __repr__(self):
        return f'JiraIssue(key={self.key}, summary={self.summary}, qn_no={self.qn_no}, description={self.description}'
