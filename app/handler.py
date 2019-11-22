""" middleware for odoo and portal """
import os
import logging
import urllib
from flask import request
from flask import Response
import jwt
import odoorpc
from dotenv import load_dotenv
from app import app
load_dotenv()

ODOO_LOGIN = os.getenv("ODOO_LOGIN")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_HOST = os.getenv("ODOO_HOST")
ODOO_PORT = os.getenv("ODOO_PORT")

JWT_SECRET = os.getenv("SECRET")

logging.basicConfig(filename='app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# possible_odoo_fields = [
# 'name', 'partner_name', 'contact_name', 'street', 'street2', 'city', 'country', 'function', 
# 'email_from', 'phone', 'mobile', 'email', 'website', 'title'
# ]

# dict keys are lending values, dict values are odoo fields
lending_toOdoo_fields = {'project': 'name', 'name': 'contact_name',
                         'company': 'partner_name', 'email': 'email_from', 'phone': 'phone'}


@app.route('/create/new/<string:record>', methods=["POST"])
def create_new_entity(record):
    """ Create new entity which depends on request record variable """
    odoo = odoo_login(ODOO_HOST, ODOO_PORT, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD)
    if not odoo:
        logging.warning("Can't establish connection to Odoo")
        return Response(status=500)

    logging.info("Get request to create new %s", record)
    data = request.form
    token = data.get('token', (None))
    # there will be parameters to create new item in odoo
    odoo_fields = {}
    odoo_env = {'contact': odoo.env['res.partner'],
                'lead': odoo.env['crm.lead']}
    if not token:
        logging.warning("Token doesn't exist in request data")
        return Response(status=401)
    elif token:
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, ['HS256'])
        except jwt.exceptions.InvalidTokenError as error:
            logging.warning("Invalid token error:  %s", error)
            return Response(status=401)

    if decoded_token:
        payload = data.items()
        for payload_key, payload_value in payload:
            for key, value in lending_toOdoo_fields.items():
                if payload_key == key:
                    odoo_fields.update({str(value): str(payload_value)})
        try:
            current_env = odoo_env.get(record, (None))
            if not current_env:
                logging.warning("Unknown odoo environment!")
                return Response(status=401)
            elif current_env == odoo.env['res.partner']:
                odoo_fields.update({"company_type": "person"})

                # Using the same lending_to_odoo_fields for contacts and leads
                # some hack below, because of not properly known format
                try:
                    odoo_fields["name"] = odoo_fields.pop("contact_name")
                    odoo_fields["email"] = odoo_fields.pop("email_from")
                except KeyError:
                    logging.warning("Key error while redefining fields from leads to contanct")
                
                current_env.create(odoo_fields)
            elif current_env == odoo.env['crm.lead']:
                current_env.create(odoo_fields)
        except odoorpc.error.RPCError as error:
            logging.warning("Odoo rpc error! Error: %s", error)
            return Response(status=500)

    return Response(status=201)


def odoo_login(odoo_host, odoo_port, odoo_db, od_login, odoo_password):
    """ Establish connection to Odoo & login to it """
    # try to establish connection to odoo
    try:
        odoo = odoorpc.ODOO(odoo_host, protocol='jsonrpc', port=odoo_port)
    except urllib.error.URLError:
        logging.warning("Can't open connection to Odoo")
        return None
    # if connection established, try to login
    if odoo:
        try:
            odoo.login(odoo_db, login=od_login, password=odoo_password)
        except odoorpc.error.RPCError:
            logging.warning("Odoo RPC error: Wrong Odoo password or login")
            return None

    return odoo
    