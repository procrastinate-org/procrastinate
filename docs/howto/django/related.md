# Create a relationship between your Django model and a Procrastinate job

When creating a relationship between your custom Django model and the
Procrastinate job model, it is advisable to disable constraint creation. This
is because Procrastinate jobs might be deleted outside of Django (e.g.,
when starting the worker with `procrastinate worker --delete-jobs=always`).

```python
class MyModel(models.Model):
    job = models.OneToOneField(ProcrastinateJob, db_constraint=False)
    # or
    job = models.ForeignKey(ProcrastinateJob, db_constraint=False)
```

Additionally, it's recommended to implement a custom migration to set the
foreign key relationship to `null` upon job deletion. Since the `on_delete`
parameter is only effective at the application level, it won't work if the job
is deleted externally.

```python
class Migration(migrations.Migration):
    operations = [
        # ... other migrations
        migrations.RunSQL(
            sql="""
                ALTER TABLE app_name_mymodel
                ADD CONSTRAINT app_name_mymodel_job_id_key
                FOREIGN KEY (procrastinate_job_id)
                REFERENCES procrastinate_jobs(id)
                ON DELETE SET NULL;
            """
            reverse_sql="""
                ALTER TABLE app_name_mymodel
                DROP CONSTRAINT app_name_mymodel_job_id_key;
            """
        ),
    ]
```

Ensure that you replace `app_name` and `mymodel` with the appropriate names
for your Django app and model.
