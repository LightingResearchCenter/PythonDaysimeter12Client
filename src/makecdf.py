#MakeCDF
#Author: Jed Kundl
#Creation Date: 19.06.2013
#INPUT: 
#OUTPUT: CDF File

def makeCDF():
    from spacepy import pycdf
    import constants
    from readraw import readRaw
    from datetime import datetime
    from getlocaloffset import getLocalOffsetS
    
    FILENAME = constants.CDF_FILENAME
    data = readRaw()
    
    with pycdf.CDF(FILENAME,'') as cdf_fp:
        #Set global attributes
        cdf_fp.attrs['creationDate'] = datetime.now()
        cdf_fp.attrs['deviceModel'] = data[0][0]
        cdf_fp.attrs['deviceSN'] = data[0][1]
        cdf_fp.attrs['redCalibration'] = data[0][2][0]
        cdf_fp.attrs['greenCalibration'] = data[0][2][1]
        cdf_fp.attrs['blueCalibration'] = data[0][2][2]
#########The following global attributes either do not exist yet, or
#########have no available source to pull the information from
#        cdf_fp.attrs['uvCalibration'] = 
#        cdf_fp.attrs['illuminanceCalibration'] =
#        cdf_fp.attrs['subjectID'] =
#        cdf_fp.attrs['subjectSex'] =
#        cdf_fp.attrs['subjectDateOfBirth'] =
#        cdf_fp.attrs['subjectMass'] =
        
        #Set variables
        cdf_fp['time'] = data[1][0]
        cdf_fp.new('matTime',type=pycdf.const.CDF_REAL8)
        cdf_fp['matTime'] = data[1][1]
        cdf_fp.new('timeOffset',getLocalOffsetS(),pycdf.const.CDF_INT4,False)
        cdf_fp['red'] = data[1][2]
        cdf_fp['green'] = data[1][3]
        cdf_fp['blue'] = data[1][4]
        cdf_fp['illuminance'] = data[1][5]
        cdf_fp['CLA'] = data[1][6]
        cdf_fp['CS'] = data[1][7]
        cdf_fp['activity'] = data[1][8]
        
#        cdf_fp['xAcceleration'] =
#        cdf_fp['yAcceleration'] =
#        cdf_fp['zAcceleration'] =
#        cdf_fp['uvIndex'] =
#        cdf_fp['temperature'] =
#        cdf_fp['longitude'] =
#        cdf_fp['latitude'] =
#        cdf_fp['event'] =
        
        #Set variable attributes for time
        cdf_fp['time'].attrs['description'] = 'UTC in CDF Epoch format, milliseconds since 1-Jan-0000'
        cdf_fp['time'].attrs['unitPrefix'] = 'm'
        cdf_fp['time'].attrs['baseUnit'] = 's'
        cdf_fp['time'].attrs['unitType'] = 'baseSI'
        cdf_fp['time'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for matTime
        cdf_fp['matTime'].attrs['description'] = 'UTC in MATLAB serial date format, days since 1-Jan-0000'
        cdf_fp['matTime'].attrs['unitPrefix'] = ''
        cdf_fp['matTime'].attrs['baseUnit'] = 'days'
        cdf_fp['matTime'].attrs['unitType'] = 'nonSI'
        cdf_fp['matTime'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for timeOffset
        cdf_fp['timeOffset'].attrs['description'] = 'Localized offset from UTC'
        cdf_fp['timeOffset'].attrs['unitPrefix'] = ''
        cdf_fp['timeOffset'].attrs['baseUnit'] = 's'
        cdf_fp['timeOffset'].attrs['unitType'] = 'baseSI'
        cdf_fp['timeOffset'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for red
        cdf_fp['red'].attrs['description'] = ''
        cdf_fp['red'].attrs['unitPrefix'] = ''
        cdf_fp['red'].attrs['baseUnit'] = 'lx'
        cdf_fp['red'].attrs['unitType'] = 'namedSI'
        cdf_fp['red'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for green
        cdf_fp['green'].attrs['description'] = ''        
        cdf_fp['green'].attrs['unitPrefix'] = ''
        cdf_fp['green'].attrs['baseUnit'] = 'lx'
        cdf_fp['green'].attrs['unitType'] = 'namedSI'
        cdf_fp['green'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for blue
        cdf_fp['blue'].attrs['description'] = ''
        cdf_fp['blue'].attrs['unitPrefix'] = ''
        cdf_fp['blue'].attrs['baseUnit'] = 'lx'
        cdf_fp['blue'].attrs['unitType'] = 'namedSI'
        cdf_fp['blue'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for illuminance
        cdf_fp['illuminance'].attrs['description'] = ''
        cdf_fp['illuminance'].attrs['unitPrefix'] = ''
        cdf_fp['illuminance'].attrs['baseUnit'] = 'lx'
        cdf_fp['illuminance'].attrs['unitType'] = 'namedSI'
        cdf_fp['illuminance'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for CLA
        cdf_fp['CLA'].attrs['description'] = 'Circadian Light'
        cdf_fp['CLA'].attrs['unitPrefix'] = ''
        cdf_fp['CLA'].attrs['baseUnit'] = 'CLA'
        cdf_fp['CLA'].attrs['unitType'] = 'nonSI'
        cdf_fp['CLA'].attrs['otherAttributes'] = 'model'
        
        #Set variable attributes for CS
        cdf_fp['CS'].attrs['description'] = 'Circadian Stimulus'
        cdf_fp['CS'].attrs['unitPrefix'] = ''
        cdf_fp['CS'].attrs['baseUnit'] = 'CS'
        cdf_fp['CS'].attrs['unitType'] = 'nonSI'
        cdf_fp['CS'].attrs['otherAttributes'] = 'model'
        
        #Set variable attributes for activity
        cdf_fp['activity'].attrs['description'] = 'Activity index in g-force (acceleration in m/2^2 over standard gravity 9.80665 m/s^2)'
        cdf_fp['activity'].attrs['unitPrefix'] = ''
        cdf_fp['activity'].attrs['baseUnit'] = 'g_n'
        cdf_fp['activity'].attrs['unitType'] = 'nonSI'
        cdf_fp['activity'].attrs['otherAttributes'] = 'method'
        
        #Set variable attributes for xAcceleration
#        cdf_fp['xAcceleration'].attrs['description'] = 'Acceleration in the x-axis relative to the accelerometer'
#        cdf_fp['xAcceleration'].attrs['unitPrefix'] = ''
#        cdf_fp['xAcceleration'].attrs['baseUnit'] = 'm/s^2'
#        cdf_fp['xAcceleration'].attrs['unitType'] = 'derivedSI'
#        cdf_fp['xAcceleration'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for yAcceleration
#        cdf_fp['yAcceleration'].attrs['description'] = 'Acceleration in the y-axis relative to the accelerometer'
#        cdf_fp['yAcceleration'].attrs['unitPrefix'] = ''
#        cdf_fp['yAcceleration'].attrs['baseUnit'] = 'm/s^2'
#        cdf_fp['yAcceleration'].attrs['unitType'] = 'derivedSI'
#        cdf_fp['yAcceleration'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for zAcceleration
#        cdf_fp['zAcceleration'].attrs['description'] = 'Acceleration in the z-axis relative to the accelerometer'
#        cdf_fp['zAcceleration'].attrs['unitPrefix'] = ''
#        cdf_fp['zAcceleration'].attrs['baseUnit'] = 'm/s^2'
#        cdf_fp['zAcceleration'].attrs['unitType'] = 'derivedSI'
#        cdf_fp['zAcceleration'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for uvIndex
#        cdf_fp['uvIndex'].attrs['description'] = 'Ultraviolet index'
#        cdf_fp['uvIndex'].attrs['unitPrefix'] = ''
#        cdf_fp['uvIndex'].attrs['baseUnit'] = 'uvIndex'
#        cdf_fp['uvIndex'].attrs['unitType'] = 'nonSI'
#        cdf_fp['uvIndex'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for temperature
#        cdf_fp['temperature'].attrs['description'] = 'Ambient air temperature in degrees Kelvin'
#        cdf_fp['temperature'].attrs['unitPrefix'] = ''
#        cdf_fp['temperature'].attrs['baseUnit'] = 'K'
#        cdf_fp['temperature'].attrs['unitType'] = 'baseSI'
#        cdf_fp['temperature'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for longitude
#        cdf_fp['longitude'].attrs['description'] = 'Longitude in decimal degrees'
#        cdf_fp['longitude'].attrs['unitPrefix'] = ''
#        cdf_fp['longitude'].attrs['baseUnit'] = 'deg'
#        cdf_fp['longitude'].attrs['unitType'] = 'nonSI'
#        cdf_fp['longitude'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for latitude
#        cdf_fp['latitude'].attrs['description'] = 'Latitude in decimal degrees'
#        cdf_fp['latitude'].attrs['unitPrefix'] = ''
#        cdf_fp['latitude'].attrs['baseUnit'] = 'deg'
#        cdf_fp['latitude'].attrs['unitType'] = 'nonSI'
#        cdf_fp['latitude'].attrs['otherAttributes'] = ''
        
        #Set variable attributes for event
#        cdf_fp['event'].attrs['description'] = 'Event marker'
#        cdf_fp['event'].attrs['unitPrefix'] = ''
#        cdf_fp['event'].attrs['baseUnit'] = ''
#       cdf_fp['event'].attrs['unitType'] = ''
#        cdf_fp['event'].attrs['otherAttributes'] = 'event code definition'