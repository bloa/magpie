import re

from .abstract_edit import AbstractEdit


class TemplatedEdit(AbstractEdit):
    @classmethod
    def template(cls, template, rename=None):
        args = [s.strip() for s in re.findall(r'"[^"]*?"|[^,]+', template[1:-1])]
        name = rename or f'{cls.__name__}{template}'
        return type(name, (cls, ), {'TEMPLATE': args})

    def __str__(self):
        return re.sub(r'Templated', '', super().__str__())
