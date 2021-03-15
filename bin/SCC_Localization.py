"""
**模块说明** 软件的本地化模块，不包括PYQT的GUI部分

**模块状态** DEBUG
"""

import configparser

DEFAULT_LOCAL_LANGUAGE = 'zh-CN'  # TODO(中期) 允许自定义语言


class GetTranslation:
    """
    *类参数*

    **module_name (str)** 调用此类的模块名
    **translation_name (str)** 需翻译的键值

    *类属性*

    **translation (str)** 返回已翻译的文本

    """

    def __init__(self, module_name: str, translation_name: str):
        self.localization = f'Localization/{DEFAULT_LOCAL_LANGUAGE}.ini'
        self.translation = self._get_translation(module_name, translation_name)

    def _get_translation(self, module_name: str, translation_name: str):
        """
        私有的翻译获取方法

        :param module_name: 调用此类的模块名
        :param translation_name: 需翻译的键值
        :return: 翻译文本
        """
        translation_read = open(self.localization, encoding='utf8')
        config_parser = configparser.ConfigParser()
        config_parser.read_file(translation_read)
        return config_parser.get(module_name, translation_name)


class GetStart:  # TODO(长期) 文件不存在+语言不支持
    pass


if __name__ == '__main__':
    pass
