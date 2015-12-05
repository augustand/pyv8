# encoding=utf-8
# !/usr/bin/env python
import os
import platform
import traceback
import logging

import PyV8


class CommonJS(PyV8.JSClass):
    def __init__(self):
        '''
        _js_modules: javascript模块,为加载
        _loaded_modules:  javascript模块,已经加载
        _js_path: javascript脚本路径
        '''
        super(CommonJS, self).__init__()

        self._js_modules = {}
        self._loaded_modules = {}
        self._js_path = [[os.path.dirname(__file__), False]]

        self.exports = {}

        self.__load_modules()

    def __load_modules(self):
        for i in range(len(self._js_path)):
            if self._js_path[i][1]:
                continue

            for (root, dirs, files) in os.walk(self._js_path[i][0]):
                print files,'111111111',dirs,root

                for _file in files:
                    namespace, ext = os.path.splitext(_file)
                    if ext != ".js":
                        continue
                    self._js_modules.update(
                        {namespace: os.path.join(root, _file)})
                    self._js_path[i][1] = True

    def require(self, module):
        if not self._js_modules.has_key(module):
            logging.error("module <%s> is not exists!", module)
            return

        logging.info("loading module <%s>...", module)
        path = self._js_modules[module]
        if self._loaded_modules.has_key(path):
            return self._loaded_modules[path]

        with open(path, 'r') as f:
            try:
                code = f.read().decode('utf-8')
                if platform.system() == 'Windows':
                    code = code.encode('utf-8')
                with PyV8.JSContext(self) as ctxt:
                    ctxt.eval(code)
                    self._loaded_modules[path] = ctxt.locals.exports
                return self._loaded_modules[path]
            except:
                logging.debug(traceback.extract_stack())
                return

    def append(self, path):

        for _path, _is_loaded in self._js_path:
            if path == _path:
                break
        else:
            self._js_path.append((path, False))
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
                return


if __name__ == '__main__':
    ctx = CommonJS()
    # ctx.append('hello')
    print ctx._js_path
    print ctx._js_modules
    print ctx.execute('require("math");')
