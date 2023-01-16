"""Data validators for DB Models."""

from mongoengine import (
    EmbeddedDocument,
    Document,
    StringField,
    DecimalField,
    IntField,
    ListField,
    EmbeddedDocumentField,
    BooleanField,
)


class CPU(EmbeddedDocument):
    manufacturer = StringField()
    cores = IntField()


class RAM(EmbeddedDocument):
    volume = StringField()
    meter = StringField()
    type = StringField()


class WiFi(EmbeddedDocument):
    exist = BooleanField()
    ghz_24 = BooleanField()
    ghz_5 = BooleanField()


class Wireless(EmbeddedDocument):
    bluetooth = StringField()
    wifi = EmbeddedDocumentField(WiFi)
    gps = BooleanField()


class OS(EmbeddedDocument):
    name = StringField()
    version = DecimalField()


class Phone(Document):
    brand = StringField(required=True)
    model = StringField(required=True)
    year = IntField()
    cpu = EmbeddedDocumentField(CPU)
    ram = EmbeddedDocumentField(RAM)
    display = DecimalField()
    wireless = EmbeddedDocumentField(Wireless)
    os = EmbeddedDocumentField(OS)
    misc = ListField(StringField())
