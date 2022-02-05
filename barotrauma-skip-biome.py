
import xml.etree.ElementTree as ET
import sys
import os

# https://barotraumagame.com/wiki/Biomes
biomes = ['coldcaverns', 'europanridge', 'theaphoticplateau', 'thegreatsea', 'hydrothermalwastes']

args = sys.argv.copy()
args.pop(0)

xml_file = args[0]
target_biome = args[1]

tree = ET.parse(xml_file)
root = tree.getroot()

locations = {}
def findAllLocations(root):
    for loc in root.iter('location'):
        location_index = int(loc.attrib['i'])
        locations[location_index] = loc
        
def setDiscoveredInLocations(locations, discovered):
    for loc in locations:
        locations[loc].attrib['discovered'] = str(discovered).lower()
        locations[loc].set('updated', 'yes')

def getAllLocationsInBiome(locations, biome):
    result = {}
    for loc in locations:
        level = locations[loc].find('Level')
        if level:
            if level.attrib['biome'] == biome:
                result[loc] = locations[loc]
    
    return result

def getFirstLocationInBiome(locations, biome):
    if biome == biomes[0]:
        min_loc = locations[0]
        for loc in locations:
            curr_min_level = min_loc.find('Level')
            level = locations[loc].find('Level')
            if float(level.attrib['difficulty']) < float(curr_min_level.attrib['difficulty']):
                min_loc = locations[loc]
        return min_loc
    else:
        prev_biome = biomes[biomes.index(biome) - 1]
        last_location_in_prev_biome = None
        for loc in locations:
            level = locations[loc].find('Level')
            if level.attrib['biome'] == prev_biome:
                if locations[loc].attrib['isgatebetweenbiomes'] == "true":
                    last_location_in_prev_biome = locations[loc]
                    break
        last_location_in_prev_biome_index = int(last_location_in_prev_biome.attrib['i'])

        connections_of_last_location_in_prev_biome = []
        for connection in root.iter('connection'):
            connection_locations = connection.attrib['locations'].split(',')
            for idx, con_loc in enumerate(connection_locations):
                if int(con_loc) == last_location_in_prev_biome_index:
                    other_con_loc = connection_locations[(idx + 1) % len(connection_locations)]
                    connection_from_prev_biome_index = int(other_con_loc)
                    location_connected_to_last_location_on_prev_biome = locations[connection_from_prev_biome_index]
                    connections_of_last_location_in_prev_biome.append(location_connected_to_last_location_on_prev_biome)
        
        for location in connections_of_last_location_in_prev_biome:
            level = level = location.find('Level')
            if level.attrib['biome'] == biome:
                return location

findAllLocations(root)
min_loc = getFirstLocationInBiome(locations, biomes[1])
print(min_loc.attrib)




# for loc in locations:
#     print(locations[loc].attrib['basename'])