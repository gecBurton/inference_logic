====================
Inference Logic
====================


.. image:: https://img.shields.io/pypi/v/inference_logic.svg
        :target: https://pypi.python.org/pypi/inference_logic

.. image:: https://img.shields.io/travis/gecBurton/inference_logic.svg
        :target: https://travis-ci.com/gecBurton/inference_logic

.. image:: https://readthedocs.org/projects/json-inference-logic/badge/?version=latest
        :target: https://inference-logic.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/gecBurton/inference_logic/shield.svg
     :target: https://pyup.io/repos/github/gecBurton/inference_logic/
     :alt: Updates



The goal of this project is to explore how to write a minimal set of features to allow declarative programming in Python.

The code is loosely based on Prolog, however:

* The data structure is dicts/tuples/other rather than Prolog's functor/term as this id more Python-like.

* We use Python's native iter-unpacking star notation to indicate that a Variable points to all elements in a list's tail.

The success of this project is measured by the number of the `99 problems`_ actually solved_ to keep the code focussed on delivering features and not bike-shedding

This code is experimental and incomplete. Do not use it in your work or school! If you wish to use a serious, well tested declarative tool in Python then try the excellent pyDatalog_.

* Free software: MIT license
* Documentation: https://inference-logic.readthedocs.io.

tldr
----

The Hello-World of declarative programming is an ancestry query which illustrates the key ideas:

.. code-block:: python

    from inference_logic import Variable, Rule, search

    X, Y, Z, C, P = Variable.factory("X", "Y", "Z", "C", "P")

    db = [
        dict(parent="Abe", child="Homer"),
        dict(parent="Homer", child="Lisa"),
        dict(parent="Homer", child="Bart"),
        dict(parent="Homer", child="Maggie"),
        Rule(dict(ancestor=X, descendant=Z), dict(parent=X, child=Z)),
        Rule(
            dict(ancestor=X, descendant=Z),
            dict(parent=X, child=Y),
            dict(ancestor=Y, descendant=Z),
        ),
    ]

    query = dict(ancestor=P, descendant=C)
    results = search(db, query)


    assert next(results) == {C: "Lisa", P: "Abe"}
    assert next(results) == {C: "Bart", P: "Abe"}
    assert next(results) == {C: "Maggie", P: "Abe"}
    assert next(results) == {C: "Homer", P: "Abe"}
    assert next(results) == {C: "Lisa", P: "Homer"}
    assert next(results) == {C: "Bart", P: "Homer"}
    assert next(results) == {C: "Maggie", P: "Homer"}


This is similar to SQL where we have:

* A database which is a list of:

  * Things that are true by construction: Tables
  * Truths that are inferred: Views

* you can query the database with a statement. The engine will then respond with a list all values for which your query is true.

Here the "database" is a list of...

* Facts which are Python dicts, tuples and primitives (i.e. JSON), this is analogous to a record in table in SQL.

* Rules whose first argument is true if subsequent arguments are all true, this is analogous to a View in SQL.

* The database can then be queried with a statement that may contain Variables. The response will be a list of Variable-values that satisfy the query.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

This was originally inspired by py4fun_ some of this code here comes directly from this project.

Thank you to kclaurelie_ for helping to solve the fundamental problem that had been bugging me for months!

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`99 problems`: https://www.ic.unicamp.br/~meidanis/courses/mc336/2009s2/prolog/problemas/
.. _pyDatalog: https://pypi.org/project/pyDatalog/
.. _py4fun: https://www.openbookproject.net/py4fun/prolog/prolog1.html
.. _kclaurelie: https://github.com/kclaurelie
.. _LINQ: https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/
.. _solved: https://github.com/gecBurton/inference_logic/tree/main/tests/ninety_nine_problems
.. _unification: https://github.com/gecBurton/inference_logic/blob/main/inference_logic/algorithms.py
