"""
**模块说明** \n
软件的本地化模块，负责返回指定语言的输出内容 \n
**模块状态** \n
已完成
"""

import configparser
import os
from . import SCC_Logs

# 文本显示的语言，默认为简体中文(zh-CN)，该值由配置文件优先提供
TRANSLATION_LANGUAGE = 'zh-CN'
# 默认翻译文件夹的地址
DEFAULT_TRUE_ADDRESS = os.path.dirname(str(__file__).rsplit('\\', maxsplit=1)[0]) + r'\Localization'
# 翻译失败时返回的默认值
_DEFAULT_Translation_STR = 'NULL'


class GetTranslation:
    """
    获取指定内容的翻译
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
            SCC_Logs.Logs(module_name=__name__).logger.debug(f'已从 {module_name} 中获取 {translation_name} '
                                                             f'对应的翻译内容 {get_translation} ')
        else:
            get_translation = _DEFAULT_Translation_STR
            SCC_Logs.Logs(module_name=__name__).logger.warning(f'无法从位于 {self._localization} '
                                                               f'中的 {module_name} 内获取 '
                                                               f'{translation_name} 对应的翻译内容')
        return get_translation


if __name__ == '__main__':
    pass
