#!/usr/bin/env python
import os
import re
import platform
from PyV8 import JSContext, JSError

import traceback
import logging

import PyV8

__author__ = "flier.lu@gmail.com"
__version__ = "%%prog 0.1 (Google v8 engine v%s)" % PyV8.JSEngine.version


class CommonJS(PyV8.JSClass):
    def __init__(self, parent=None):
        super(CommonJS, self).__init__()

        self._js_modules = {}
        self._loaded_modules = {}
        self.parent = parent
        self._js_path = [(os.path.dirname(__file__), 0)]

        self.exports = {}

        self.__load_modules()

    def __load_modules(self):
        for i in range(len(self._js_path) - 1):
            if self._js_path[i][1]:
                continue

            for (root, dirs, files) in os.walk(self._js_path[i][0]):
                for _file in files:
                    namespace, ext = os.path.splitext(_file)
                    if ext != ".js":
                        continue
                    self._js_modules.update(
                        {namespace: os.path.join(root, _file)})
                    self._js_path[i][1] = 1

    def require(self, module):
        if not self._js_modules.has_key(module):
            logging.error("module <%s> is not exists!", module)
            return

        logging.info("loading module <%s>...", module)
        path = self._js_modules[module]
        if not self._loaded_modules.has_key(path):
            with open(path, 'r') as f:

                try:
                    code = f.read().decode('utf-8')
                    if platform.system() == 'Windows':
                        code = code.encode('utf-8')
                    with PyV8.JSContext(self) as ctxt:
                        ctxt.eval(code)
                except:
                    logging.debug(traceback.extract_stack())

                self._loaded_modules[path] = ctxt.locals.exports
                return self._loaded_modules[path]
        else:
            return self._loaded_modules[path]

    def append(self, path):

        for _path, _is_loaded in self._js_path:
            if path == _path:
                break
        else:
            self._js_path.append((path, 0))
            self.__load_modules()

        return self

    def execute(self, code):
        logging.info("executing script...")

        with PyV8.JSContext(self) as _ctxt:
            try:
                if not isinstance(code, basestring):
                    logging.error("code is not string")
                    return

                code = code.decode('utf-8')
                if platform.system() == 'Windows':
                    code = code.encode('utf-8')
                return _ctxt.eval(code)
            except:
                logging.error("fail to process debug event")
                logging.debug(traceback.extract_stack())


if __name__ == '__main__':
    ctx = CommonJS()
    # ctx.append('/my/js/path')
    print ctx.execute('require("math");')
