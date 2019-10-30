.. _how-to-locks:

Ensure jobs run sequentially and in order
-----------------------------------------

In this section, we'll see **how** to setup locks. If you want to know
more about the locking feature (mainly the **why**), head to the Discussions
section (see :ref:`discussion-locks`).

Let's take ou example from the section linked above. In a environment with at least 2
workers, we're writing individual letters to the end of a file and want the letters to
be written in the same order that we ran the tasks::

    @app.task
    def write_alphabet(letter):
        time.sleep(random.random() * 5)
        with open("/tmp/alphabet.txt", "a") as f:
            f.write(letter)

If we defer the tasks without locks::

    write_alphabet.defer(letter="a")
    write_alphabet.defer(letter="b")
    write_alphabet.defer(letter="c")
    write_alphabet.defer(letter="d")

The result will most probably be unorder, say ``dabc``.

We can solve this problem by using locks::

    write_alphabet.configure(lock="/tmp/alphabet.txt").defer(letter="a")
    write_alphabet.configure(lock="/tmp/alphabet.txt").defer(letter="b")
    write_alphabet.configure(lock="/tmp/alphabet.txt").defer(letter="c")
    write_alphabet.configure(lock="/tmp/alphabet.txt").defer(letter="d")

Or simply::

    job_descritption = write_alphabet.configure(lock="/tmp/alphabet.txt")
    job_descritption.defer(letter="a")
    job_descritption.defer(letter="b")
    job_descritption.defer(letter="c")
    job_descritption.defer(letter="d")

Both ways, we're assured of getting ``abcd`` in our file.
