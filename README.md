# Topograpical distance visualization (TDV)

This repository representing a prototypical implementation of my bachelor thesis. 

The thesis has the topic **Enhancing dimension reduction visualizations with topographical information**

## Idea/Abstract
Visualization and dimensional reduction often play a critical role in the field of "Visual analytics". Most dimensional reduction approaches visualize their data only with scatterplots, which lose the benefits of complex or more recent visualization techniques. By not using these methods information can get lost. Further are reduction methods always faulty, credibility is therefore to be considered with caution.

In this thesis I evaluate a new approach to visualize complex and big data, by combining dimensional reduction methods with topographical visualization. Therefore I present an prototypical implementation to test and compare this approach with recent dimensional reduction approaches. For the comparison I used two common metrics in form of neighborhood preservation and distance preservation. For the implementation I use established and recent dimensional reduction as prestept to my approach.

The final visualization visualize the abberation in a form, that point to point distances are more accuratly visible. Therefore the visualization use topographic structures and depict the error as mountains. The result is a visualizaiton, which should help users to get a better insight into the data and help to classify the (local) credibility.

The main topic of this thesis is the evaluation of the feasibility of my approach and the results of my implementation.

## Visualizations

![Idea](https://github.com/BluemlJ/TDV/blob/master/idea.png)

On the left side we see the Atom Dataset from the Fundamental Clustering Problem Suite by Ultsch (https://www.uni-marburg.de/fb12/arbeitsgruppen/datenbionik/data) and the representation as a scatterplot after using PCA. On the right side we see the calculated topographical map.

![Idea](https://github.com/BluemlJ/TDV/blob/master/images/topogram.png)

The visualization is the result if we used the default parameter in process.py and used them for the example in the example folder.
## Scripts

**dim_red**: Script with four common dimensional reduction approaches. Works with csv.

**draw_image**: Class for drawing topograms and heatmaps. It also can draw isochrones if we do not use this function yet. It works on the grid class and should be used in the process not after. 

**eval**: Evaluates distance preservation and neighbourhood preservation. It is not needed in the process but can be used for evaluation after using. 

**math_functions**: Some math functions 

**process**: The "main" script of this approach.

**objects/...**: Object classes representing the data. datapoint representing one row of the original data. Cell representing a group of points wihtin a fixed position on the grid. Grid held global informations about the cells.

## Example

In this section I will demonstrate how to use this protoype with the isolet dataset. 
The UCI ISOLET Dataset has over 6000 instances and over 600 dimensions. (https://archive.ics.uci.edu/ml/datasets/isolet)

The first step is to use the dim_red script to generate a csv file. This has the new dimensions dred1 and dred2 as first and second column and represents the data after using a dimensional reduction approach.

After generating the new csv, we can set the hyperparameter and the correct path to this csv in process.py.

Be careful with the parameters and their effects on the runtime. 

After this we can start this script. It will generate different visualizations while running and save them in images/. The results will be saved as a csv file. The structure of this file is the following:

Column 0: dred1;
Column 1: dred2;
Column 2: height;
Column 3-n: Data;... 


The result.csv can be visualized seperatly. 
The logs can be found in logfile and logfil2. The first is detailed version for debugging. The size of this file not to underestimate. We did not upload logfile here because his size. Logfile2 is far more an overview and a smaller version.

The overall runtime of this approach is quite heavy so dont worry if it needs time. 

