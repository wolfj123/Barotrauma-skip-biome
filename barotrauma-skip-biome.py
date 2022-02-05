
import xml.etree.ElementTree as ET
import sys
import os

# https://barotraumagame.com/wiki/Biomes
biomes = ['coldcaverns', 'europanridge', 'theaphoticplateau', 'thegreatsea', 'hydrothermalwastes']
JOVIAN_RADIATION_STEP = 100


# DEFAULT CONFIG    
update_jovian_radiation = True
jovian_radiation_distance = 3 * JOVIAN_RADIATION_STEP
update_discoverability_of_prev_biomes = True
unlock_biome_passages = True

def read_config():
    global update_jovian_radiation
    global jovian_radiation_distance
    global update_discoverability_of_prev_biomes
    global unlock_biome_passages

    curr_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_name = 'config.xml'
    config_file_path = os.path.join(curr_dir, config_file_name)

    try:
        config_tree = ET.parse(config_file_path)
        config_root = config_tree.getroot() 
        
        for radiation in config_root.iter('Radiation'):
            for enable in radiation.iter('update'):
                update_jovian_radiation = (enable.attrib['value'] == "true")
                print('Jovian Radiation update set to: {v}'.format(v = update_jovian_radiation))

            if update_jovian_radiation:
                for distance in radiation.iter('distance'):
                    jovian_radiation_distance = int(distance.attrib['value'])
                    print('Jovian Radiation distance from the sub set to: {v}'.format(v = jovian_radiation_distance))

        for discoverabilty in config_root.iter('Discoverabilty'):
            for enable in discoverabilty.iter('update'):
                update_discoverability_of_prev_biomes = (enable.attrib['value'] == "true")
                print('Updating visibility over previous biomes set to: {v}'.format(v = update_discoverability_of_prev_biomes))

        for gates in config_root.iter('Gates'):
            for enable in gates.iter('update'):
                unlock_biome_passages = (enable.attrib['value'] == "true") 
                print('Unlocking passage ways to previous biomes set to: {v}'.format(v = unlock_biome_passages))
            
    except Exception as e:
        # print(e)
        return   

def findAllLocations(root):
    locations = {}
    for loc in root.iter('location'):
        location_index = int(loc.attrib['i'])
        locations[location_index] = loc
    return locations

def findConnectionToBiome(locations, biome):
    if biome == biomes[0]:
        return
    
    prev_biome = biomes[biomes.index(biome) - 1]
    last_location_in_prev_biome = None
    for loc in locations:
        level = locations[loc].find('Level')
        if level.attrib['biome'] == prev_biome:
            if locations[loc].attrib['isgatebetweenbiomes'] == "true":
                last_location_in_prev_biome = locations[loc]
                break
    last_location_in_prev_biome_index = int(last_location_in_prev_biome.attrib['i'])

    for connection in root.iter('connection'):
        connection_locations = connection.attrib['locations'].split(',')
        for idx, con_loc in enumerate(connection_locations):
            if int(con_loc) == last_location_in_prev_biome_index and connection.attrib['biome'] == biome:
                return connection          

def findAllConnectionsBetweenBiomes(locations):
    connection_between_biomes = []
    for biome in biomes[1:]:
        connection_between_biomes.append(findConnectionToBiome(locations, biome))
    return connection_between_biomes  

def setDiscoveredInLocations(locations, discovered):
    for loc in locations:
        locations[loc].attrib['discovered'] = str(discovered).lower()

def getAllLocationsInBiome(locations, biome):
    result = {}
    for loc in locations:
        level = locations[loc].find('Level')
        if level.attrib['biome'] == biome:
            result[loc] = locations[loc]
    
    return result

def discoverAllPrevBiomes(locations, biome):
    setDiscoveredInLocations(locations, False)

    prev_biomes = biomes[:biomes.index(biome)]
    for prev_biome in prev_biomes:
        biome_locations = getAllLocationsInBiome(locations, prev_biome)
        setDiscoveredInLocations(biome_locations, True)

def getFirstLocation(locations):
    min_loc = locations[0]
    for loc in locations:
        curr_min_level = min_loc.find('Level')
        level = locations[loc].find('Level')
        if float(level.attrib['difficulty']) < float(curr_min_level.attrib['difficulty']):
            min_loc = locations[loc]
    return min_loc

def getFirstLocationInBiome(locations, connection_between_biomes, biome):
    if biome == biomes[0]:
        return getFirstLocation(locations)

    connection = connection_between_biomes[biomes.index(biome) - 1]
    locations_indices_in_connection = connection.attrib['locations'].split(',')
    for loc_idx in locations_indices_in_connection:
        loc = locations[int(loc_idx)]
        loc_biome = loc.find('Level').attrib['biome']
        if loc_biome == biome:
            return loc

def updateCurrentLocation(location):
    location_index = int(location.attrib['i'])
    for map in root.iter('map'):
        map.attrib['currentlocation'] = str(location_index)

def updateJovianRadiation(location):
    location_x = float(location.attrib['position'].split(',')[0])
    new_jovian_radiotion_location = int(location_x - jovian_radiation_distance)
    for radiation in root.iter('Radiation'):
        radiation.attrib['amount'] = str(new_jovian_radiotion_location)

def lockAllPassages(connection_between_biomes):
    for connection in connection_between_biomes:
        connection.attrib['locked'] = 'true'

def unlockPassages(connection_between_biomes, biome):
    lockAllPassages(connection_between_biomes)

    if(biome == biomes[0]):
        return

    biome_index = biomes.index(biome)
    prev_connections = connection_between_biomes[:biome_index]
    for connection in prev_connections:
        connection.attrib['locked'] = 'false'
    

args = sys.argv.copy()
args.pop(0)
xml_file = args[0]
target_biome = args[1]
tree = ET.parse(xml_file)
root = tree.getroot()
def main():
    read_config()

    # print(update_jovian_radiation)
    # print(jovian_radiation_distance)
    # print(update_discoverability_of_prev_biomes)
    # print(unlock_biome_passages)

    locations = findAllLocations(root)
    connection_between_biomes = findAllConnectionsBetweenBiomes(locations)
    new_location = getFirstLocationInBiome(locations, connection_between_biomes, target_biome)
    updateCurrentLocation(new_location)
    
    if update_discoverability_of_prev_biomes:
        discoverAllPrevBiomes(locations, target_biome)

    if update_jovian_radiation:
        updateJovianRadiation(new_location)

    if unlock_biome_passages:
        unlockPassages(connection_between_biomes, target_biome)

    tree.write(xml_file)
    print("Save File Updated!")

main()
