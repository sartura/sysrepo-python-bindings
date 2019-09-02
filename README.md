# sysrepo-python-bindings
Repository for working on examples using python and sysrepo. This README is intended for Python 3 plugin development.

A basic Python 3 plugin layout will be presented and explained.

## Content
* Generic plugin code layout
* Application specific code layout

## Generic plugin code layout
A generic example code in Python 3 listed below show how to initialize a plugin and subscribe to operational (state) data

```python {.line-numbers}
import sysrepo as sr

yang_module_name = "yang_module_name"

connection = sr.Connection("Arbitrary_name_of_the_connection")
session = sr.Session(connection)
subscription = sr.Subscribe(session)

# subscription for operational data
subscription.dp_get_items_subscribe("/"+yang_module_name+":operational-data-container", module_operational_data_callback, None, sr.SR_SUBSCR_DEFAULT)
# subscription for module change
subscription.module_change_subscribe(yang_module_name, module_change_callback, None, 0, sr.SR_SUBSCR_DEFAULT)
# subscription for RPC calls
subscribe.rpc_subscribe_tree("/"+yang_module_name+":rpc-container", rpc_tree_callback, None, sr.SR_SUBSCR_DEFAULT)

sr.global_loop()

```

The first step is to create a connection to the sysrepo daemon. For that we use the .Connection constructor defined in the sysrepo package.
After a connection has been made we can initiate a session. For initializing a session we call the .Session constructor and pass it the connection object.
After we initialize a session we can create a subscription object which will be used for subscribing to different events. To create a subscription object
we call the .Subscribe constructor and pass it the previously created session object.

After the previously described three steps to initiate the subscription object we proceed to add subscriptions. In the code above three types of subscriptions are described, for more possible
subscriptions please refer to the [C++/Python documentation](http://www.sysrepo.org/static/doc/html/group__classes.html). To subscribe for receiving notification for operational data requests
we use the .dp_get_items_subscribe method of the subscription object. The method requires a string identifying the container which has the 'config' option set to 'false'. additionally it requires
a callback function to be called when an event occurs. Additionally we can specify a private context to be sent to the callback and the subscription options.

For the module change subscription we specify the module name that for which we want to monitor the changes that happen. Also we need to specify the callback function to be called when an module change event occurs.
Additional parameters are again a private context to be passed to the callback function, priority for the callback if we happen to have multiple modules which we need to monitor and the subscription options.

For the rpc_subscribe_tree parameter list is identical to the one for the operational data subscribe function. The only difference is that that for the first parameter we need to specify the path to the YANG RPC
block for which we want to receive events.

## Application specific code layout
The application specific part is related to the implementation for the callbacks. Each application has YANG modules that need to be monitored and different ways to handle data for different events.
For an example please refer to the numa-pci-state-data.py plugin.