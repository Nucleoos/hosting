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

{
    'name': 'Hosting',
    'version': '1.0',
    'category': 'Custom',
    'description': """Allow to very simply create and manage new OpenERP instances

You must configure your server for this module to work.
Note : Called commands are Debian specific

Packages :
    - Apache2
    - Supervisor
    - Virtualenv
    - Sudo
Filesystem (this module system user) :
    - Write access on configuration directories (openerp, supervisor and apache)
Filesystem (hosted instances system user) :
    - Write access on PostgreSQL PID directory
    - Write access on filestores directory
System (this module system user) :
    - Sudo right for "pg_createcluster"
    - Sudo right for "service apache2 reload"
Configuration :
    - Add supervisor configuration directory in the [include] section of /etc/supervisor/supervisord.conf
    - Add a file containing an Include directive for the apache configuration directory in /etc/apache2/conf.d/
    - Catchall DNS entry on *.dbname.domain.tld
    - Directive "NameVirtualHost" active for https on apache
    - Activate XML-RPC service on Supervisor
    - Activate apache2 mods : ssl, proxy_http, headers
""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [],
    'init_xml': [],
    'images': [],
    'update_xml': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'hosting_data.xml',
        'hosting_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
