#!/usr/bin/python
# -*- coding: UTF-8 -*-
# version xu.2020.09.10.141500  init configUtil
# description 配置文件读取


def get(config, section, key, logger):
    val = config.get(section, key)
    logger.info("config.ini - %s.%s: %s" % (section, key, val))
    return val


def getint(config, section, key, logger):
    val = config.getint(section, key)
    logger.info("config.ini - %s.%s: %s" % (section, key, val))
    return val
