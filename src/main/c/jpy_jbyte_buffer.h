/*
 * Copyright 2023 JPY-CONSORTIUM Ltd.
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

#ifndef JPY_JBYTE_BUFFER_H
#define JPY_JBYTE_BUFFER_H

#ifdef __cplusplus
extern "C" {
#endif

#include "jpy_compat.h"

/**
 * The Java ByteBuffer representation in Python.
 *
 * IMPORTANT: JPy_JByteBufferObj must only differ from the JPy_JObj structure by the 'pyBuffer' member
 * since we use the same basic type, name JPy_JType for it. DON'T ever change member positions!
 * @see JPy_JObj
 */
typedef struct JPy_JByteBufferObj
{
    PyObject_HEAD
    jobject objectRef;
    Py_buffer *pyBuffer;
}
JPy_JByteBufferObj;

#ifdef __cplusplus
}  /* extern "C" */
#endif
#endif /* !JPY_JBYTE_BUFFER_H */
