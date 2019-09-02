#! /usr/bin/env python3

__author__ = "Luka Paulic <luka.paulic@sartura.hr>"

import sysrepo as sr
import sys
import logging
import subprocess as sp

# ================================= HELPER FUNCTIONS ==========================================
def numa_nodes_get(holder):
    p = sp.Popen(["numactl", "-H"], stdout=sp.PIPE)
    output, err = p.communicate()
    if (err):
        print(err)
    else:
        lines = output.decode().splitlines()
        node_count = int(lines[0].split(" ")[1])
        nodes = []
        values_count = 0
        # create aray of tuples, where each tuple holds data necessarty for each node
        for i in range(node_count):
            tup = ()
            for line in lines:
                if (line.startswith("node " + str(i) + " cpus:")):
                    tup = tup + tuple(line.split(" ")[3:])
                elif (line.startswith("node " + str(i) + " size:")):
                    tup = tup + (line.split(" ")[3],)
            values_count += len(tup)
            nodes.insert(i, tup)

        try:
            out_values = holder.allocate(values_count)
            index = 0
            val_index = 0

            for node in nodes:
                for i in range(len(node)-1):
                    out_values.val(val_index).set("/host-numa-pci:numa-topology/numa-nodes[numa-node='" + str(index) + "']/node-cpus", int(node[val_index]), sr.SR_UINT32_T)
                    val_index += 1
                out_values.val(val_index).set("/host-numa-pci:numa-topology/numa-nodes[numa-node='" + str(index) + "']/numa-node-mem", int(node[val_index]), sr.SR_UINT32_T)
                index += 1
        except Exception as e:
            logging.exception(e)

def interfaces_get(holder):
    p = sp.Popen(["lspci"], stdout=sp.PIPE)
    output, err = p.communicate()
    if (err):
        print(err)
    else:
        lines = output.decode().splitlines()
        index = 0
        for line in lines:
            if ("10-gigabit" not in line.lower()) or ("ethernet" not in line.lower()):
                continue
            try:
                pci_address = line.split(" ")[0]
                print(pci_address)
                values = holder.reallocate(index+1)
                values.val(index).set("/host-numa-pci:host-interfaces/interfaces[pci-addr='"+pci_address+"']/other-info", line[line.find(":")+1:], sr.SR_STRING_T)
                values.val(index).set("/host-numa-pci:host-interfaces/interfaces[pci-addr='"+pci_address+"']/int-type", "10-Gigabit", sr.SR_ENUM_T)
                index += 1
            except Exception as e:
                logging.exception(e)




# ================================= STATE DATA CALLBACK =======================================
def host_numa_pci_state_data(xpath, holder, request_id, original_xpath, private_ctx):
    print("\n\n ========== CALLBACK: STATE DATA ========== \n\n")
    print("Original XPATH: " + original_xpath)
    print("Current XPATH: " + xpath)

    last_node = xpath.split(":")[-1].split("/")[-1]
    print(last_node)

    if (last_node == "numa-nodes"):
        numa_nodes_get(holder)
    elif (last_node == "interfaces"):
        interfaces_get(holder)
    else:
        print("unsuported leaf node")

# ================================= INITIALIZATION ============================================
try:
    yang_module_name = "host-numa-pci"

    print("\n\n ========== Plugin started ========== \n\n")
    # create a connection to sysrepod
    connection = sr.Connection("numa-pci-state-data plugin")
    # start a session using the newly opened connection
    session = sr.Session(connection)
    # subscribe to events in the current session
    subscription = sr.Subscribe(session)

    print("\n\n ========== Plugin subscription ========== \n\n")

    subscription.dp_get_items_subscribe("/"+yang_module_name+":numa-topology", host_numa_pci_state_data, sr.SR_SUBSCR_DEFAULT)
    subscription.dp_get_items_subscribe("/"+yang_module_name+":host-interfaces", host_numa_pci_state_data, sr.SR_SUBSCR_DEFAULT)

    sr.global_loop()

    print("\n\n ========== Plugin exited ========== \n\n")

except Exception as e:
    logging.exception(e)

