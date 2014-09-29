EGOSC + HEAT HA Demo
====================
 
.. contents:: Contents:
   :local: 
 
Create the Stack
----------------

1. Create the stack::

    jay@devstack1:~/src/jay-work/heat_egosc/service$ heat stack-create s1 --template-file=./sleep.scale.yml 
    +--------------------------------------+------------+--------------------+----------------------+
    | id                                   | stack_name | stack_status       | creation_time        |
    +--------------------------------------+------------+--------------------+----------------------+
    | 2c644400-da4c-4d2e-86d4-4113ecd4b891 | s1         | CREATE_IN_PROGRESS | 2014-09-29T08:17:53Z |
    +--------------------------------------+------------+--------------------+----------------------+

2. Check stack status, stack was created successfully::

    jay@devstack1:~/src/jay-work/heat_egosc/service$ heat stack-list
    +--------------------------------------+------------+-----------------+----------------------+
    | id                                   | stack_name | stack_status    | creation_time        |
    +--------------------------------------+------------+-----------------+----------------------+
    | 2c644400-da4c-4d2e-86d4-4113ecd4b891 | s1         | CREATE_COMPLETE | 2014-09-29T08:17:53Z |
    +--------------------------------------+------------+-----------------+----------------------+

3. EGO Services were created successfully, one hadm (Hadoop Master) and the other is hadc (Hadoop Compute), both of the two services have only one service instance::

    root@devstack1:/opt/sym71/eservice/esc/conf/services# egosh service list
    SERVICE  STATE    ALLOC CONSUMER RGROUP RESOURCE SLOTS SEQ_NO INST_STATE ACTI  
    hadc     STARTED  21    /Manage* Manag* devstac* 1     1      RUN        44    
    hadm     STARTED  20    /Manage* Manag* devstac* 1     1      RUN        43    
    WEBGUI   STARTED  2     /Manage* Manag* devstac* 1     1      RUN        38    
    ascd     STARTED  6     /Manage* Manag* devstac* 1     1      RUN        36    
    SD       STARTED  8     /Manage* Manag* devstac* 1     1      RUN        37 

Tigger HA for Service Instance
------------------------------

1. Check the process id for hadc service instance::
 
    root@devstack1:/opt/sym71/eservice/esc/conf/services# ps -ef | grep sleep
    root     21684 21683  0 16:18 ?        00:00:00 sleep 10000
    root     22087 22086  0 16:18 ?        00:00:00 sleep 10000
    root     22541 17496  0 16:18 ?        00:00:00 sleep 20
    root     22552  4285  0 16:18 pts/8    00:00:00 grep --color=auto sleep

2. Kill 22087::

    root@devstack1:/opt/sym71/eservice/esc/conf/services# kill -9 22087

3. Check service instance for hadc, its ACTI ID has been changed from 44 to 45, this means the service instance restart successfully::

    root@devstack1:/opt/sym71/eservice/esc/conf/services# egosh service list
    SERVICE  STATE    ALLOC CONSUMER RGROUP RESOURCE SLOTS SEQ_NO INST_STATE ACTI  
    hadc     STARTED  21    /Manage* Manag* devstac* 1     1      RUN        45    
    hadm     STARTED  20    /Manage* Manag* devstac* 1     1      RUN        43    
    WEBGUI   STARTED  2     /Manage* Manag* devstac* 1     1      RUN        38    
    ascd     STARTED  6     /Manage* Manag* devstac* 1     1      RUN        36    
    SD       STARTED  8     /Manage* Manag* devstac* 1     1      RUN        37  

Delete the Stack
----------------
 
1. Delete the stack::

    jay@devstack1:~/src/jay-work/heat_egosc/service$ heat stack-delete s1
    +--------------------------------------+------------+--------------------+----------------------+
    | id                                   | stack_name | stack_status       | creation_time        |
    +--------------------------------------+------------+--------------------+----------------------+
    | 2c644400-da4c-4d2e-86d4-4113ecd4b891 | s1         | DELETE_IN_PROGRESS | 2014-09-29T08:17:53Z |
    +--------------------------------------+------------+--------------------+----------------------+

2. Check delete result, the stack was deleted successfully::

    jay@devstack1:~/src/jay-work/heat_egosc/service$ heat stack-list
    +----+------------+--------------+---------------+
    | id | stack_name | stack_status | creation_time |
    +----+------------+--------------+---------------+
    +----+------------+--------------+---------------+

3. All of the services related to hadoop cluster was deleted::

    root@devstack1:/opt/sym71/eservice/esc/conf/services# egosh service list
    SERVICE  STATE    ALLOC CONSUMER RGROUP RESOURCE SLOTS SEQ_NO INST_STATE ACTI  
    WEBGUI   STARTED  2     /Manage* Manag* devstac* 1     1      RUN        38    
    ascd     STARTED  6     /Manage* Manag* devstac* 1     1      RUN        36    
    SD       STARTED  8     /Manage* Manag* devstac* 1     1      RUN        37   
