from procrastinate import blueprints, retry


def test_app_task_explicit(app, mocker):
    bp = blueprints.Blueprint()

    @bp.task(
        name="foobar",
        queue="bar",
        lock="sher",
        queueing_lock="baz",
        retry=True,
        pass_context=True,
    )
    def wrapped():
        return "foo"

    app.register_blueprint(bp)

    assert wrapped() == "foo"
    assert app.tasks["foobar"].name == "foobar"
    assert app.tasks["foobar"].queue == "bar"
    assert app.tasks["foobar"].lock == "sher"
    assert app.tasks["foobar"].queueing_lock == "baz"
    assert isinstance(app.tasks["foobar"].retry_strategy, retry.RetryStrategy)
    assert app.tasks["foobar"].pass_context is True
    assert app.tasks["foobar"] is wrapped
    assert app.tasks["foobar"].func is wrapped.__wrapped__
