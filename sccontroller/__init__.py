import os
import time
import copy
import sqlite3
from datetime import timedelta
from threading import Thread
from flask import json, abort, request, g
from flask_api import FlaskAPI, status, exceptions
from flask_jwt import JWT, jwt_required
from werkzeug.security import check_password_hash
from solcx import set_solc_version, get_installed_solc_versions, install_solc
from .sccontroller import SCContoller
from .contract import Contract
from .template import Template


def create_app(test_cfg=None):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(16),
        DATABASE=os.path.join(app.instance_path, 'sccontroller.sqlite'),
        JWT_EXPIRATION_DELTA=timedelta(hours=1)
    )

    if test_cfg is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_cfg)

    if not 'NODE' in app.config:
        print('Specify eth node address in instance/config.py')
        exit(-1)
    if not 'DEFAULT_ACCOUNT' in app.config:
        print ('Specify default eth account in instance/config.py')
        exit(-1)

    try:
        if not 'v0.6.2' in  get_installed_solc_versions():
            install_solc('v0.6.2')
            set_solc_version('v0.6.2')
    except Exception as e:
        print('Unable to install solc v0.6.2: ' + str(e))
        exit(-1)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def authenticate(username, password):
        user = auth.get_user(username)
        if user and check_password_hash(user.password, password):
            return user

    def identity(payload):
        user_id = payload['identity']
        return auth.get_user_by_id(user_id)


    jwt = JWT(app, authenticate, identity)

    @app.errorhandler(400)
    def custom400(error):
        response = json.dumps({'message': error.description['message']})
        return response

    @app.errorhandler(503)
    def custom503(error):
        response = json.dumps({'message': error.description['message']})
        return response

    @app.route('/templates')
    @jwt_required()
    def templates():
        """Return templates"""

        try:
            templates = Template.all()

            return [{
                'id': it.id,
                'name': it.name,
                'description': it.description,
                'parameters_list': [param for param in it.parameters_list if param['name'] != "refund"]
            } for it in templates], status.HTTP_200_OK
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    @app.route('/templates/<int:id>')
    @jwt_required()
    def template(id):
        """Return template info by id

        Keyword arguments:
        id -- id of the template
        """

        try:
            template = Template.by_id(id)

            return {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'parameters_list': [param for param in template.parameters_list if param['name'] != "refund"]
            }, status.HTTP_200_OK
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    @app.route('/create-cotract', methods=['POST'])
    @jwt_required()
    def create_contract():
        """Create and deploy contract from template with params

        Data arguments:
        template_id -- id of the template
        parameters -- params dict key=value (keys as keys from templates parameters_list)
        """
        try:
            data = request.get_json(True)
            scc = SCContoller.get_scc()

            contract = scc.generate(data['template_id'], data['parameters'])
            if scc.w3.eth.getBalance(scc.w3.eth.defaultAccount) < scc.deploy_gas_cost(contract):
                abort(status.HTTP_503_SERVICE_UNAVAILABLE, {'message': 'Not enough gas in system to deploy'})
            scc.deploy(contract)

            return {"id": contract.id}, status.HTTP_200_OK
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})
        except ValueError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    @app.route('/contracts')
    @jwt_required()
    def get_contracts():
        """Return contracts info"""

        try:
            contracts = Contract.all()

            return [{
                'id': contract.id,
                'template_id': contract.template.id,
                'address': contract.address,
                'status': contract.get_status(),
                'creator_guide': contract.template.creator_guide,
                'users_guide': contract.template.users_guide,
            } for contract in contracts], status.HTTP_200_OK
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    @app.route('/contracts', methods=['POST'])
    @jwt_required()
    def get_contracts_by_id():
        """Return contracts info by ids

        Keyword arguments:
        ids -- array of ids of the contracts
        """

        try:
            data = request.get_json(True)

            contracts = [Contract.by_id(id) for id in data['ids']]

            return [{
                'id': contract.id,
                'template_id': contract.template.id,
                'address': contract.address,
                'status': contract.get_status(),
                'creator_guide': contract.template.creator_guide,
                'users_guide': contract.template.users_guide,
            } for contract in contracts], status.HTTP_200_OK
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    @app.route('/contracts/<int:id>')
    @jwt_required()
    def get_contract(id):
        """Return contract info by id

       Keyword arguments:
       id -- id of the contract
       """

        try:
            contract = Contract.by_id(id)

            return {
                'id': contract.id,
                'template_id': contract.template.id,
                'address': contract.address,
                'status': contract.get_status(),
                'creator_guide': contract.template.creator_guide,
                'users_guide': contract.template.users_guide,
            }, status.HTTP_200_OK
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    @app.route('/contracts/<int:id>/destroy')
    @jwt_required()
    def destroy_contract(id):
        """Destroy the contract by id and return success of the destruction

        Keyword arguments:
        id -- id of the contract
        """
        try:
            SCContoller.get_scc().destruct(Contract.by_id(id))

            return '', status.HTTP_204_NO_CONTENT
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, {'message': str(e)})

    from . import db, auth, template_controller
    db.init_app(app)
    auth.init_app(app)
    template_controller.init_app(app)

    def handle_event(event):
        status = event['args']['cur_status']
        address = event['address']
        try:
            contract = Contract.by_address(address)
            contract.set_status(status)
        except (KeyError, ReferenceError):
            pass

    def log_loop(event_filters, poll_interval):
        with app.app_context():
            while True:
                for event_filter in event_filters:
                    for event in event_filter.get_new_entries():
                        handle_event(event)
                time.sleep(poll_interval)

    with app.app_context():
        try:
            scc = SCContoller.get_scc()
            event_filters = [scc.event_filter(template) for template in Template.all()]
            worker = Thread(target=log_loop, args=(event_filters, 5), daemon=True)
            worker.start()
        except sqlite3.DatabaseError:
            db.init_db()
            scc = SCContoller.get_scc()
            event_filters = [scc.event_filter(template) for template in Template.all()]
            worker = Thread(target=log_loop, args=(event_filters, 5), daemon=True)
            worker.start()
        except ConnectionError as e:
            print(str(e))
            exit(-1)
        except ValueError as e:
            print(str(e))
            exit(-1)

    return app
