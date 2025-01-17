#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2012, Mark Theunissen <mark.theunissen@gmail.com>
# Sponsored by Four Kitchens http://fourkitchens.com.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mysql_user
short_description: Adds or removes a user from a MySQL database
description:
   - Adds or removes a user from a MySQL database.
options:
  name:
    description:
      - Name of the user (role) to add or remove.
    type: str
    required: true
  password:
    description:
      - Set the user's password.
    type: str
  encrypted:
    description:
      - Indicate that the 'password' field is a `mysql_native_password` hash.
    type: bool
    default: no
  host:
    description:
      - The 'host' part of the MySQL username.
    type: str
    default: localhost
  host_all:
    description:
      - Override the host option, making ansible apply changes
        to all hostnames for a given user.
      - This option cannot be used when creating users.
    type: bool
    default: no
  priv:
    description:
      - "MySQL privileges string in the format: C(db.table:priv1,priv2)."
      - "Multiple privileges can be specified by separating each one using
        a forward slash: C(db.table:priv/db.table:priv)."
      - The format is based on MySQL C(GRANT) statement.
      - Database and table names can be quoted, MySQL-style.
      - If column privileges are used, the C(priv1,priv2) part must be
        exactly as returned by a C(SHOW GRANT) statement. If not followed,
        the module will always report changes. It includes grouping columns
        by permission (C(SELECT(col1,col2)) instead of C(SELECT(col1),SELECT(col2))).
      - Can be passed as a dictionary (see the examples).
      - Supports GRANTs for procedures and functions (see the examples).
    type: raw
  append_privs:
    description:
      - Append the privileges defined by priv to the existing ones for this
        user instead of overwriting existing ones.
    type: bool
    default: no
  tls_requires:
    description:
      - Set requirement for secure transport as a dictionary of requirements (see the examples).
      - Valid requirements are SSL, X509, SUBJECT, ISSUER, CIPHER.
      - SUBJECT, ISSUER and CIPHER are complementary, and mutually exclusive with SSL and X509.
      - U(https://mariadb.com/kb/en/securing-connections-for-client-and-server/#requiring-tls).
    type: dict
    version_added: 1.0.0
  sql_log_bin:
    description:
      - Whether binary logging should be enabled or disabled for the connection.
    type: bool
    default: yes
  state:
    description:
      - Whether the user should exist.
      - When C(absent), removes the user.
    type: str
    choices: [ absent, present ]
    default: present
  check_implicit_admin:
    description:
      - Check if mysql allows login as root/nopassword before trying supplied credentials.
      - If success, passed I(login_user)/I(login_password) will be ignored.
    type: bool
    default: no
  update_password:
    description:
      - C(always) will update passwords if they differ.
      - C(on_create) will only set the password for newly created users.
    type: str
    choices: [ always, on_create ]
    default: always
  plugin:
    description:
      - User's plugin to authenticate (``CREATE USER user IDENTIFIED WITH plugin``).
    type: str
    version_added: '0.1.0'
  plugin_hash_string:
    description:
      - User's plugin hash string (``CREATE USER user IDENTIFIED WITH plugin AS plugin_hash_string``).
    type: str
    version_added: '0.1.0'
  plugin_auth_string:
    description:
      - User's plugin auth_string (``CREATE USER user IDENTIFIED WITH plugin BY plugin_auth_string``).
    type: str
    version_added: '0.1.0'
  resource_limits:
    description:
      - Limit the user for certain server resources. Provided since MySQL 5.6 / MariaDB 10.2.
      - "Available options are C(MAX_QUERIES_PER_HOUR: num), C(MAX_UPDATES_PER_HOUR: num),
        C(MAX_CONNECTIONS_PER_HOUR: num), C(MAX_USER_CONNECTIONS: num)."
      - Used when I(state=present), ignored otherwise.
    type: dict
    version_added: '0.1.0'

notes:
   - "MySQL server installs with default I(login_user) of C(root) and no password.
     To secure this user as part of an idempotent playbook, you must create at least two tasks:
     1) change the root user's password, without providing any I(login_user)/I(login_password) details,
     2) drop a C(~/.my.cnf) file containing the new root credentials.
     Subsequent runs of the playbook will then succeed by reading the new credentials from the file."
   - Currently, there is only support for the C(mysql_native_password) encrypted password hash module.
   - Supports (check_mode).

seealso:
- module: community.mysql.mysql_info
- name: MySQL access control and account management reference
  description: Complete reference of the MySQL access control and account management documentation.
  link: https://dev.mysql.com/doc/refman/8.0/en/access-control.html
- name: MySQL provided privileges reference
  description: Complete reference of the MySQL provided privileges documentation.
  link: https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html

author:
- Jonathan Mainguy (@Jmainguy)
- Benjamin Malynovytch (@bmalynovytch)
- Lukasz Tomaszkiewicz (@tomaszkiewicz)
extends_documentation_fragment:
- community.mysql.mysql

'''

EXAMPLES = r'''
- name: Removes anonymous user account for localhost
  community.mysql.mysql_user:
    name: ''
    host: localhost
    state: absent

- name: Removes all anonymous user accounts
  community.mysql.mysql_user:
    name: ''
    host_all: yes
    state: absent

- name: Create database user with name 'bob' and password '12345' with all database privileges
  community.mysql.mysql_user:
    name: bob
    password: 12345
    priv: '*.*:ALL'
    state: present

- name: Create database user using hashed password with all database privileges
  community.mysql.mysql_user:
    name: bob
    password: '*EE0D72C1085C46C5278932678FBE2C6A782821B4'
    encrypted: yes
    priv: '*.*:ALL'
    state: present

- name: Create database user with password and all database privileges and 'WITH GRANT OPTION'
  community.mysql.mysql_user:
    name: bob
    password: 12345
    priv: '*.*:ALL,GRANT'
    state: present

- name: Create user with password, all database privileges and 'WITH GRANT OPTION' in db1 and db2
  community.mysql.mysql_user:
    state: present
    name: bob
    password: 12345dd
    priv:
      'db1.*': 'ALL,GRANT'
      'db2.*': 'ALL,GRANT'

# Use 'PROCEDURE' instead of 'FUNCTION' to apply GRANTs for a MySQL procedure instead.
- name: Grant a user the right to execute a function
  community.mysql.mysql_user:
    name: readonly
    password: 12345
    priv:
      FUNCTION my_db.my_function: EXECUTE
    state: present

# Note that REQUIRESSL is a special privilege that should only apply to *.* by itself.
# Setting this privilege in this manner is deprecated.
# Use 'tls_requires' instead.
- name: Modify user to require SSL connections
  community.mysql.mysql_user:
    name: bob
    append_privs: yes
    priv: '*.*:REQUIRESSL'
    state: present

- name: Modify user to require TLS connection with a valid client certificate
  community.mysql.mysql_user:
    name: bob
    tls_requires:
      x509:
    state: present

- name: Modify user to require TLS connection with a specific client certificate and cipher
  community.mysql.mysql_user:
    name: bob
    tls_requires:
      subject: '/CN=alice/O=MyDom, Inc./C=US/ST=Oregon/L=Portland'
      cipher: 'ECDHE-ECDSA-AES256-SHA384'

- name: Modify user to no longer require SSL
  community.mysql.mysql_user:
    name: bob
    tls_requires:

- name: Ensure no user named 'sally'@'localhost' exists, also passing in the auth credentials
  community.mysql.mysql_user:
    login_user: root
    login_password: 123456
    name: sally
    state: absent

# check_implicit_admin example
- name: >
    Ensure no user named 'sally'@'localhost' exists, also passing in the auth credentials.
    If mysql allows root/nopassword login, try it without the credentials first.
    If it's not allowed, pass the credentials
  community.mysql.mysql_user:
    check_implicit_admin: yes
    login_user: root
    login_password: 123456
    name: sally
    state: absent

- name: Ensure no user named 'sally' exists at all
  community.mysql.mysql_user:
    name: sally
    host_all: yes
    state: absent

- name: Specify grants composed of more than one word
  community.mysql.mysql_user:
    name: replication
    password: 12345
    priv: "*.*:REPLICATION CLIENT"
    state: present

- name: Revoke all privileges for user 'bob' and password '12345'
  community.mysql.mysql_user:
    name: bob
    password: 12345
    priv: "*.*:USAGE"
    state: present

# Example privileges string format
# mydb.*:INSERT,UPDATE/anotherdb.*:SELECT/yetanotherdb.*:ALL

- name: Example using login_unix_socket to connect to server
  community.mysql.mysql_user:
    name: root
    password: abc123
    login_unix_socket: /var/run/mysqld/mysqld.sock

- name: Example of skipping binary logging while adding user 'bob'
  community.mysql.mysql_user:
    name: bob
    password: 12345
    priv: "*.*:USAGE"
    state: present
    sql_log_bin: no

- name: Create user 'bob' authenticated with plugin 'AWSAuthenticationPlugin'
  community.mysql.mysql_user:
    name: bob
    plugin: AWSAuthenticationPlugin
    plugin_hash_string: RDS
    priv: '*.*:ALL'
    state: present

- name: Limit bob's resources to 10 queries per hour and 5 connections per hour
  community.mysql.mysql_user:
    name: bob
    resource_limits:
      MAX_QUERIES_PER_HOUR: 10
      MAX_CONNECTIONS_PER_HOUR: 5

# Example .my.cnf file for setting the root password
# [client]
# user=root
# password=n<_665{vS43y
'''

RETURN = '''#'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.mysql.plugins.module_utils.database import SQLParseError
from ansible_collections.community.mysql.plugins.module_utils.mysql import (
    mysql_connect, mysql_driver, mysql_driver_fail_msg, mysql_common_argument_spec
)
from ansible_collections.community.mysql.plugins.module_utils.user import (
    convert_priv_dict_to_str,
    get_impl,
    get_mode,
    handle_requiressl_in_priv_string,
    InvalidPrivsError,
    limit_resources,
    privileges_unpack,
    sanitize_requires,
    user_add,
    user_delete,
    user_exists,
    user_mod,
)
from ansible.module_utils._text import to_native


# ===========================================
# Module execution.
#


def main():
    argument_spec = mysql_common_argument_spec()
    argument_spec.update(
        user=dict(type='str', required=True, aliases=['name']),
        password=dict(type='str', no_log=True),
        encrypted=dict(type='bool', default=False),
        host=dict(type='str', default='localhost'),
        host_all=dict(type="bool", default=False),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        priv=dict(type='raw'),
        tls_requires=dict(type='dict'),
        append_privs=dict(type='bool', default=False),
        check_implicit_admin=dict(type='bool', default=False),
        update_password=dict(type='str', default='always', choices=['always', 'on_create'], no_log=False),
        sql_log_bin=dict(type='bool', default=True),
        plugin=dict(default=None, type='str'),
        plugin_hash_string=dict(default=None, type='str'),
        plugin_auth_string=dict(default=None, type='str'),
        resource_limits=dict(type='dict'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    login_user = module.params["login_user"]
    login_password = module.params["login_password"]
    user = module.params["user"]
    password = module.params["password"]
    encrypted = module.boolean(module.params["encrypted"])
    host = module.params["host"].lower()
    host_all = module.params["host_all"]
    state = module.params["state"]
    priv = module.params["priv"]
    tls_requires = sanitize_requires(module.params["tls_requires"])
    check_implicit_admin = module.params["check_implicit_admin"]
    connect_timeout = module.params["connect_timeout"]
    config_file = module.params["config_file"]
    append_privs = module.boolean(module.params["append_privs"])
    update_password = module.params['update_password']
    ssl_cert = module.params["client_cert"]
    ssl_key = module.params["client_key"]
    ssl_ca = module.params["ca_cert"]
    check_hostname = module.params["check_hostname"]
    db = ''
    sql_log_bin = module.params["sql_log_bin"]
    plugin = module.params["plugin"]
    plugin_hash_string = module.params["plugin_hash_string"]
    plugin_auth_string = module.params["plugin_auth_string"]
    resource_limits = module.params["resource_limits"]
    if priv and not isinstance(priv, (str, dict)):
        module.fail_json(msg="priv parameter must be str or dict but %s was passed" % type(priv))

    if priv and isinstance(priv, dict):
        priv = convert_priv_dict_to_str(priv)

    if priv and "REQUIRESSL" in priv:
        priv, tls_requires = handle_requiressl_in_priv_string(module, priv, tls_requires)

    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)

    cursor = None
    try:
        if check_implicit_admin:
            try:
                cursor, db_conn = mysql_connect(module, "root", "", config_file, ssl_cert, ssl_key, ssl_ca, db,
                                                connect_timeout=connect_timeout, check_hostname=check_hostname)
            except Exception:
                pass

        if not cursor:
            cursor, db_conn = mysql_connect(module, login_user, login_password, config_file, ssl_cert, ssl_key, ssl_ca, db,
                                            connect_timeout=connect_timeout, check_hostname=check_hostname)
    except Exception as e:
        module.fail_json(msg="unable to connect to database, check login_user and login_password are correct or %s has the credentials. "
                             "Exception message: %s" % (config_file, to_native(e)))

    if not sql_log_bin:
        cursor.execute("SET SQL_LOG_BIN=0;")

    get_impl(cursor)

    if priv is not None:
        try:
            mode = get_mode(cursor)
        except Exception as e:
            module.fail_json(msg=to_native(e))
        try:
            priv = privileges_unpack(priv, mode)
        except Exception as e:
            module.fail_json(msg="invalid privileges string: %s" % to_native(e))

    if state == "present":
        if user_exists(cursor, user, host, host_all):
            try:
                if update_password == "always":
                    changed, msg = user_mod(cursor, user, host, host_all, password, encrypted,
                                            plugin, plugin_hash_string, plugin_auth_string,
                                            priv, append_privs, tls_requires, module)
                else:
                    changed, msg = user_mod(cursor, user, host, host_all, None, encrypted,
                                            plugin, plugin_hash_string, plugin_auth_string,
                                            priv, append_privs, tls_requires, module)

            except (SQLParseError, InvalidPrivsError, mysql_driver.Error) as e:
                module.fail_json(msg=to_native(e))
        else:
            if host_all:
                module.fail_json(msg="host_all parameter cannot be used when adding a user")
            try:
                changed = user_add(cursor, user, host, host_all, password, encrypted,
                                   plugin, plugin_hash_string, plugin_auth_string,
                                   priv, tls_requires, module.check_mode)
                if changed:
                    msg = "User added"

            except (SQLParseError, InvalidPrivsError, mysql_driver.Error) as e:
                module.fail_json(msg=to_native(e))

        if resource_limits:
            changed = limit_resources(module, cursor, user, host, resource_limits, module.check_mode) or changed

    elif state == "absent":
        if user_exists(cursor, user, host, host_all):
            changed = user_delete(cursor, user, host, host_all, module.check_mode)
            msg = "User deleted"
        else:
            changed = False
            msg = "User doesn't exist"
    module.exit_json(changed=changed, user=user, msg=msg)


if __name__ == '__main__':
    main()
