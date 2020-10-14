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



declarative programming on json-like objects in Python


* Free software: MIT license
* Documentation: https://json-inference-logic.readthedocs.io.


Features
--------

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




99 problems
-----------

`99 problems`_

.. automodule:: tests.ninety_nine_problems.test_list
   :members:

.. automodule:: tests.ninety_nine_problems.test_arithmetic
   :members:



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`99 problems`: https://www.ic.unicamp.br/~meidanis/courses/mc336/2009s2/prolog/problemas/
