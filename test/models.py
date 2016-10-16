from peewee import *
db = SqliteDatabase('test.db')


class BaseModel(Model):
    class Meta:
        database = db


class Config(BaseModel):
    name = CharField(unique=True)
    value = CharField()


class Jar(BaseModel):
    inner_name = CharField(max_length=100)
    name = CharField(max_length=100)
    type = CharField(max_length=100)
    url = CharField(max_length=200)
    path = CharField(max_length=200, null=True)
    downloaded = BooleanField(default=False)


class Server(BaseModel):
    name = CharField(unique=True)
    initialized = BooleanField(default=False)
    jar = ForeignKeyField(Jar, related_name='servers')

    java_size = IntegerField()
    xmx = IntegerField()
    xms = IntegerField()


def get_without_failing(model, query, default=None):
    results = model.select().where(query).limit(1)
    return results[0] if len(results) > 0 else default


def create_tables():
    db.connect()
    db.create_tables([Config, Jar, Server], safe=True)
    db.close()
