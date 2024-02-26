Prerequisites
-------------

Before you install and configure the ruck service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``ruck`` database:

     .. code-block:: none

        CREATE DATABASE ruck;

   * Grant proper access to the ``ruck`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON ruck.* TO 'ruck'@'localhost' \
          IDENTIFIED BY 'RUCK_DBPASS';
        GRANT ALL PRIVILEGES ON ruck.* TO 'ruck'@'%' \
          IDENTIFIED BY 'RUCK_DBPASS';

     Replace ``RUCK_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``ruck`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt ruck

   * Add the ``admin`` role to the ``ruck`` user:

     .. code-block:: console

        $ openstack role add --project service --user ruck admin

   * Create the ruck service entities:

     .. code-block:: console

        $ openstack service create --name ruck --description "ruck" ruck

#. Create the ruck service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        ruck public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        ruck internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        ruck admin http://controller:XXXX/vY/%\(tenant_id\)s
