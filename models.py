# -*- coding: utf-8 -*-
import datetime
from flask import url_for
from app import db

class Link(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    slug = db.StringField(max_length=255, required=True)
    url = db.StringField(max_length=255, required=True)
    _id = db.IntField(min_value=1)

    def get_absolute_url(self):
        return url_for('link', kwargs={"slug": self.slug})

    meta = {
        'allow_inheritance': True,
        'indexes': ['_id', 'slug'],
        'ordering': ['-_id']
    }
