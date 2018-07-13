import json
import yaml
from shutil import copyfile
import os

if not os.path.exists('./dist/'):
    os.makedirs('./dist/')


# Dictionary to map the BLOND appliance names to NILMTK
TYPE_MAPPER_DICT={
    'Dev Board':'ICT appliance',
    'Paper Shredder':'paper shredder',
    'Multi-Tool':'multi-function device',
    'Space Heater':'electric air heater',
    'Fan':'fan',
    'Battery Charger':'charger',
    'Monitor':'computer monitor',
    'Laptop':'laptop computer',
    'Kettle':'kettle',
    'USB Charger':'mobile phone charger',
    'Electric Toothbrush':'wireless phone charger',
    'PC':'desktop computer',
    'Daylight':'LED lamp',
    'Printer':'printer',
    'Projector':'projector',
    'Screen Motor':'motor'

}

# Dictionary to count instance numers for appliances
INSTANCE_COUNT_DICT={
    'ICT appliance':1,
    'paper shredder':1,
    'multi-function device':1,
    'electric air heater':1,
    'fan':1,
    'charger':1,
    'computer monitor':1,
    'laptop computer':1,
    'kettle':1,
    'mobile phone charger':1,
    'wireless phone charger':1,
    'desktop computer':1,
    'LED lamp':1,
    'printer':1,
    'projector':1,
    'motor':1
}

# Dictionary to map the BLOND circuit to the NILMTK format
MEDAL_TO_PHASE_DICT = dict.fromkeys([1,2,3,7,12],1)
MEDAL_TO_PHASE_DICT.update(dict.fromkeys([6,10,11,13,14],2))
MEDAL_TO_PHASE_DICT.update(dict.fromkeys([4,5,8,9,15],3))


"""Build the appliances from the json log to a NILMTK format for a given Socket.
Args:
   medalIndex(Int): The current MEDAL number.
   socketIndex(Int): The current Socket index.
   entries(List): The current MEDAL of the json log.
Returns:
    A list of NILMTK appliance entries for this socket.
"""

def buildAppliancesForSocket(medalIndex, socketIndex, entries):
    socketName = 'socket_'+str(socketIndex)
    socketEntries = []

    for entry in entries:
        socketEntries.append({
            'appliance': entry[socketName],
            'start': entry['timestamp']
        })

    # Remove duplicates ignoring the timestamp
    st = set()
    clone_socketEntries = socketEntries[:]
    for entry in clone_socketEntries:
        if entry['appliance']['appliance_name'] in st:
            socketEntries.remove(entry)
        st.add(entry['appliance']['appliance_name'])


    for i, entry in enumerate(socketEntries):
        if (i+2) < len(socketEntries):
            entry['end'] = socketEntries[i+1]['start']
        else:
            entry['end'] = '2017-06-30T00-00-00'
    appliances = []
    for socket in socketEntries:
        if not socket['appliance']['appliance_name'] == None:
            appl_type = TYPE_MAPPER_DICT.get(str(socket['appliance']['class_name']))
            appl_ins = INSTANCE_COUNT_DICT.get(appl_type)
            
            appliances.append({
                'type': TYPE_MAPPER_DICT.get(str(socket['appliance']['class_name'])),
                'instance': appl_ins,
                'meters': [((medalIndex-1)*6)+socketIndex + 3],
                'max_power': int(socket['appliance']['power'][:-1]) if socket['appliance']['power'] else 0,
                'original_name': str(socket['appliance']['appliance_name']) + ' - ' + str(socket['appliance']['class_name']),
                'dates_active': [{ 'start': str(socket['start']), 'end': str(socket['end']) }]
            })
            INSTANCE_COUNT_DICT[appl_type] += 1

    return appliances




"""Gets all NILMTK appliances from the json log for the this MEDAL.
Args:
   medalIndex(Int): The curent MEDAL number.
Returns:
    A list of NILMTK appliance entries for the MEDAL index.
"""

def buildAppliancesForMedal(medalIndex):
    entries = d['MEDAL-'+str(medalIndex)]['entries']

    appliances = []

    for i in range(1, 7):
        appliance_new =buildAppliancesForSocket(medalIndex, i, entries)
        appliances.extend(appliance_new)
        
    return appliances


with open('appliance_log.json') as json_data:
    d = json.load(json_data)
    appliances = []
    for i in range(1, 16):
        appliance_new = buildAppliancesForMedal(i)
        appliances.extend(appliance_new)

    elec_meters = {}
    
    medal = { 'device_model': 'medal' }
    clear = { 'device_model' : 'clear', 'site_meter' : True}

    # First 3 phases for CLEAR unit
    for i in range(1,4):
        elec_meters[i] = clear
    # 4-93 phases to the Sockets
    for medalIndex in range(1,16):
        medal_tmp = medal.copy()
        medal_tmp['submeter_of'] = MEDAL_TO_PHASE_DICT[medalIndex]
        for socketIndex in range(1,7):
            meter = ((medalIndex-1)*6)+socketIndex
            elec_meters[meter + 3] = medal_tmp
            

    yaml_data = {
        'instance': 1,
        'original_name': 'office',
        'elec_meters': elec_meters,
        'appliances': appliances
    }

    with open('dist/building1.yaml', 'w') as outfile:
        yaml.dump(yaml_data, outfile, default_flow_style=False)

    copyfile('dataset.yml', 'dist/dataset.yaml')
    copyfile('meter_devices.yml', 'dist/meter_devices.yaml')

