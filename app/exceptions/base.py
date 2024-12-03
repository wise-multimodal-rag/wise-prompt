import json


class ApplicationError(Exception):
    """Application 내에서 발생하는 에러 포맷"""

    def __init__(self, code: int, message: str, result):
        self.code = code
        self.message = message
        self.result = result

    def __str__(self):
        exception_data = {
            "code": self.code,
            "message": self.message,
            "result": self.result
        }
        return json.dumps(exception_data, indent=4, ensure_ascii=False)

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "result": self.result
        }
