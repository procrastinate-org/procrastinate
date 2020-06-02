Define custom JSON encoders and decoders
----------------------------------------

When calling ``mytask.defer()`` to create a job, the task arguments are serialized into
a JSON string for storing into the PostgreSQL database.

And after fetching a job from the database Procrastinate workers need to deserialize
the task arguments before calling the task.

By default Procrastinate relies on the JSON dumps and loads functions used by psycopg2.
(See the `psycopg2 documentation`_.) Procrastinate makes it possible to specify custom
encoders and decoders.

Here is an example involving serializing/deserializing ``datetime`` objects::

    import functools
    import json

    from procrastinate import App, AiopgConnector

    # Function used for encoding datetime objects
    def encode(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError()


    # Function used for decoding datetime objects
    def decode(dict_):
        if "dt" in dict_:
            dict_["dt"] = datetime.datetime.fromisoformat(dict_["dt"])
        return dict_

    json_dumps = functools.partial(json.dumps, default=encode)
    json_loads = functools.partial(json.loads, object_hook=decode)

    app = App(connector=AiopgConnector(json_dumps=json_dumps, json_loads=json_loads))

In this example the custom JSON dumps and loads functions are based on the standard
``json`` module's ``dumps`` and ``loads`` functions, with specific ``default`` and
``object_hook`` for serializing and deserializing ``datetime`` objects, respectively.
(See the `Python 3 json documentation`_ for more detail.)

This mechanism even makes it possible to use a different JSON implementation than
``json``, such as `UltraJSON`_ for example.

Also, if your encoding function starts resembling a long list of ``if isinstance``
calls, you may want to have a look at ``functools.singledispatch`` for a cleaner
way. (See the `Python 3 functools documentation`_ for more detail.)

.. _psycopg2 documentation: https://www.psycopg.org/docs/extras.html#json-adaptation
.. _Python 3 json documentation: https://docs.python.org/3/library/json.html
.. _UltraJSON: https://pypi.org/project/ujson/
.. _Python 3 functools documentation: https://docs.python.org/3/library/functools.html#functools.singledispatch
