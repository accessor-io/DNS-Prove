Command Line Interface
=====================

Interactive Mode
--------------

Start the interactive CLI:

.. code-block:: bash

   dns-prove

Available Commands
----------------

verify
~~~~~~
Verify a domain's DNS records:

.. code-block:: bash

   verify example.eth
   v example.eth  # Short form

batch
~~~~~
Process multiple domains from a file:

.. code-block:: bash

   batch domains.txt [output.json]
   b domains.txt  # Short form

network
~~~~~~~
Switch between networks:

.. code-block:: bash

   network mainnet
   n testnet  # Short form

status
~~~~~~
Show current status and settings:

.. code-block:: bash

   status
   s  # Short form

Command Aliases
-------------

========  ===========
Alias     Command
========  ===========
v         verify
b         batch
n         network
s         status
c         config
r         resolve
e         export
q         quit
clear     cache clear
stats     cache stats
========  =========== 