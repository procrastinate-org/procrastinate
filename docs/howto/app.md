# Find a correct place for your app

We advise you to place your app in one of the following places:

- Ideally, a dedicated module (`your_app.procrastinate` for example),
- The place where you define all your tasks if it's a single module.

In the first case, it's important to specify the location of your tasks using the
`import_paths` parameter:

```
import procrastinate

app = procrastinate.App(
    connector=connector,
    import_paths=["dotted.path.to", "all.the.modules", "that.define.tasks"]
)
```

If you want to put your app at the top-level of your program, be sure to check
the relevant discussion section: {ref}`top-level-app`.
