
import numpy
import math

import logging as logging
    
import rmgpy.constants as constants
from rmgpy.molecule import Molecule
from rmgpy.species import Species
from rmgpy.statmech import Conformer
from rmgpy.thermo import Wilhoit, NASA, ThermoData
import rmgpy.data.rmg

def processThermoData(spc, thermo0, thermoClass=NASA):
    """
    Converts via Wilhoit into required `thermoClass` and sets `E0`.
    
    Resulting thermo is returned.
    """
    thermo = None
    database = rmgpy.data.rmg.database
    solvationdatabase = database.solvation

    # Always convert to Wilhoit so we can compute E0
    if isinstance(thermo0, Wilhoit):
        wilhoit = thermo0
    elif isinstance(thermo0, ThermoData):
        Tdata = thermo0._Tdata.value_si
        Cpdata = thermo0._Cpdata.value_si
        H298 = thermo0._H298.value_si
        S298 = thermo0._S298.value_si
        Cp0 = thermo0._Cp0.value_si
        CpInf = thermo0._CpInf.value_si
        wilhoit = Wilhoit().fitToDataForConstantB(Tdata, Cpdata, Cp0, CpInf, H298, S298, B=1000.0)
    else:
        Cp0 = spc.calculateCp0()
        CpInf = spc.calculateCpInf()
        wilhoit = thermo0.toWilhoit(Cp0=Cp0, CpInf=CpInf)
    wilhoit.comment = thermo0.comment

    # Add on solvation correction
    if Species.solventData and not "Liquid thermo library" in thermo0.comment:
        #logging.info("Making solvent correction for {0}".format(Species.solventName))
        soluteData = database.solvation.getSoluteData(spc)
        solvation_correction = database.solvation.getSolvationCorrection(soluteData, Species.solventData)
        # correction is added to the entropy and enthalpy
        wilhoit.S0.value_si = (wilhoit.S0.value_si + solvation_correction.entropy)
        wilhoit.H0.value_si = (wilhoit.H0.value_si + solvation_correction.enthalpy)
        
    # Compute E0 by extrapolation to 0 K
    if spc.conformer is None:
        spc.conformer = Conformer()
    spc.conformer.E0 = wilhoit.E0
    
    # Convert to desired thermo class
    if thermoClass is Wilhoit:
        thermo = wilhoit
    elif thermoClass is NASA:
        if Species.solventData:
            #if liquid phase simulation keep the nasa polynomial if it comes from a liquid phase thermoLibrary. Otherwise convert wilhoit to NASA
            if "Liquid thermo library" in thermo0.comment and isinstance(thermo0, NASA):
                thermo = thermo0
                if thermo.E0 is None:
                    thermo.E0 = wilhoit.E0
            else:
                thermo = wilhoit.toNASA(Tmin=100.0, Tmax=5000.0, Tint=1000.0)
        else: 
            #gas phase with species matching thermo library keep the NASA from library or convert if group additivity
            if "Thermo library" in thermo0.comment and isinstance(thermo0,NASA):
                thermo=thermo0
                if thermo.E0 is None:
                    thermo.E0 = wilhoit.E0
            else:
                thermo = wilhoit.toNASA(Tmin=100.0, Tmax=5000.0, Tint=1000.0)
    else:
        raise Exception('thermoClass neither NASA nor Wilhoit.  Cannot process thermo data.')
    
    if thermo.__class__ != thermo0.__class__:
        # Compute RMS error of overall transformation
        Tlist = numpy.array([300.0, 400.0, 500.0, 600.0, 800.0, 1000.0, 1500.0], numpy.float64)
        err = 0.0
        for T in Tlist:
            err += (thermo.getHeatCapacity(T) - thermo0.getHeatCapacity(T))**2
        err = math.sqrt(err/len(Tlist))/constants.R
        # logging.log(logging.WARNING if err > 0.2 else 0, 'Average RMS error in heat capacity fit to {0} = {1:g}*R'.format(spc, err))

    return thermo
    

def generateThermoData(spc, thermoClass=NASA, quantumMechanics=None):
    """
    Generates thermo data, first checking Libraries, then using either QM or Database.
    
    If quantumMechanics is not None, it is asked to calculate the thermo.
    Failing that, the database is used.
    
    The database generates the thermo data for each structure (resonance isomer),
    picks that with lowest H298 value.
    
    It then calls :meth:`processThermoData`, to convert (via Wilhoit) to NASA
    and set the E0.
    
    Result stored in `spc.thermo` and returned.
    """
    

    database = rmgpy.data.rmg.database
    thermo0 = database.thermo.getThermoData(spc, trainingSet=None, quantumMechanics=quantumMechanics) 
        
    return processThermoData(spc, thermo0, thermoClass)

def generateTransportData(species):
    """
    Generate the transportData parameters for the species.
    """
    database = rmgpy.data.rmg.database
    transport_db = database.transport

    return transport_db.getTransportProperties(species)[0]
