from . import db
from flask import json


class Template:

    def __init__(self, name, description, filename, contract_name, creator_guide, users_guide, statuses_list,
                 parameters_list, id=None, exist=False):
        """The default constructor"""
        self.__id = id
        self.__name = name
        self.__description = description
        self.__filename = filename
        self.__contract_name = contract_name
        self.__parameters_list = parameters_list
        self.__statuses_list = statuses_list
        self.__creator_guide = creator_guide
        self.__users_guide = users_guide
        if not exist:
            db_cur = db.get_db().cursor()
            db_cur.execute(
                'INSERT INTO template (name, description, filename, contract_name, creator_guide, \
                users_guide, statuses_list, parameters_list) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (name, description, filename, contract_name, json.dumps(creator_guide),
                 json.dumps(users_guide), json.dumps(statuses_list), json.dumps(parameters_list))
            )
            self.__id = db_cur.lastrowid
            db.get_db().commit()

    @staticmethod
    def by_id(id):
        template = db.get_db().execute(
            'SELECT * FROM template WHERE id=?',
            (id,)
        ).fetchone()
        if template is None:
            raise KeyError("Template with this id doesn't exist")

        return Template(template['name'], template['description'], template['filename'],
                        template['contract_name'], json.loads(template['creator_guide']),
                        json.loads(template['users_guide']), json.loads(template['statuses_list']),
                        json.loads(template['parameters_list']), id, exist=True)

    @staticmethod
    def all():
        templates = db.get_db().execute(
            'SELECT * FROM template'
        ).fetchall()
        if templates is None:
            raise KeyError("Templates don't exist")

        return [
            Template(template['name'], template['description'], template['filename'],
                     template['contract_name'], json.loads(template['creator_guide']),
                     json.loads(template['users_guide']), json.loads(template['statuses_list']),
                     json.loads(template['parameters_list']), template['id'], exist=True)
            for template in templates]

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def filename(self):
        return self.__filename

    @property
    def contract_name(self):
        return self.__contract_name

    @property
    def parameters_list(self):
        return self.__parameters_list

    @property
    def statuses_list(self):
        return self.__statuses_list

    @property
    def creator_guide(self):
        return self.__creator_guide

    @property
    def users_guide(self):
        return self.__users_guide

    def get_creator_guide_by_status(self, status_id):
        """
        Return creator's guide for status of this template

        Keyword arguments:
        status_id -- id of the status
        """
        return self.__creator_guide[status_id]

    def get_users_guide_by_status(self, status_id):
        """
        Return users' guide for status of this template

        Keyword arguments:
        status_id -- id of the status
        """

        return self.__users_guide[status_id]
