from core.exceptions import InvalidLevelException

# tiered parameters for use in armor mitigation calculations. first tuple
# element is the minimum level of the tier. the tuples must be in descending
# order of minimum level for the lookup to work. parameters taken from
# http://elitistjerks.com/f15/t29453-combat_ratings_level_85_cataclysm/. it is
# confirmed that the 81+ ratings are in effect in pre-cata 4.0.1 in
# http://blue.mmo-champion.com/topic/22463/physical-mitigation-change-intentional
PARAMETERS = [ (81, 2167.5, 158167.5),
               (60,  467.5,  22167.5),
               ( 1,   85.0,   -400.0) ] # yes, negative 400

def lookup_parameters(level):
    for parameters in PARAMETERS:
        if level >= parameters[0]:
            return parameters
    raise InvalidLevelException(_('No armor mitigation parameters available for level {level}').format(level=level))

def parameter(level=85):
    parameters = lookup_parameters(level)
    return level * parameters[1] - parameters[2]

# this is the fraction of damage reduced by the armor
def mitigation(armor, level=85, parameter=None):
    if parameter == None:
        parameter = armor_mitigation.parameter(level)
    return armor / (armor + parameter)

# this is the fraction of damage retained despite the armor, 1 - mitigation. 
def multiplier(armor, level=85, parameter=None):
    if parameter == None:
        parameter = armor_mitigation.parameter(level)
    return parameter / (armor + parameter)
