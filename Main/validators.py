from django.core.exceptions import ValidationError

class CharValidator:
    ALLOWED_CHARS = ("ЁЙФЯЦЧУВСКАМЕПИНРТГОШЛЩДЗЖХЭёйфяцычувскамепинртгоьшлбщдюзжхэъ"
                     "QAZWSXEDCRFVTGBYHNUJMIKOLPqazwsxedcrfvtgbyhnujmikolp"
                     "1234567890-_.,!~:;№=+*/%()? \r\n\t")
    def __init__(self, message=None):
        self.message = message if message else "Недопустимый символ"
    def __call__(self,value, *args, **kwargs):
        if not (set(value) <= set(self.ALLOWED_CHARS)):
            raise ValidationError(self.message)