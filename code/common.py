# coding=utf-8 
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C1001
# pylint: disable=W0232
# pylint: disable=R0903


class Common:
    common_num = 0
    def __init__(self):
        #
        pass
    def GET(self):
        Common.common_num += 1
        #return "hello" + str(Common.common_num)
        return "hello world"
    