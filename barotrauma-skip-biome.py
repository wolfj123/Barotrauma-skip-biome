
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
    print('TODO read_config')

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
        # print(locations[loc].attrib)
        level = locations[loc].find('Level')
        # print(level)
        if level.attrib['biome'] == biome:
            result[loc] = locations[loc]
    
    return result

def discoverAllPrevBiomes(locations, biome):
    setDiscoveredInLocations(locations, False)

    prev_biomes = biomes[:biomes.index(biome)]
    for prev_biome in prev_biomes:
        biome_locations = getAllLocationsInBiome(locations, prev_biome)
        print(biome_locations)
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
    locations = findAllLocations(root)
    connection_between_biomes = findAllConnectionsBetweenBiomes(locations)
    new_location = getFirstLocationInBiome(locations, connection_between_biomes, target_biome)
    updateCurrentLocation(new_location)
    discoverAllPrevBiomes(locations, target_biome)
    updateJovianRadiation(new_location)
    unlockPassages(connection_between_biomes, target_biome)
    # for gate in connection_between_biomes:
    #     print(gate.attrib)
    tree.write(xml_file)

main()
