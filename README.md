![Build Status](https://github.com/jpy-consortium/jpy/actions/workflows/build.yml/badge.svg?branch=master)


jpy - a Python-Java Bridge
==========================

jpy is a **bi-directional** Python-Java bridge which you can use to embed Java
code in Python programs or the other way round. It has been designed
particularly with regard to maximum data transfer speed between the two
languages.  It comes with a number of outstanding features:

* Fully translates Java class hierarchies to Python
* Transparently handles Java method overloading
* Support of Java multi-threading
* Fast and memory-efficient support of primitive Java array parameters via
  [Python buffers](http://docs.python.org/3.3/c-api/buffer.html)
  (e.g. [Numpy arrays](http://docs.scipy.org/doc/numpy/reference/arrays.html))
* Support of Java methods that modify primitive Java array parameters (mutable
  parameters)
* Java arrays translate into Python sequence objects
* Java API for accessing Python objects (`jpy.jar`)

jpy has been tested with Python 3.6–3.13 and OpenJDK 8+ on Linux, Windows, and macOS.

The initial development of jpy was driven by the need to write Python
extensions to an established scientific imaging application programmed in
Java, namely the [SNAP](http://step.esa.int/) toolbox, the SeNtinel
Application Platform project, funded by the [European Space
Agency](http://www.esa.int/ESA) (ESA). (jpy is bundled with the SNAP
distribution.) Current development and maintenance is funded by [Deephaven](https://deephaven.io).

Writing such Python plug-ins for a Java application usually requires a
bi-directional communication between Python and Java since the Python
extension code must be able to call back into the Java APIs.

For more information please have a look into jpy's

* [documentation](http://jpy.readthedocs.org/en/latest/)
* [source repository](https://github.com/jpy-consortium/jpy)
* [issue tracker](https://github.com/jpy-consortium/jpy/issues?state=open)

How to build wheels for Linux and Mac
-------------------------------------

Install a JDK 8, preferably the Oracle distribution. Set `JDK_HOME` or
`JPY_JDK_HOME` to point to your JDK installation and run the build script:

    $ export JDK_HOME=<your-jdk-dir>
    $ export JAVA_HOME=$JDK_HOME
    $ pip install setuptools wheel
    $ python setup.py build maven bdist_wheel

On success, the wheel is found in the `dist` directory.

To deploy the `jpy.jar` (if you don't know why you need this step, this is not
for you)::

    $ mvn clean deploy -DskipTests=true

How to build a wheel for Windows
--------------------------------

Set `JDK_HOME` or `JPY_JDK_HOME` to point to your JDK installation. You'll
need Windows SDK 7.1 or Visual Studio C++ to build the sources. With Windows
SDK 7.1::

    > SET VS90COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools\
    > SET DISTUTILS_USE_SDK=1
    > C:\Program Files\Microsoft SDKs\Windows\v7.1\bin\setenv /x64 /release
    > SET JDK_HOME=<your-jdk-dir>
    > pip install setuptools wheel
    > python setup.py build maven bdist_wheel
    
With Visual Studio 14 and higher it is much easier::

    > SET VS100COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\Tools\
    > SET JDK_HOME=<your-jdk-dir>
    > pip install setuptools wheel
    > python setup.py build maven bdist_wheel

On success, the wheel can be found in the `dist` directory.

How to install from sources
---------------------------

TBD

Releasing jpy
-------------

The target reader of this section is a jpy developer wishing to release a new
jpy version.  Note: You need to have Sphinx installed to update the
documentation.

1. Make sure all Java *and* Python units tests run green
2. Remove the `-SNAPSHOT` qualifier from versions names in both the Maven
   `pom.xml` and `setup.py` files, and update the version numbers and copyright
   years in `jpyutil.py` and `doc/conf.py`.
3. Generate Java API doc by running `mvn javadoc:javadoc` which will update
   directory `doc/_static`
4. Update documentation, `cd doc` and run `make html` 
5. http://peterdowns.com/posts/first-time-with-pypi.html


Running Tests
----------------

Run: `python setup.py build test`

Code Of Conduct
---------------

This project has adopted the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). 
For more information see the [Code of Conduct](CODE_OF_CONDUCT.md) or contact [opencode@deephaven.io](mailto:opencode@deephaven.io)
with any additional questions or comments.

Contributing
------------

For instructions on contributing, see [CONTRIBUTING.md](CONTRIBUTING.md).


Notes
-----

Some of the details on this README are out of date. Efforts to improve them will be made in the future.
