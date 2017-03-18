import unittest

from rmgpy.molecule.molecule import Molecule
from rmgpy.molecule.parser import *
from rmgpy.molecule.atomtype import atomTypes
from external.wip import work_in_progress


class ParserTest(unittest.TestCase):

    def setUp(self):

        self.methane = Molecule().fromAdjacencyList("""
1 C u0 p0 c0 {2,S} {3,S} {4,S} {5,S}
2 H u0 p0 c0 {1,S}
3 H u0 p0 c0 {1,S}
4 H u0 p0 c0 {1,S}
5 H u0 p0 c0 {1,S}
""")
        self.methylamine = Molecule().fromAdjacencyList("""
1 N u0 p1 c0 {2,S} {3,S} {4,S}
2 C u0 p0 c0 {1,S} {5,S} {6,S} {7,S}
3 H u0 p0 c0 {1,S}
4 H u0 p0 c0 {1,S}
5 H u0 p0 c0 {2,S}
6 H u0 p0 c0 {2,S}
7 H u0 p0 c0 {2,S}
""")

    def test_fromAugmentedInChI(self):
        aug_inchi = 'InChI=1S/CH4/h1H4'
        mol = fromAugmentedInChI(Molecule(), aug_inchi)
        self.assertTrue(not mol.InChI == '')
        self.assertTrue(mol.isIsomorphic(self.methane))

        aug_inchi = 'InChI=1/CH4/h1H4'
        mol = fromAugmentedInChI(Molecule(), aug_inchi)
        self.assertTrue(not mol.InChI == '')
        self.assertTrue(mol.isIsomorphic(self.methane))

    def compare(self, adjlist, smiles):
        """
        Compare result of parsing an adjacency list and a SMILES string.
        
        The adjacency list is presumed correct and this is to test the SMILES parser.
        """
        mol1 = Molecule().fromAdjacencyList(adjlist)
        mol2 = Molecule(SMILES=smiles)
        self.assertTrue(mol1.isIsomorphic(mol2), "Parsing SMILES={!r} gave unexpected molecule\n{}".format(smiles, mol2.toAdjacencyList()))


    def test_fromSMILES(self):
        smiles = 'C'
        mol = fromSMILES(Molecule(), smiles)
        self.assertTrue(mol.isIsomorphic(self.methane))

        #Test that atomtypes that rely on lone pairs for identity are typed correctly
        smiles = 'CN'
        mol = fromSMILES(Molecule(), smiles)
        self.assertEquals(mol.atoms[1].atomType, atomTypes['N3s'] )

        # Test N2
        adjlist = '''
        1 N u0 p1 c0 {2,T}
        2 N u0 p1 c0 {1,T}
        '''
        smiles = 'N#N'
        self.compare(adjlist, smiles)

        # Test CH4
        adjlist = '''
        1 C u0 p0 c0 {2,S} {3,S} {4,S} {5,S}
        2 H u0 p0 c0 {1,S}
        3 H u0 p0 c0 {1,S}
        4 H u0 p0 c0 {1,S}
        5 H u0 p0 c0 {1,S}
        '''
        smiles = 'C'
        self.compare(adjlist, smiles)


        # Test H2O
        adjlist = '''
        1 O u0 p2 c0 {2,S} {3,S}
        2 H u0 p0 c0 {1,S}
        3 H u0 p0 c0 {1,S}
        '''
        smiles = 'O'
        self.compare(adjlist, smiles)


        # Test C2H6
        adjlist = '''
        1 C u0 p0 c0 {2,S} {3,S} {4,S} {5,S}
        2 C u0 p0 c0 {1,S} {6,S} {7,S} {8,S}
        3 H u0 p0 c0 {1,S}
        4 H u0 p0 c0 {1,S}
        5 H u0 p0 c0 {1,S}
        6 H u0 p0 c0 {2,S}
        7 H u0 p0 c0 {2,S}
        8 H u0 p0 c0 {2,S}
        '''
        smiles = 'CC'
        self.compare(adjlist, smiles)


        # Test H2
        adjlist = '''
        1 H u0 p0 c0 {2,S}
        2 H u0 p0 c0 {1,S}
        '''
        smiles = '[H][H]'
        self.compare(adjlist, smiles)


        # Test H2O2
        adjlist = '''
        1 O u0 p2 c0 {2,S} {3,S}
        2 O u0 p2 c0 {1,S} {4,S}
        3 H u0 p0 c0 {1,S}
        4 H u0 p0 c0 {2,S}
        '''
        smiles = 'OO'
        self.compare(adjlist, smiles)


        # Test C3H8
        adjlist = '''
        1  C u0 p0 c0 {2,S} {4,S} {5,S} {6,S}
        2  C u0 p0 c0 {1,S} {3,S} {7,S} {8,S}
        3  C u0 p0 c0 {2,S} {9,S} {10,S} {11,S}
        4  H u0 p0 c0 {1,S}
        5  H u0 p0 c0 {1,S}
        6  H u0 p0 c0 {1,S}
        7  H u0 p0 c0 {2,S}
        8  H u0 p0 c0 {2,S}
        9  H u0 p0 c0 {3,S}
        10 H u0 p0 c0 {3,S}
        11 H u0 p0 c0 {3,S}
        '''
        smiles = 'CCC'
        self.compare(adjlist, smiles)


        # Test Ar
        adjlist = '''
        1 Ar u0 p4 c0
        '''
        smiles = '[Ar]'
        self.compare(adjlist, smiles)


        # Test He
        adjlist = '''
        1 He u0 p1 c0
        '''
        smiles = '[He]'
        self.compare(adjlist, smiles)


        # Test CH4O
        adjlist = '''
        1 C u0 p0 c0 {2,S} {3,S} {4,S} {5,S}
        2 O u0 p2 c0 {1,S} {6,S}
        3 H u0 p0 c0 {1,S}
        4 H u0 p0 c0 {1,S}
        5 H u0 p0 c0 {1,S}
        6 H u0 p0 c0 {2,S}
        '''
        smiles = 'CO'
        self.compare(adjlist, smiles)


        # Test CO2
        adjlist = '''
        1 O u0 p2 c0 {2,D}
        2 C u0 p0 c0 {1,D} {3,D}
        3 O u0 p2 c0 {2,D}
        '''
        smiles = 'O=C=O'
        self.compare(adjlist, smiles)


        # Test CO
        adjlist = '''
        1 C u0 p1 c-1 {2,T}
        2 O u0 p1 c+1 {1,T}
        '''
        smiles = '[C-]#[O+]'
        self.compare(adjlist, smiles)


        # Test C2H4
        adjlist = '''
        1 C u0 p0 c0 {2,D} {3,S} {4,S}
        2 C u0 p0 c0 {1,D} {5,S} {6,S}
        3 H u0 p0 c0 {1,S}
        4 H u0 p0 c0 {1,S}
        5 H u0 p0 c0 {2,S}
        6 H u0 p0 c0 {2,S}
        '''
        smiles = 'C=C'
        self.compare(adjlist, smiles)


        # Test O2
        adjlist = '''
        1 O u0 p2 c0 {2,D}
        2 O u0 p2 c0 {1,D}
        '''
        smiles = 'O=O'
        self.compare(adjlist, smiles)


        # Test CH3
        adjlist = '''
        multiplicity 2
        1 C u1 p0 c0 {2,S} {3,S} {4,S}
        2 H u0 p0 c0 {1,S}
        3 H u0 p0 c0 {1,S}
        4 H u0 p0 c0 {1,S}
        '''
        smiles = '[CH3]'
        self.compare(adjlist, smiles)


        # Test HO
        adjlist = '''
        multiplicity 2
        1 O u1 p2 c0 {2,S}
        2 H u0 p0 c0 {1,S}
        '''
        smiles = '[OH]'
        self.compare(adjlist, smiles)


        # Test C2H5
        adjlist = '''
        multiplicity 2
        1 C u0 p0 c0 {2,S} {5,S} {6,S} {7,S}
        2 C u1 p0 c0 {1,S} {3,S} {4,S}
        3 H u0 p0 c0 {2,S}
        4 H u0 p0 c0 {2,S}
        5 H u0 p0 c0 {1,S}
        6 H u0 p0 c0 {1,S}
        7 H u0 p0 c0 {1,S}
        '''
        smiles = 'C[CH2]'
        self.compare(adjlist, smiles)


        # Test O
        adjlist = '''
        multiplicity 3
        1 O u2 p2 c0
        '''
        smiles = '[O]'
        self.compare(adjlist, smiles)


        # Test HO2
        adjlist = '''
        multiplicity 2
        1 O u1 p2 c0 {2,S}
        2 O u0 p2 c0 {1,S} {3,S}
        3 H u0 p0 c0 {2,S}
        '''
        smiles = '[O]O'
        self.compare(adjlist, smiles)


        # Test H
        adjlist = '''
        multiplicity 2
        1 H u1 p0 c0
        '''
        smiles = '[H]'
        self.compare(adjlist, smiles)


        # Test O2
        adjlist = '''
        multiplicity 3
        1 O u1 p2 c0 {2,S}
        2 O u1 p2 c0 {1,S}
        '''
        smiles = '[O][O]'
        self.compare(adjlist, smiles)


    def test_fromInChI(self):
        inchi = 'InChI=1S/CH4/h1H4'
        mol = fromInChI(Molecule(), inchi)
        self.assertTrue(mol.isIsomorphic(self.methane))
        #Test that atomtypes that rely on lone pairs for identity are typed correctly
        inchi = "InChI=1S/CH5N/c1-2/h2H2,1H3"
        mol = fromInChI(Molecule(), inchi)
        self.assertEquals(mol.atoms[1].atomType, atomTypes['N3s'] )

    #current implementation of SMARTS is broken
    def test_fromSMARTS(self):
        smarts = '[CH4]'
        mol = fromSMARTS(Molecule(), smarts)
        self.assertTrue(mol.isIsomorphic(self.methane))

    def test_toRDKitMol(self):
        """
        Test that toRDKitMol returns correct indices and atom mappings.
        """
        bondOrderDict = {'SINGLE':1,'DOUBLE':2,'TRIPLE':3,'AROMATIC':1.5}
        mol = fromSMILES(Molecule(), 'C1CCC=C1C=O')
        rdkitmol, rdAtomIndices = mol.toRDKitMol(removeHs=False, returnMapping=True, sanitize=True)
        for atom in mol.atoms:
            # Check that all atoms are found in mapping
            self.assertTrue(atom in rdAtomIndices)
            # Check that all bonds are in rdkitmol with correct mapping and order
            for connectedAtom, bond in atom.bonds.iteritems():
                bondType = str(rdkitmol.GetBondBetweenAtoms(rdAtomIndices[atom],rdAtomIndices[connectedAtom]).GetBondType())
                rdkitBondOrder = bondOrderDict[bondType]
                self.assertEqual(bond.order, rdkitBondOrder)
        
        # Test for removeHs = True        
        rdkitmol2, rdAtomIndices2 = mol.toRDKitMol(removeHs=True, returnMapping=True, sanitize=True)
        
        for atom in mol.atoms:
            # Check that all non-hydrogen atoms are found in mapping
            if atom.symbol != 'H':
                self.assertTrue(atom in rdAtomIndices)
                # Check that all bonds connected to non-hydrogen have the correct mapping and order
                for connectedAtom, bond in atom.bonds.iteritems():
                    if connectedAtom.symbol != 'H':
                        bondType = str(rdkitmol.GetBondBetweenAtoms(rdAtomIndices[atom],rdAtomIndices[connectedAtom]).GetBondType())
                        rdkitBondOrder = bondOrderDict[bondType]
                        self.assertEqual(bond.order, rdkitBondOrder)   



class ResetLonePairsTest(unittest.TestCase):

    def test_Methane(self):
        smi = 'C'
        mol = Molecule().fromSMILES(smi)
        p_indices = []

        reset_lone_pairs(mol, p_indices)

        for at in mol.atoms:
            self.assertEquals(at.lonePairs, 0)

    def test_SingletMethylene(self):
        adjlist = """
multiplicity 1
1 C u0 p1 c0 {2,S} {3,S}
2 H u0 p0 c0 {1,S}
3 H u0 p0 c0 {1,S}
"""
        mol = Molecule().fromAdjacencyList(adjlist)
        p_indices = [1]

        reset_lone_pairs(mol, p_indices)

        for at in mol.atoms:
            if at.symbol == 'C':
                self.assertEquals(at.lonePairs, 1)
            else:
                self.assertEquals(at.lonePairs, 0)
