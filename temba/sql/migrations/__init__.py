import os

from django.db.migrations import RunSQL


class InstallSQL(RunSQL):
    """
    Migration that reads the SQL from the named file and runs it as a RunSQL migration
    """

    def __init__(self, filename):
        # build the full path to our filename
        sql_path = os.path.join(os.path.dirname(__file__), f"{filename}.sql")
        with open(sql_path) as sql_file:
            sql = sql_file.read()

        super().__init__(sql)
