/*
 * Copyright 2015 Brockmann Consult GmbH
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef JPY_COMPAT_H
#define JPY_COMPAT_H

#ifdef __cplusplus
extern "C" {
#endif

#include <Python.h>
#include "frameobject.h"

#define JPY_VERSION_ERROR "jpy requires Python 3.9+"

#if PY_MAJOR_VERSION < 3 || PY_MINOR_VERSION < 9
    #error JPY_VERSION_ERROR
#endif

#define JPy_IS_CLONG(pyArg)      PyLong_Check(pyArg)
#define JPy_AS_CLONG(pyArg)      PyLong_AsLong(pyArg)
#define JPy_AS_CLONGLONG(pyArg)  PyLong_AsLongLong(pyArg)
#define JPy_FROM_CLONG(cl)       PyLong_FromLong(cl)

#define JPy_IS_STR(pyArg)        PyUnicode_Check(pyArg)
#define JPy_FROM_CSTR(cstr)      PyUnicode_FromString(cstr)
#define JPy_FROM_FORMAT          PyUnicode_FromFormat

#define JPy_AS_UTF8(unicode)                 PyUnicode_AsUTF8(unicode)
#define JPy_AS_WIDE_CHAR_STR(unicode, size)  PyUnicode_AsWideCharString(unicode, size)
#define JPy_FROM_WIDE_CHAR_STR(wc, size)     PyUnicode_FromKindAndData(PyUnicode_2BYTE_KIND, wc, size)

#ifdef __cplusplus
} /* extern "C" */
#endif
#endif /* !JPY_COMPAT_H */
