"""
**模块说明** 软件的本地化模块，暂不包括GUI部分

**模块状态** 开发中
"""

import configparser

LOCAL_LANGUAGE = 'zh-CN'


class GetTranslation:  # TODO(长期) 文件和键值不存在错误
    """
    *类参数*

    **module_name -> str** 调用此类的模块名
    **translation_name -> str** 需翻译的键值

    *类属性*

    **translation -> str** 返回已翻译的文本

    """

    def __init__(self, module_name, translation_name):
        self.localization = f'Localization/{LOCAL_LANGUAGE}.ini'
        self.translation = self._get_translation(module_name, translation_name)

    def _get_translation(self, module_name, translation_name):
        translation_read = open(self.localization, encoding='utf8')
        config_parser = configparser.ConfigParser()
        config_parser.read_file(translation_read)
        return config_parser.get(module_name, translation_name)


if __name__ == '__main__':
    pass
