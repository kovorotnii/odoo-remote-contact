# odoo-remote-contact
- App works as a middleware between Odoo and Your: landing page, site, and etc. Nowadays, it allows to create leads and contacts.
- Using JWT authorization
- Tested on Odoo 11 CE, [OdooRPC 0.7.0](https://github.com/OCA/odoorpc)

#### Make sure that your Odoo user-account has permissions to create leads and contancts!!!
 - In the most cases this will help to fix security error (Go to Settings -> Users -> Select current user):
   - Choose in Application Accesses:
     - Sales : Manager
     - Administration - Access Rights
   - Choose in Extra rights
     - Contact creation
#### So, if these combination will not help you, try to add more rights to your Odoo user! Do it properly!

#### Due to [docker-compose.yaml](./docker-compose.yaml) build base image using this command:
 `docker build -t odoo-middleware .`
#### Set Odoo credetials as environment variables in [docker-compose.yaml](./docker-compose.yaml)
 - ODOO_LOGIN  
 - ODOO_PASSWORD 
 - ODOO_DB 
 - ODOO_HOST 
 - ODOO_PORT 

