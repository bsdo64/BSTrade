import os

from PyQt5.uic import loadUiType, compileUiDir


VIEW_PATH = os.path.dirname(os.path.realpath(__file__)) + '/View'
UI_PATH = VIEW_PATH + '/Ui'


def pre_compile_ui():
    print('haha')
    compileUiDir(UI_PATH, recurse=True)


def load_ui(cls_name):
    file_name = UI_PATH + '/ui_' + cls_name + '.ui'
    return loadUiType(file_name)[0]


pre_compile_ui()
