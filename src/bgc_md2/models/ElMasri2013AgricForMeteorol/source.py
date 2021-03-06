from sympy import var, ImmutableMatrix, Piecewise
from bgc_md2.resolve.mvars import (
    CompartmentalMatrix,
    InputTuple,
    TimeSymbol,
    StateVariableTuple,
    VegetationCarbonInputScalar,
    VegetationCarbonInputPartitioningTuple,
    VegetationCarbonStateVariableTuple,
)
from ..BibInfo import BibInfo 
#from bgc_md2.resolve.MVarSet import MVarSet
from bgc_md2.helper import MVarSet

sym_dict = {
        'C_leaf': 'Amount of carbon for the leaf' #"kgC*m^{-2}" 
        ,'C_stem': 'Amount of carbon for the stem' #"kgC*m^{-2}" 
        ,'C_roots': 'Amount of carbon for the root' #"kgC*m^{-2}" 
        ,' GPP': 'Carbon gain via photosynthesis (Gross Primary Productivity, GPP)' #"KgC*m^{−2}*yr^{−1}"
        ,'NPP': 'Net primary Productivity (NPP)' #"KgC*m^{−2}*yr^{−1}"
        ,'k_leaf': ''
        ,'cn_leaf': ''
        ,'k_stem': ''
        ,'cn_stem': ''
        ,'k_roots': ''
        ,'cn_roots': ''
        ,'gt': 'Function of Q_10 and temperature' #See table A1 for equations
        ,'teta': ''
        ,'R_leaf': 'Leaf respiration'
        ,'R_stem': 'Stem respiration'
        ,'R_roots': 'Roots respiration'
        ,'Allo_fact_stem': ''
        ,'Allo_fact_roots': ''
        ,'Allo_fact_leaf': ''
        ,'a_L': 'Parameter introduced by the author of this entry in order to summarize equations on the paper.'
        ,'a_S': 'Parameter introduced by the author of this entry in order to summarize equations on the paper.'  
        ,'a_R': 'Parameter introduced by the author of this entry in order to summarize equations on the paper.'  
        ,'Y_leaf': 'Litter production' #"year"
        ,'Y_stem': 'Litter production' #"year"
        ,'Y_roots': 'Litter production' #"year"
}

for name in sym_dict.keys():
    var(name)

#NPP=G-(R_gL+R_gS+R_gR)-(R_mL+R_mS+R_mR)
R_leaf = k_leaf * (C_leaf/cn_leaf) * teta * gt
R_stem = k_stem * (C_stem/cn_stem) * teta * gt
R_roots = k_roots * (C_roots/cn_roots) * teta * gt
Allo_fact_leaf = 1 - Allo_fact_stem - Allo_fact_roots
a_L = Piecewise((((GPP*Allo_fact_leaf)-R_leaf),NPP<0),((NPP*Allo_fact_leaf),NPP>0))
a_S = Piecewise((((GPP*Allo_fact_stem)-R_stem),NPP<0),((NPP*Allo_fact_stem),NPP>0))
a_R = Piecewise((((GPP*Allo_fact_roots)-R_roots),NPP<0),((NPP*Allo_fact_roots),NPP>0))

x = StateVariableTuple((C_leaf, C_stem, C_roots))
u = (a_L,a_S,a_R)
b = 1 
Input = InputTuple(b*ImmutableMatrix(u))
#"f_v = u + A*x"
A = CompartmentalMatrix(
[[-(1/Y_leaf),0,0],
                               [0, -(1/Y_stem), 0],
                               [0, 0, -(1/Y_roots)]]
)
t = TimeSymbol("t")

mvs = MVarSet({
    BibInfo(# Bibliographical Information
        name="ISAM",
        longName="Integrated Science Assessment Model", 
        version="",
        entryAuthor="Verónika Ceballos-Núñez",
        entryAuthorOrcid="0000-0002-0046-1160",
        entryCreationDate="3/5/2018",
        doi="10.1111/j.1365-2486.2004.00890.x",
        sym_dict=sym_dict
    ),
    A,  # the overall compartmental matrix
    Input,  # the overall input
    t,  # time for the complete system
    x,  # state vector of the complete system
    VegetationCarbonInputScalar(b),
    # vegetation carbon partitioning.
    VegetationCarbonInputPartitioningTuple(u),
    VegetationCarbonStateVariableTuple((C_leaf, C_stem, C_roots)),
})
