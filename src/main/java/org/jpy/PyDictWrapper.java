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
 *
 * This file was modified by Illumon.
 *
 */
package org.jpy;

import java.util.*;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.stream.Collectors;

/**
 * A simple wrapper around PyObjects that are actually Python dictionaries, to present the most useful parts of a
 * Map interface.
 */
public class PyDictWrapper implements Map<PyObject, PyObject> {
    private PyObject pyObject;

    PyDictWrapper(PyObject pyObject) {
        this.pyObject = pyObject;
    }

    @Override
    public int size() {
        return pyObject.callMethod("__len__").getIntValue();
    }

    @Override
    public boolean isEmpty() {
        return size() == 0;
    }

    @Override
    public boolean containsKey(Object key) {
        return PyLib.pyDictContains(pyObject.getPointer(), key, null);
    }

    /**
     * An extension to the Map interface that allows the use of String keys without generating warnings.
     */
    public boolean containsKey(String key) {
        return PyLib.pyDictContains(pyObject.getPointer(), key, String.class);
    }

    public boolean containsKey(PyObject key) {
        return PyLib.pyDictContains(pyObject.getPointer(), key, PyObject.class);
    }

    @Override
    public boolean containsValue(Object value) {
        return values().contains(value);
    }

    @Override
    public PyObject get(Object key) {
        return pyObject.callMethod("__getitem__", key);
    }

    /**
     * An extension to the Map interface that allows the use of String keys without generating warnings.
     */
    public PyObject get(String key) {
        return pyObject.callMethod("__getitem__", key);
    }

    @Override
    public PyObject put(PyObject key, PyObject value) {
        return putObject(key, value);
    }

    /**
     * An extension to the Map interface that allows the use of Object key-values without generating warnings.
     */
    public PyObject putObject(Object key, Object value) {
        return pyObject.callMethod("__setitem__", key, value);
    }

    @Override
    public PyObject remove(Object key) {
        try {
            PyObject value = get(key);
            pyObject.callMethod("__delitem__", key);
            return value;
        } catch (KeyError ke) {
            return null;
        }
    }

    public PyObject remove(String key) {
        return remove((Object)key);
    }

    @Override
    public void putAll(Map<? extends PyObject, ? extends PyObject> m) {
        throw new UnsupportedOperationException();
    }

    @Override
    public void clear() {
        pyObject.callMethod("clear");
    }

    /**
     * {@inheritDoc}
     *
     * <br><b>Note: we are returning a COPY not a VIEW of the keys</b>
     */
    @Override
    public Set<PyObject> keySet() {
        return new LinkedHashSet<>(PyLib.pyDictKeys(pyObject.getPointer()).asList());
    }

    /**
     * {@inheritDoc}
     *
     * <br><b>Note: we are returning a COPY not a VIEW of the values</b>
     */
    @Override
    public Collection<PyObject> values() {
        return PyLib.pyDictValues(pyObject.getPointer()).asList();
    }

    /**
     * {@inheritDoc}
     *
     * <br><b>Note: we are returning a COPY not a VIEW of the entries</b>
     */
    @Override
    public Set<Entry<PyObject, PyObject>> entrySet() {
        // todo: we'd prefer to use something like
        // https://docs.python.org/2.7/c-api/dict.html#c.PyDict_Next
        // https://docs.python.org/3/c-api/dict.html#c.PyDict_Next
        // but that method signature is a bit weird on the java <-> python jni layer with PyObject
        // reference return values...
        return PyLib.pyDictKeys(pyObject.getPointer())
            .asList()
            .stream()
            .map(p -> new SimpleImmutableEntry<>(p, get(p)))
            .collect(Collectors.toCollection(LinkedHashSet::new));
    }

    /**
     * Gets the underlying PyObject.
     *
     * @return the PyObject wrapped by this dictionary.
     */
    public PyObject unwrap() {
        return pyObject;
    }

    /**
     * Gets the underlying pointer for this object.
     *
     * @return the pointer to the underlying Python object wrapped by this dictionary.
     */
    long getPointer() {
        return pyObject.getPointer();
    }

    /**
     * Copy this dictionary into a new dictionary.
     *
     * @return a wrapped copy of this Python dictionary.
     */
    public PyDictWrapper copy() {
        return new PyDictWrapper(PyLib.copyDict(pyObject.getPointer()));
    }
}