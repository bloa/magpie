"""
PYGGI: Python General framework for Genetic Improvement
"""

## TODO: SimpleNamespace
class Config:
    def __init__(self):
        self.enable_astor = False
        self.log_dir = './pyggi_logs'
        self.work_dir = './pyggi_work'

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self.__dict__))

config = Config()

def oink():
    '''
    :return: ``'oink oink'``
    :rtype: str
    '''
    return 'oink oink'
