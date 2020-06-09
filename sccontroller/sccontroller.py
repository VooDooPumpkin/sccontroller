from web3 import Web3
from solcx import compile_files
from flask import json, current_app, g
import os
import requests
from .contract import Contract
from .template import Template


class SCContoller:

    def __init__(self, node, defaul_account, root_path):
        """Constructor"""
        self.w3 = Web3(Web3.HTTPProvider(node))
        try:
            self.w3.eth.blockNumber
        except requests.exceptions.InvalidSchema:
            raise ConnectionError("Can not connect to Node '{}'".format(node))
        try:
            self.w3.eth.defaultAccount = self.w3.toChecksumAddress(defaul_account)
            if self.w3.toChecksumAddress(defaul_account) not in self.w3.eth.accounts:
                raise ValueError("Invalid account address '{}'".format(defaul_account))
        except ValueError:
            raise ValueError("Invalid account address '{}'".format(defaul_account))
        self.templates_dir = root_path.replace('\\', '/') + '/templates'

    @staticmethod
    def get_scc():
        if 'scc' not in g:
            g.scc = SCContoller(current_app.config['NODE'], current_app.config['DEFAULT_ACCOUNT'],
                                current_app.root_path)

        return g.scc

    def generate(self, template_id, parameters):
        template = Template.by_id(template_id)
        contract = compile_files([os.path.normpath(self.templates_dir + '/' + template.filename)])
        identifier = '{}:{}'.format(self.templates_dir + '/' + template.filename, template.contract_name)
        if 'refund' in [param['name'] for param in template.parameters_list]:
            parameters['refund'] = self.w3.eth.defaultAccount
        for param in template.parameters_list:
            pname = param['name']
            ptype = param['type']
            if pname == 'refund':
                parameters['refund'] = self.w3.eth.defaultAccount
                continue
            if pname not in parameters.keys():
                raise TypeError("Not enough parameters. Expected '{}' parameter".format(pname))
            if ptype.lower() == 'address':
                try:
                    parameters[pname] = self.w3.toChecksumAddress(parameters[pname])
                except:
                    raise ValueError("Wrong value for address type '{}'".format(parameters[pname]))
            elif ptype.lower() == 'string':
                try:
                    parameters[pname] = self.w3.toText(parameters[pname])
                except:
                    raise ValueError("Wrong value for string type '{}'".format(parameters[pname]))
            elif ptype.lower() == 'bytes':
                try:
                    parameters[pname] = self.w3.toBytes(parameters[pname])
                except:
                    raise ValueError("Wrong value for bytes type '{}'".format(parameters[pname]))
            elif 'uint' in ptype.lower():
                try:
                    parameters[pname] = self.w3.toInt(parameters[pname])
                except:
                    raise ValueError("Wrong value for uint type '{}'".format(parameters[pname]))
                finally:
                    if parameters[pname] < 0:
                        raise ValueError("Wrong value for uint type '{}'".format(parameters[pname]))
            elif 'int' in ptype.lower():
                try:
                    parameters[pname] = self.w3.toInt(parameters[pname])
                except:
                    raise ValueError("Wrong value for int type '{}'".format(parameters[pname]))

        contract = Contract(template_id, contract[identifier]['bin'], contract[identifier]['abi'], parameters=parameters)

        return contract

    def get_contract(self, id):
        contract = Contract.by_id(id)

        return contract

    def deploy(self, contract):
        # Instantiate and deploy contract
        w3_contract = self.w3.eth.contract(
            abi=contract.abi,
            bytecode=contract.binary_code
        )
        # Get transaction hash from deployed contract
        tx_hash = w3_contract.constructor(**contract.parameters).transact()
        # Get tx receipt to get contract address
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        contract_address = tx_receipt['contractAddress']
        contract.set_address(contract_address)

        return contract_address

    def destruct(self, contract):
        w3_contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(contract.address),
                                abi=contract.abi)

        tx_hash = w3_contract.functions.kill().transact()
        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

        Contract.delete(contract.id)

        return receipt

    def transaction_gas_cost(self, transaction):
        gas_used = self.w3.eth.estimateGas(transaction)
        gas_price = self.w3.eth.gasPrice

        return gas_price * gas_used

    def deploy_gas_cost(self, contract):
        params = contract.parameters
        contract = self.w3.eth.contract(
            abi=contract.abi,
            bytecode=contract.binary_code
        )
        gas_used = contract.constructor(**params).estimateGas()
        gas_price = self.w3.eth.gasPrice

        return gas_price * gas_used

    def event_filter(self, template):
        contract = compile_files([os.path.normpath(self.templates_dir + '/' + template.filename)])
        identifier = '{}:{}'.format(self.templates_dir + '/' + template.filename, template.contract_name)

        contract = contract.pop(identifier)

        contract = self.w3.eth.contract(
            abi=contract['abi'],
            bytecode=contract['bin']
        )

        event_filter = contract.events.StatusChanged.createFilter(fromBlock="latest")

        return event_filter


