from . import db
from flask import json
from .template import Template


class Contract:

    instances = {}

    class __Decorators(object):
        @staticmethod
        def contract_alive(decorated):
            def wrapper(contract, *args, **kwargs):
                if not contract.is_alive():
                    raise ReferenceError('Contract was destroyed')
                return decorated(contract, *args, **kwargs)
            return wrapper

    def __init__(self, template_id, binary_code, abi, parameters, address=None, id=None, user=None, exist=False ):
        """The default constructor"""
        self.__id = id
        self.__template = Template.by_id(template_id)
        self.__binary_code = binary_code
        self.__abi = abi
        self.__parameters = parameters
        self.__address = address
        print(user)
        if not exist:
            db_cur = db.get_db().cursor()
            db_cur.execute(
                'INSERT INTO contract (template_id, binary_code, abi, parameters, user_id) VALUES (?, ?, ?, ?, ?)',
                (template_id, binary_code, json.dumps(abi), json.dumps(parameters), user.id)
            )
            self.__id = db_cur.lastrowid
            db.get_db().commit()


    @staticmethod
    def by_address(address, user):
        contract = db.get_db().execute(
            'SELECT * FROM contract WHERE address=?' + ' AND user_id=' + str(user.id) if user else '',
            (address, )
        ).fetchone()
        if contract == None:
            raise KeyError("Contract with this address doesn't exist")

        return Contract(contract['template_id'], contract['binary_code'], json.loads(contract['abi']),
                        json.loads(contract['parameters']), address, contract['id'], exist=True)

    @staticmethod
    def by_id(id, user=None):
        contract = db.get_db().execute(
            'SELECT * FROM contract WHERE id=?' + ' AND user_id=' + str(user.id) if user else '',
            (id,)
        ).fetchone()
        if contract == None:
            raise KeyError("Contract with this id doesn't exist")

        return Contract(contract['template_id'], contract['binary_code'], json.loads(contract['abi']),
                        json.loads(contract['parameters']), contract['address'], id, exist=True)

    @staticmethod
    def all(user=None):
        contracts = db.get_db().execute(
            'SELECT * FROM contract' + ' WHERE user_id=' + str(user.id) if user else ''
        ).fetchall()
        if contracts == None:
            raise KeyError("Contracts don't exist")

        return [Contract(contract['template_id'], contract['binary_code'], json.loads(contract['abi']),
                         json.loads(contract['parameters']), contract['address'], contract['id'],
                         exist=True) for contract in contracts]

    @staticmethod
    def delete(id):
        db_cur = db.get_db().cursor()
        db_cur.execute(
            'DELETE FROM contract WHERE id=(?)',
            (id, )
        )
        db.get_db().commit()

    @property
    @__Decorators.contract_alive
    def id(self):
        return self.__id

    @property
    @__Decorators.contract_alive
    def template(self):
        return self.__template

    @property
    @__Decorators.contract_alive
    def binary_code(self):
        return self.__binary_code

    @property
    @__Decorators.contract_alive
    def abi(self):
        return self.__abi

    @property
    @__Decorators.contract_alive
    def parameters(self):
        return self.__parameters

    @property
    @__Decorators.contract_alive
    def address(self):
        address = db.get_db().execute(
            'SELECT address FROM contract WHERE id=?',
            (self.id,)
        ).fetchone()[0]
        return address

    @__Decorators.contract_alive
    def set_address(self, address):
        if self.address is not None:
            raise PermissionError('Address has been already set')
        db.get_db().execute(
            'UPDATE contract SET address=? WHERE id=?',
            (address, self.id)
        )
        db.get_db().commit()
        self.__address = address

        return self

    @__Decorators.contract_alive
    def set_status(self, status):
        db.get_db().execute(
            'UPDATE contract SET status_id=? WHERE id=?',
            (status, self.id)
        )
        db.get_db().commit()

        return self

    @__Decorators.contract_alive
    def get_status(self):
        status = db.get_db().execute(
            'SELECT status_id FROM contract WHERE id=?',
            (self.id, )
        ).fetchone()[0]

        return self.template.statuses_list[status]

    def is_alive(self):
        contract = db.get_db().execute(
            'SELECT id FROM contract WHERE id=?',
            (self.__id,)
        ).fetchone()
        return contract is not None
