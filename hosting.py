# -*- coding: utf-8 -*-
##############################################################################
#
#    hosting module for OpenERP, Allow to very simply create and manage new OpenERP instances
#    Copyright (C) 2014 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of hosting
#
#    hosting is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    hosting is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import getpass
from openerp.osv import orm
from openerp.osv import fields


class HostingInstance(orm.Model):
    _name = 'hosting.instance'
    _description = 'Hosting Instance'

    def _get_instance_values(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        for instance in self.browse(cr, uid, ids, context=context):
            instance_name = instance.variant_id.server_id.prefix + str(instance.id)
            result[instance.id] = {
                'name': instance_name,
                'oerp_port': instance.variant_id.server_id.oerp_start_port + instance.id,
                'postgresql_port': instance.variant_id.server_id.postgresql_start_port + instance.id,
                'username': instance_name,
                'filestore_path': '%s/%s' % (instance.variant_id.server_id.filestores_path, instance_name),
            }

        return result

    _columns = {
        'name': fields.function(_get_instance_values, method=True, string='Name', type='char', store=False, size=64, multi='values', help='Name of the hosted instance'),
        'variant_id': fields.many2one('hosting.variant', 'Variant', required=True, help='Variant used by this instance'),
        'oerp_port': fields.function(_get_instance_values, method=True, string='OpenERP Port', type='integer', store=False, multi='values', help='Port used for OpenERP by this instance'),
        'postgresql_port': fields.function(_get_instance_values, method=True, string='PostgreSQL Port', type='integer', store=False, multi='values', help='Port used for PostgreSQL by this instance'),
        'username': fields.function(_get_instance_values, method=True, string='Username', type='char', store=False, size=64, multi='values', help='Username linked to this instance'),
        'filestore_path': fields.function(_get_instance_values, method=True, string='Filestore Path', type='char', store=False, size=512, multi='values', help='Path of the filestore for this instance'),
    }

    def create(self, cr, uid, values, context=None):
        id = super(HostingInstance, self).create(cr, uid, values, context=context)
        # TODO :
            # Create PostgreSQL cluster : sudo pg_createcluster <version> <prefix+id> -p <pg_start_port+id> --start
            # Create PostgreSQL user (on new cluster)
            # Create OpenERP configuration file
            # Create Supervisor configuration file
            # Create apache2 vhost file
            # Start new OpenERP instance
            # Reread Supervisor configuration
            # Activate apache2 vhost
            # Reload apache configuration
        return id

    def write(self, cr, uid, ids, values, context=None):
        res = super(HostingInstance, self).write(cr, uid, ids, values, context=context)
        # TODO :
            # Update OpenERP configuration file
            # Update Supervisor configuration file
            # Update apache2 vhost file
            # Update PostgreSQL user
            # Reload Supervisor configuration
            # Restart OpenERP instance
            # Reload apache configuration
        return res

    def update_configuration_files(self, cr, uid, ids, context=None):
        return True


class HostingVersion(orm.Model):
    _name = 'hosting.version'
    _description = 'Hosting Version'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of the version'),
        'oerp_template': fields.text('OpenERP Template', required=True, help='OpenERP Template configuration'),
        'supervisor_template': fields.text('Supervisor Template', required=True, help='Supervisor Template configuration'),
        'apache_template': fields.text('Apache Template', required=True, help='Apache Template configuration'),
    }


class HostingVariant(orm.Model):
    _name = 'hosting.variant'
    _description = 'Hosting Variant'

    def _get_variant_values(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        for variant in self.browse(cr, uid, ids, context=context):
            result[variant.id] = {
                'variant_path': '%s/%s' % (variant.server_id.variants_path, variant.name),
                'virtualenv_path': '%s/%s' % (variant.server_id.virtualenvs_path, variant.name),
            }

        return result

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of the hosted variant'),
        'server_id': fields.many2one('hosting.server', 'Server', required=True, help='Server where this variant is available'),
        'instance_ids': fields.one2many('hosting.instance', 'variant_id', 'Instances', help='Instances created using this variant'),
        'version_id': fields.many2one('hosting.version', 'Version', required=True, help='OpenERP version used by this variant'),
        'variant_path': fields.function(_get_variant_values, method=True, string='Variant Path', type='char', store=False, size=512, multi='values', help='Path of the variant'),
        'virtualenv_path': fields.function(_get_variant_values, method=True, string='Virtualenv Path', type='char', store=False, size=512, multi='values', help='Path of the virtualenv'),
        'oerp_template': fields.text('OpenERP Config File Template', required=True, help='Template for the configuration file of OpenERP'),
        'supervisor_template': fields.text('Supervisor Config File Template', required=True, help='Template for the configuration file of Supervisor'),
        'apache_template': fields.text('Apache Config File Template', required=True, help='Template for the configuration file of Apache'),
    }

    def write(self, cr, uid, ids, values, context=None):
        res = super(HostingVariant, self).write(cr, uid, ids, values, context=context)

        instance_ids = [instance.id for variant in self.browse(cr, uid, ids, context=context) for instance in variant.instance_ids]
        self.pool.get('hosting.instance').update_configuration_files(cr, uid, instance_ids, context=context)

        return res

    def onchange_version_id(self, cr, uid, ids, version_id, context=None):
        """
        Change the default configuration files contents from version
        """
        if not version_id:
            return {}

        version_obj = self.pool.get('hosting.version')
        version = version_obj.browse(cr, uid, version_id, context=context)

        return {
            'value': {
                'oerp_template': version.oerp_template,
                'supervisor_template': version.supervisor_template,
                'apache_template': version.apache_template,
            },
            'warning': {
                'title': 'Automatic change',
                'message': 'The configuration file templates have changed, you may have to check the contents',
            },
        }


class HostingServer(orm.Model):
    _name = 'hosting.server'
    _description = 'Hosting Server'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of the hosting server'),
        'apache_port': fields.integer('Apache Port', required=True, help='Port used on apache for https'),
        'oerp_start_port': fields.integer('OpenERP Start Port', required=True, help='First port used for instances on this server'),
        'postgresql_start_port': fields.integer('PostgreSQL Start Port', required=True, help='First port used for instance clusters on this server'),
        'system_username': fields.char('System Username', size=64, required=True, help='User who will run the OpenERP instances'),
        'prefix': fields.char('Prefix', size=16, required=True, help='Prefix used for the instance specific names on this server'),
        'domain_name': fields.char('Domain Name', size=64, required=True, help='Domain name used to access instances on this server'),
        'postgresql_version': fields.char('PostgreSQL Version', size=64, required=True, help='Version of PostgreSQL used on this server'),
        'variant_ids': fields.one2many('hosting.variant', 'server_id', 'Variants', help='List of variants available on this server'),
        'supervisor_port': fields.integer('Supervisor Port', required=True, help='Port for supervisor administration on this server'),
        'supervisor_username': fields.char('Supervisor Username', size=64, required=True, help='Username for supervisor administration on this server'),
        'supervisor_password': fields.char('Supervisor Password', size=64, required=True, help='Password for supervisor administration on this server'),
        'variants_path': fields.char('Variants Path', size=512, required=True, help='Directory where OpenERP variants will be stored'),
        'virtualenvs_path': fields.char('Virtualenvs Path', size=512, required=True, help='Directory where OpenERP virtualenvs will be stored'),
        'filestores_path': fields.char('Filestores Path', size=512, required=True, help='Directory where OpenERP instance filestores will be stored'),
        'oerp_path': fields.char('OpenERP Path', size=512, required=True, help='Directory where OpenERP configuration files will be stored'),
        'supervisor_path': fields.char('Supervisor Path', size=512, required=True, help='Directory where Supervisor configuration files will be stored'),
        'apache_path': fields.char('Apache Path', size=512, required=True, help='Directory where Apache configuration files will be stored'),
    }

    _defaults = {
        'apache_port': 443,
        'supervisor_port': 9001,
        'oerp_start_port': 10000,
        'postgresql_start_port': 20000,
        'system_username': getpass.getuser(),
        'prefix': lambda self, cr, uid, context=None: cr.dbname,
        'domain_name': 'example.com',
        'postgresql_version': '9.1',
        'variants_path': '/srv/openerp/hosting/variants',
        'virtualenvs_path': '/srv/openerp/hosting/virtualenvs',
        'filestores_path': '/srv/openerp/hosting/filestores',
        'oerp_path': '/etc/openerp.d',
        'supervisor_path': '/etc/supervisor/conf.d',
        'apache_path': '/etc/apache2/sites-available',
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
