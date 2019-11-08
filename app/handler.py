""" middleware for odoo and portal """
import os
import logging
from flask import request
from flask import Response
import jwt
import odoorpc
from dotenv import load_dotenv
from app import app
load_dotenv()

ODOO_LOGIN = os.getenv("LOGIN")
ODOO_PASSWORD = os.getenv("PASSWORD")
ODOO_DB = os.getenv("DB")
ODOO_HOST = os.getenv("HOST")
ODOO_PORT = os.getenv("PORT")

JWT_SECRET = os.getenv("SECRET")

odoo = odoorpc.ODOO(ODOO_HOST, protocol='jsonrpc', port=ODOO_PORT)

logging.basicConfig(filename='app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# function stays for person job position
# title stays for person appeal like miss, mister and etc.
odoo_contact_fields = [
    'name', 'phone', 'mobile', 'email', 'street', 'street2', 'city', 'function', 'website', 'title'
    ]

# try to login to odoo
try:
    odoo.login(ODOO_DB, login=ODOO_LOGIN, password=ODOO_PASSWORD)
except odoorpc.error.RPCError:
    logging.warning("Can't login successfully to odoo")

# routing below
@app.route('/create/contact', methods=["POST"])
def create_odoo_contact():
    """ Create contact in odoo, if token is valid, in other case return 401 code """
    data = request.form

    token = data.get('token', (None))

    if not token:
        print("token doesnt exist")
        logging.warning("Token doesnt exist in request")      
        return Response(status=401)
    else:
        # set default company type for all external contacts
        exist_odoo_fields = {"company_type": "person"}
        #get key, values from data
        items = data.items()
        
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, ['HS256'])
        except jwt.exceptions.InvalidSignatureError as error:
            logging.warning('Invalid token error. Error: %s', error)
            return Response(status=401)
        
        if decoded_token['target'] == "odoo":
            for item_key, item_value in items:
                for key in odoo_contact_fields:
                    if key == item_key:
                        # add key:value to dict
                        exist_odoo_fields.update({str(item_key): str(item_value)})
            print(exist_odoo_fields)
            try:
                contact = odoo.env['res.partner']
                # create contact from dict
                contact.create(exist_odoo_fields)
            except odoorpc.error.RPCError as error:
                logging.warning("Odoo rpc error! Error: %s", error)
                return Response(status=500)    

    return Response(status=201)
