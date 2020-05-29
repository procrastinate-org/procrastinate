Set the database schema
-----------------------

Any PostgreSQL database contains one or more schemas. Schemas are
PostgreSQL way of implementing namespaces for database objects. See the
`PostgreSQL Schema documentation`_ for more details on schemas. See the glossary
on :term:`schema` for a note on the several meanings of the term *schema*.

By default Procrastinate uses the ``public`` schema, which is PostgreSQL's default
schema, i.e. the schema that every new database contains.

To have Procrastinate use another schema than ``public``, change the *schema search
path* when creating the `AiopgConnector`::

    app = procrastinate.App(
        connector=procrastinate.AiopgConnector(
            host="localhost",
            options="-c search_path=myschema"
        )
    )

With this the ``procrastinate schema --apply`` command will create the Procrastinate
database objects (tables, functions, etc.) into the ``myschema`` schema. And all the
SQL queries issued by Procrastinate will apply to the database objects of that schema.

.. _PostgreSQL Schema documentation: https://www.postgresql.org/docs/current/ddl-schemas.html
