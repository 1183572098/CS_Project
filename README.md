# CS_Project

The project structure is divided into datasets folder, log folder, optimization_results folder and results folder, as well as several python code files.

## datasets

All datasets are stored in this folder. Because the data set size is too large, the data set is not stored in the compressed package. But there is it on github at https://github.com/1183572098/CS_Project

## log

All run logs are stored in this folder. I clean it up manually every once in a while.

## optimization_results

The statistical results of the optimized algorithm will be stored here.

## results

The initial matching algorithm statistics are stored here.

## config.py

This file is used to read the configuration table, that is, to read the parameters in `matching.csv`.

## dataset.py

Running this file is used to pre-process the data in the dataset. Please don't run it lightly, as a full run may take around 24 hours.

## EloRating.py

Run this file to perform the initial matching algorithm and generate the resulting data.

## evaluation.py

Run this file to evaluate the algorithm.

## main.py

useless file.

## optimization.py

Running this file executes the optimized algorithm and generates the resulting data.