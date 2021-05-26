"""
**模块说明** \n
软件的本地化模块，负责返回指定语言的输出内容 \n
**模块状态** \n
已完成
"""

import configparser
import os
if __name__ == '__main__':
    from CodeBase import SCC_Logs
else:
    from . import SCC_Logs

# 文本显示的语言，默认为简体中文(zh-CN)，该值由配置文件优先提供
TRANSLATION_LANGUAGE = 'zh-CN'
# 默认翻译文件夹的地址
DEFAULT_TRUE_ADDRESS = os.path.dirname(str(__file__).rsplit('\\', maxsplit=1)[0]) + r'\Localization'
# 翻译失败时返回的默认值
_DEFAULT_Translation_STR = 'NULL'
# 本模块的日志拓展选项，用于输出更为详细的日志内容
_LOG_STACK_BOOL = False


class GetTranslation:
    """
    获取指定内容的翻译 \n
    保证无论如何均会返回一个值

    *类参数* \n
    **module_name: str** 调用此类的模块名，这将作为节名传入 \n
    **translation_name: str** 待翻译的内容

    *类属性* \n
    **translation -> str** 返回已翻译的文本
    """

    def __init__(self, module_name: str, translation_name: str):
        self._localization = rf"{DEFAULT_TRUE_ADDRESS}\{TRANSLATION_LANGUAGE}.ini"
        self.translation = self._get_translation(module_name, translation_name)
        self._logger = SCC_Logs.Logs().logger

    def _translation_exists(self, ini_address: str, module_name: str, config_name: str):
        """
        确定指定配置文件，模块内容，待翻译的内容是否存在

        :param ini_address: 指定配置文件的地址
        :param module_name: 模块名，这将作为节名传入
        :param config_name: 待翻译的内容
        :return: Bool
        """
        translation_exists = False
        if os.path.exists(ini_address):
            get_configparser = self._get_configparser(ini_address)
            if get_configparser.has_option(module_name, config_name):
                translation_exists = True
        if not translation_exists:
            self._logger.warning(f'未在位于 <{ini_address}> 的 <{module_name}> 里找到 <{config_name}> 对应的文本内容，'
                                 f'已返回默认值 <{_DEFAULT_Translation_STR}>', stack_info=_LOG_STACK_BOOL)
        return translation_exists

    @staticmethod
    def _get_configparser(ini_address: str):
        """
        返回已读取文件的ConfigParser类，该方法未做稳定性处理

        :param ini_address: 指定配置文件的地址
        :return: 已读取文件的ConfigParser类
        """
        get_configparser = configparser.ConfigParser()
        get_configparser.optionxform = lambda option: option
        get_configparser.read_file(open(ini_address, encoding='utf8'))
        return get_configparser

    def _get_translation(self, module_name: str, translation_name: str):
        """
        从ini文件中获取翻译

        :param module_name: 调用此类的模块名
        :param translation_name: 待翻译的内容
        :return: 已翻译的文本
        """
        if self._translation_exists(self._localization, module_name, translation_name):
            get_translation = self._get_configparser(self._localization).get(module_name, translation_name)
            self._logger.debug(f'已从 <{module_name}> 中获取 <{translation_name}> 对应的翻译内容 <{get_translation}>',
                               stack_info=_LOG_STACK_BOOL)
        else:
            get_translation = _DEFAULT_Translation_STR
        return get_translation
