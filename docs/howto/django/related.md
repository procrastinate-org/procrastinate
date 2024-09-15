# Create a relation between your model and the ProcrastinateJob model

When creating a relation between your custom Django model and the
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
foreign key relation to `null` upon job deletion. This is because the
`on_delete` parameter in Django models is only effective at the
application level and won't work if the job is deleted externally.

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

:::{note}
Ensure that you replace `app_name` and `mymodel` with the appropriate names
for your Django app and model.
:::

Alternatively, you can choose to cascade the deletion, which means that when a
job is deleted, any related records of your model will also be deleted.

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
                ON DELETE CASCADE;
            """,
            reverse_sql="""
                ALTER TABLE app_name_mymodel
                DROP CONSTRAINT app_name_mymodel_job_id_key;
            """
        ),
    ]
```
