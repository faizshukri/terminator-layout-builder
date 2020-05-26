#!/usr/bin/env python

from collections import ChainMap
from configobj import ConfigObj
from pathlib import Path
import numbers
import os.path
import pydash
import sys
import yaml
import traceback
import logging

terminatorConfigPath = "%s/.config/terminator/config" % str(Path.home())
layoutDefinitionFile = "%s/.config/terminator/layout.yaml" % str(Path.home())
layoutCacheFile = "%s/.config/terminator/.layout_cache" % str(Path.home())

config = ConfigObj(terminatorConfigPath, indent_type="  ") if os.path.isfile(
    terminatorConfigPath) else ConfigObj(indent_type="  ")

config.filename = terminatorConfigPath

root = None

_ID = 0


def next_id(name):
    global _ID
    _ID += 1
    return '%s%s' % (name, _ID)


def readConfig(file: str):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def resolveElem(elem, parentElem):

    elemRoot = elem.get('root')

    if parentElem is None:
        if elemRoot:
            global root
            root = elemRoot
        windowElem = {"parent": "", "type": "Window",
                      "id": next_id('window')}
        return pydash.assign({windowElem['id']: windowElem}, resolveElem(elem, windowElem))

    cmd = elem.get('cmd')
    if cmd:
        cmdElem = {'parent': parentElem['id'], 'type': 'Terminal',
                   'command': 'bash -c "trap $SHELL EXIT; %s"' % cmd, 'profile': 'default'}
        if elem.get('order') is not None:
            cmdElem['order'] = elem.get('order')

        if elem.get('title'):
            cmdElem['title'] = elem.get('title')

        if elemRoot or root:
            cmdElem['directory'] = elemRoot or root

        return {next_id('terminal'): cmdElem}

    if any(k in elem for k in ("vertical", "horizontal")):
        template = {}
        panedType = 'HPaned' if "horizontal" in elem else 'VPaned'
        panedElem = {"parent": parentElem['id'],
                     "type": panedType, "id": next_id(panedType.lower())}

        verticalOrHorinzontalElem = (
            elem.get('vertical') or elem.get('horizontal'))

        if elem.get('order') is not None:
            panedElem['order'] = elem.get('order')

        ratio = verticalOrHorinzontalElem.get('ratio')
        if ratio:
            if(not isinstance(ratio, numbers.Number) or ratio < 0 or ratio > 1):
                sys.exit(
                    "[ERROR] Ratio must be a Number, between 0 and 1.")

            panedElem['ratio'] = ratio

        pydash.assign(template, {panedElem['id']: panedElem})

        panes = verticalOrHorinzontalElem.get('panes')
        if(len(panes) != 2):
            sys.exit(
                "[ERROR] Panes must have exactly 2 items.")
        lala = list(map(lambda i_el: resolveElem(pydash.assign(
            i_el[1], {"order": i_el[0]}), panedElem), enumerate(panes)))
        for key, value in [(k, v) for x in lala for (k, v) in x.items()]:
            pydash.assign(template, {key: value})
        return template

    tabs = elem.get('tabs')
    if tabs:
        template = {}
        tabsEl = {"parent": parentElem.get('id'), "type": "Notebook",
                  "id": next_id('notebook'), "active_page": 0}

        if tabs.get('labels'):
            if(len(tabs.get('labels')) != len(tabs.get('items'))):
                sys.exit(
                    "[ERROR] The labels must be the same size with the items.")
            tabsEl['labels'] = tabs.get('labels')

        pydash.assign(template, {tabsEl['id']: tabsEl})
        lala = list(map(lambda i_el: resolveElem(pydash.assign(
            i_el[1], {"order": i_el[0]}), tabsEl), enumerate(tabs['items'])))
        for key, value in [(k, v) for x in lala for (k, v) in x.items()]:
            pydash.assign(template, {key: value})
        return template

    sys.exit("[ERROR] Unknown element: %s" % elem)


def main():
    try:
        if not os.path.exists(layoutDefinitionFile):
            sys.exit("Layout file not exists [%s]. Skipped." %
                     layoutDefinitionFile)

        cacheFile = open(layoutCacheFile)
        cacheFileContent = cacheFile.read().split(",")

        def filterFn(layout):
            if pydash.has(config, 'layouts.%s' % layout[0]) and layout[0] not in cacheFileContent:
                sys.stdout.write(
                    "Layout %s already exists. Replace? [y/N]: " % layout[0])
                choice = input().lower()
                if (choice != 'y'):
                    return False
            return True

        layouts = list(
            filter(filterFn, readConfig(layoutDefinitionFile).items()))

        for layout, windows in layouts:
            global _ID, root
            _ID = 0
            root = None

            pydash.objects.set_(config, 'layouts.%s' % layout, dict(
                ChainMap(*list(map(lambda window: resolveElem(window, None), windows)))))

        cacheFile = open(layoutCacheFile, 'w')
        cacheFile.write(",".join(list(map(lambda layout: layout[0], layouts))))
        cacheFile.close()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        print(e)
