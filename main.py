#!/usr/bin/env python

from __future__ import annotations
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Optional, Union, Dict
from configobj import ConfigObj
import yaml
import pydash
import json


@dataclass
class Terminal:
    cmd: str
    title: Optional[str]


@dataclass
class Split:
    horizontal: Optional[Paned]
    vertical: Optional[Paned]


@dataclass
class Paned:
    ratio: float
    panes: List[Split, Terminal]


Tab = Union[Terminal, Split]


@dataclass
class Notebook:
    labels: List[str]
    tabs: List[Tab]


@dataclass
class Window(Split, Terminal):
    root: str
    notebook: Optional[Notebook]


Layout = Dict[str, List[Window]]

_last_id = 0

config = ConfigObj(indent_type="  ")

config.filename = "./hey.ini"


def next_id(name):
    global _last_id
    id = _last_id
    _last_id += 1
    return '%s%s' % (name, id)


def readConfig(file: str) -> Layout:
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def readConfigTest(file: str) -> List[Layout]:
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)['tests']
        except yaml.YAMLError as exc:
            print(exc)


def resolveElem(elem, parentElem):
    if parentElem is None:
        windowElem = {"parent": "", "type": "Window",
                      "id": next_id('window')}
        return pydash.assign({windowElem['id']: windowElem}, resolveElem(elem, windowElem))

    cmd = elem.get('cmd')
    if cmd:
        cmdElem = {'parent': parentElem['id'], 'type': 'Terminal',
                   'command': 'bash -c "trap $SHELL EXIT; %s"' % cmd, 'profile': 'default'}
        if elem.get('order') is not None:
            cmdElem['order'] = elem.get('order')
        return {next_id('terminal'): cmdElem}

    if any(k in elem for k in ("vertical", "horizontal")):
        template = {}
        panedType = 'HPaned' if "horizontal" in elem else 'VPaned'
        panedElem = {"parent": parentElem['id'],
                     "type": panedType, "id": next_id(panedType.lower())}
        if elem.get('order'):
            panedElem['order'] = elem.get('order')
        pydash.assign(template, {panedElem['id']: panedElem})
        panes = (elem.get('vertical')
                 or elem.get('horizontal')).get('panes')
        lala = list(map(lambda x: resolveElem(x, panedElem), panes))
        for key, value in [(k, v) for x in lala for (k, v) in x.items()]:
            pydash.assign(template, {key: value})
        return template

    notebook: Notebook = elem.get('notebook')
    if notebook:
        template = {}
        notebookEl = {"parent": parentElem.get('id'), "type": "Notebook",
                      "id": next_id('notebook')}
        pydash.assign(template, {notebookEl['id']: notebookEl})
        lala = list(map(lambda i_el: resolveElem(pydash.assign(
            i_el[1], {"order": i_el[0]}), notebookEl), enumerate(notebook['tabs'])))
        for key, value in [(k, v) for x in lala for (k, v) in x.items()]:
            pydash.assign(template, {key: value})
        return template


def main():
    for layout, windows in readConfigTest('data')[3].items():
        for window in windows:
            print(window)

            result = resolveElem(window, None)

            print(json.dumps(result, indent=2))
            config["layouts"] = {}
            config["layouts"][layout] = result
            config.write()


if __name__ == "__main__":
    main()
