# MLE FIX FOR NILMTK
This file has a small fix for the MLE disaggregation model for NILMTK.
The problem was that the model used methods from pandas which are at a certain pandas version not implemented.
Even with this fix MLE still does not work properly for BLOND for unknown reasons.
## Applying the fix
In order to apply this fix you have to replace the *maximum_likelihood_estimation.py* in */path/to/nilmtk/disaggregation/* with this one. Please create and save a backup of the old *maximum_likelihood_estimation.py*