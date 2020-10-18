====================
JSON Inference Logic
====================


.. image:: https://img.shields.io/pypi/v/json_inference_logic.svg
        :target: https://pypi.python.org/pypi/json_inference_logic

.. image:: https://img.shields.io/travis/gecBurton/json_inference_logic.svg
        :target: https://travis-ci.com/gecBurton/json_inference_logic

.. image:: https://readthedocs.org/projects/json-inference-logic/badge/?version=latest
        :target: https://json-inference-logic.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/gecBurton/json_inference_logic/shield.svg
     :target: https://pyup.io/repos/github/gecBurton/json_inference_logic/
     :alt: Updates



This is an library to explore how it is possible to write
declarative code in Python.

This code is experimental and incomplete. Do not use it in your
work or school! If you wish to use a serious, well tested
declarative tool in Python use the excellent pyDatalog_.

* Free software: MIT license
* Documentation: https://json-inference-logic.readthedocs.io.

tldr
----

Write declarative code in pure Python

.. code-block:: python

    X, Y, Z, C, P = Variable.factory("X", "Y", "Z", "C", "P")

    db = [
        dict(parent="G", child="A"),
        dict(parent="A", child="O"),
        Rule(dict(ancestor=X, descendant=Z), dict(parent=X, child=Z)),
        Rule(
            dict(ancestor=X, descendant=Z),
            dict(parent=X, child=Y),
            dict(ancestor=Y, descendant=Z),
        ),
    ]

    query = dict(ancestor=P, descendant=C)


    assert next(search(db, query)) == {P: "G", C: "O"}
    assert next(search(db, query)) == {P: "G", C: "A"}
    assert next(search(db, query)) == {P: "A", C: "O"}



Motivation
----------

Today popular programming languages will typically support a
range of programming styles such as:

* imperative
* object orientated
* functional

They may also include something more mysterious called declarative
or logical programming. However declarative programing remains
poorly understood and badly supported compared to other styles.

This situation is odd because almost all programmers are perfectly
competent in a purely declarative language: SQL.

Other commonly used declarative resources include:

* Regex
* HTML
* math(s) stuff: BLAS; Matlab etc

A common theme is clear: declarative code is written in domain
specific code, normal code is written in normal languages, and the
bridge between them is usually some thin wrapper around the DSL that
does little more than type conversion.

It is unclear that it has to be this way, after all LINQ_ gives C#
programmers access to declarative tools both for interacting with
SQL but also for working with .net objects.

So the goal of this project is to explore how to write a minimal
set of features that allows a programmer to code declaratively
in native Python.

The code is loosely based on Prolog, and success is measured in
number of the `99 problems`_ solved to keep the code focussed
on delivering features not bike-shedding



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

This was originally inspired by py4fun_ some of this code here comes directly
from this project.

Thank you to kclaurelie_ for helping to solve the fundamental
problem that had been bugging me for months!

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`99 problems`: https://www.ic.unicamp.br/~meidanis/courses/mc336/2009s2/prolog/problemas/
.. _pyDatalog: https://pypi.org/project/pyDatalog/
.. _py4fun: https://www.openbookproject.net/py4fun/prolog/prolog1.html
.. _kclaurelie: https://github.com/kclaurelie
.. _LINQ: https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/
