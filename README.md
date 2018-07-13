# BLOND DATA CONVERTER  
## Usage 
### Downloading the BLOND-250 dataset

run 
> python download_sum.py

This will download all summary files for each day for each MEDAL and CLEAR unit.
The folder structure will be kept as it is on the FTP.

### Converting BLOND metadata to NILMTK
run 
>cd metadata_converter/ && python convert_blond.py && cd ..

This will build the building.yaml file and copy the dataset.yml and meter_devices.yml to the dist/ folder. This dist folder containing these three files will be needed for the data conversion.

### Converting BLOND to NILMTK
run 
> cd data_converter/ && python convert_sum.py && cd ..

This will convert BLOND to a NILMTK format. The result will be written as converted_sum.hdf5 in the data/ folder.

### Running tests
The notebooks/ folder contains a IPythonNotebook computing some basic statistics about the BLOND dataset.

If you want to test NILMTK disaggregation models you can run the test_top_k.py script which will disaggregate for k=5 appliances. You can change the parameters in the file in order to get different results. The script can be run with 
> cd tests/ && python test_top_k.py && cd ..