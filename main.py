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


def resolvePane(pane, parentEl):
    # if any(k in pane for k in ("vertical", "horizontal")):
    #     print(pane)
    # pydash.assign(template, resolvePaned(window, windowEl))

    cmd: Terminal = pane.get('cmd')
    if cmd:
        return {next_id('terminal'): {
            'parent': parentEl['id'], 'type': 'Terminal', 'command': 'bash -c "trap $SHELL EXIT; %s"' % cmd, 'profile': 'default'}}

    return True


def resolvePaned(window: Split, parentEl: dict) -> dict:
    splitType = 'HPaned' if "horizontal" in window else 'VPaned'

    template = {}

    splitEl = {"parent": parentEl['id'],
               "type": splitType, "id": next_id(splitType.lower())}

    pydash.assign(template, {splitEl['id']: splitEl})

    panes = (window.get('vertical')
             or window.get('horizontal')).get('panes')

    lala = list(map(lambda x: resolvePane(x, splitEl), panes))

    print(lala)

    for key, value in [(k, v) for x in lala for (k, v) in x.items()]:
        pydash.assign(template, {key: value})

    return template


def main():
    for layout, windows in readConfigTest('data')[2].items():
        for window in windows:
            print(window)
            template = {}

            windowEl = {"parent": "", "type": "Window",
                        "id": next_id('window')}

            # config[windowEl['id']] = windowEl

            pydash.assign(template, {windowEl['id']: windowEl})

            cmd: Terminal = window.get('cmd')
            if cmd:
                # config[next_id('terminal')] = {
                #     'parent': windowEl['id'], 'type': 'Terminal', 'command': cmd, 'profile': 'default'}
                pydash.assign(template, {next_id('terminal'): {
                    'parent': windowEl['id'], 'type': 'Terminal', 'command': 'bash -c "trap $SHELL EXIT; %s"' % cmd, 'profile': 'default'}})

            if any(k in window for k in ("vertical", "horizontal")):
                for key, value in resolvePaned(window, windowEl).items():
                    # config[key] = value
                    pydash.assign(template, {key: value})

            notebook: Notebook = window.get('notebook')
            if notebook:
                print(notebook['tabs'])

            print(json.dumps(template, indent=2))
            config["layouts"] = {}
            config["layouts"][layout] = template
            config.write()


if __name__ == "__main__":
    main()