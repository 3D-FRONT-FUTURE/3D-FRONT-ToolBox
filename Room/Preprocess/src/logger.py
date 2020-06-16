import logging
from logging import handlers




class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self,
                 filename,
                 level='info',
                 when='D',
                 backCount=3,
                 # fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
                 fmt='%(asctime)s [%(levelname)s] %(message)s'):

        format_str = logging.Formatter(fmt)

        # StreamHandler
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        
        # TimedRotatingFileHandler
        # th = handlers.TimedRotatingFileHandler(
        #     filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        # th.setFormatter(format_str)

        # logger
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations.get(level))
        self.logger.addHandler(sh)
        # self.logger.addHandler(th)

    def d(self, str):
        """debug"""

        self.logger.debug(str)

    def i(self, str):
        """info"""

        self.logger.info(str)

    def w(self, str):
        """warning"""
        
        self.logger.warning(str)

    def e(self, str):
        """error"""
        
        self.logger.error(str)

    def c(self, str):
        """critical"""
        
        self.logger.critical(str)


logger = Logger('info.log', level='info')


if __name__ == '__main__':
    log = Logger('all.log', level='debug')
    log.d('debug')
    log.i('info')
    log.w(u'WARNING')
    log.e(u'ERROR')
    log.c(u'FATAL')
    Logger('error.log', level='error').logger.error('error')
