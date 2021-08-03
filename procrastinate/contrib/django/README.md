# Django contrib package

## Usage

See https://procrastinate.readthedocs.io/en/stable/howto/django.html

## Contributing

### How are the migrations dynamically generated

In the following `procrastinate.contrib.django.migrations` is noted `p.c.d.migrations`
for conciseness.

The end goal is that when we run `./manage.py migrate`, Django sees one Django migration
for each sql migration in our `procrastinate/sql/migrations` folder. This means we want
to "trick" Django into thinking that there are migrations in the `p.c.d.migrations`
package, but this package doesn't exist on the disk.

This all happens in  `migrations_magic` if you want to read the code along.

Django introspects its apps looking for migrations (in django.db.migrations.loader). It
doesn't specifically let each App override the way it's done, so we can't "just"
override the right method in App and be done with it. But Django doesn't read the
migrations modules on the disk directly either. It does the following:

A. Try to import `p.c.d.migrations` using `importlib.import_module`. If it doesn't
  work, consider the app doesn't provide migrations
B. Use `pkgutil.iter_modules()` to discover all modules under `p.c.d.migrations`
C. For each module, import it using using `importlib.import_module` and read its
  `Migration` class

Python's import mechanisms are modular, there's multiple ways we can add some code for
our use case. While not necessary for the following, reading Python's import
documentation will help: https://docs.python.org/3/reference/import.html

We could imagine doing step A by going either way: either `p.c.d.migrations` could exist
and be empty or we could trick Python's import system into believing it exists. The
first alternative seems simpler, but if we do that, in the B step,
`pkgutil.iter_modules` will try to load submodules the same way this module was loaded:
by reading the disk. So in the end, given we'll be tricking the import system anyway,
we're doing it for both `p.c.d.migrations` and `p.c.d.migrations.*`

Doing step A is done the following way: we ensure that before Django tries to load
migrations, this module's `load()` function is called. It adds an instance of
`ProcrastinateMigrationsImporter` at the end of the `sys.meta_path`. This means that
whenever a module will be imported and not be found on the disk, our instance's
`find_spec()` method will be called. This method should return a `ModuleSpec` instance
if we want the finder to take responsibility on loading the module, None otherwise. We
return a ModuleSpec when the path we want to load is `p.c.d.migrations`, and provide a
loader instance, that will be used for loading our virtual module. Our importer class
serves as both finder and loader, so loader is self.

Python will create an empty module for us with `__name__` set to the dotted path of the
module we want to run, and call the loader's exec_module method, where our role is to
put the content of the module in place. In particular, the module's `__path__` is
important. A module is a package (i.e. it has submodules) if it has a `__path__`. Also,
the `__path__` will be used for `pkgutil.iter_modules`. At this step, we could put a
plausible value in the `__path__` like, but there's no real file on the disk we can
match, and this would require us to figure out where we are on the disk. A better
solution is to use a value that we know won't be mistaken for a path, and that we're
sure we can recognize easily. That's what we do with `VIRTUAL_PATH`.

Step B: Ok, we've returned a module for `p.c.d.migrations`, now Django will be running
`pkgutil.iter_modules` on our module's `__path__` (`VIRTUAL_PATH`). This results in
Python calling all the callables in `sys.path_hooks` with our path until one doesn't raise
`ImportError`. The default path hooks will all fail, we need our own hook. That's why in
the `load()` function mentionned below, we also added our importer's `path_hook` method to
`sys.path_hook`. We get called and check that the path is the `VIRTUAL_PATH` that we set
earlier. The path hook needs to return a Finder object suitable for listing its
submodules, so that would be `self`

Now Python will call a non-standard method on our finder: `iter_modules`
(https://docs.python.org/3/library/pkgutil.html?highlight=iter_modules#`pkgutil.iter_modules`)
This method is expected to return tuples consisting of a submodule name and a boolean
indicating whether the submodule is itself a package or not (easy: in our case it's
not). We'll expand below on how we got ahold of the fake migrations modules we want
to expose, but for now, let's assume we have them. We're able to return a list of
module names.

Step C: Now, Django will iterate on our module names and call `importlib.import_module`.
It works the same as before: Python will not manage to load the modules on disk, so
following the order of `sys.meta_path`, it will ask our importer's `find_spec()`. This
method returns `ModuleSpec` objects both for `p.c.d.migrations` and anything below, and
indicates itself to be the loader. This means the `exec_module` method is called next,
and this time, we can attach the `Migration` class that we have prepared to the module,
based on the module's `__name__` attribute.

Django will be happy with that and consider our app to have valid migrations.

But how did we generate the proper `Migration` classes? This part is actually much
more readable:

- We use `importlib_resources.files` to get the path of each sql file in
  procrastinate's migration folder (ensuring this would work even if our package was
  actually in a zip)
- For each migration, we build a `ProcrastinateMigration` object that extracts various
  parts from the migration filename
- For each `ProcrastinateMigration`, we generate a new class inheriting Django's
  `Migration` class. It needs to know the migration operations, its name and index
  (`0001`, `0002`, ...) and be linked to the previous migration
- The migration operations consist of a single step: a RunSQL operation whose SQL
  is the contents of the corresponding procrastinate migration file (read with `importlib_resources.read_text`)

That's it.
