2. Edit the ``/etc/ruck/ruck.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://ruck:RUCK_DBPASS@controller/ruck
