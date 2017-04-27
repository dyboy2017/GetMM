#/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

class MuchThread(threading.Thread):
    """
    属性:
    target: 传入外部函数, 用户线程调用
    args: 函数参数
    """
    def __init__(self, target, args):#多线程走起，多线程并发下载图片到本地,用这种方式解决多页面问题
        super(MuchThread, self).__init__()  #调用父类的构造函数 
        self.target = target
        self.args = args

    def run(self) :
        self.target(self.args)
