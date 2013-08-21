import sqlite3
import peewee


class Node(peewee.Model):
    """node class"""
    host = peewee.CharField(max_length=50)
    port = peewee.IntegerField()

    @property
    def addr(self):
        return (self.host, self.port)


class Message(peewee.Model):
    """message object"""
    node = peewee.ForeignKeyField(Node)
    data = peewee.TextField()


def init(db_name):
    database = peewee.SqliteDatabase(db_name)

    for model in [Node, Message]:
        model._meta.database = database
        try:
            model.create_table()
        except sqlite3.OperationalError:
            pass
