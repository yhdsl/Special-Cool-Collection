"""
**模块说明** \n
软件的本地化模块，负责返回指定语言的输出内容，但不包括GUI部分 \n
已在__init__文件中提供便捷方法 \n
**模块状态** \n
DEBUG
"""

import configparser
import os

# 默认选择的语言
DEFAULT_LANGUAGE = 'zh-CN'
# 默认语言配置文件的存储地址
DEFAULT_Config_Address = os.path.dirname(os.getcwd()) + r"\Config\CodeBase\Main.ini"
# 本模块的名称，用于在配置文件中搜索自定义的语言
DEFAULT_Module = 'SCC_Localization'
# 翻译失败时返回的默认值
DEFAULT_Translation = 'NULL'


class GetTranslation:
    """
    获取指定内容的翻译

    *类参数* \n
    **module_name: str** 调用此类的模块名，这将作为节名传入 \n
    **translation_name: str** 待翻译的内容

    *类属性* \n
    **translation() (str)** 返回已翻译的文本
    """

    def __init__(self, module_name: str, translation_name: str):
        self._lang = self._get_language()
        self._localization = os.path.dirname(os.getcwd()) + rf"\Localization\{self._lang}.ini"
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
            if module_name in get_configparser.sections():
                if config_name in get_configparser.options(module_name):
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

    def _get_language(self):
        """
        :return: 自定义的语言名称
        """
        if self._translation_exists(DEFAULT_Config_Address, DEFAULT_Module, 'DEFAULT_LANGUAGE'):
            language = self._get_configparser(DEFAULT_Config_Address).get(DEFAULT_Module, 'DEFAULT_LANGUAGE')
        else:
            language = DEFAULT_LANGUAGE
        return language

    def _get_translation(self, module_name: str, translation_name: str):
        """
        从ini文件中获取翻译

        :param module_name: 调用此类的模块名
        :param translation_name: 待翻译的内容
        :return: 已翻译的文本
        """
        if self._translation_exists(self._localization, module_name, translation_name):
            get_translation = self._get_configparser(self._localization).get(module_name, translation_name)
        else:
            get_translation = eval(DEFAULT_Translation, {"module": module_name, "translation": translation_name})
        return get_translation


if __name__ == '__main__':
    pass
