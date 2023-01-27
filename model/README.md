# Modelling

## Introduction

There are two jupyter notebooks in this folder: [notebook.ipynb](./notebook.ipynb) and [presentation.ipynb](./presentation.ipynb). While the latter is a notebook that was specifically made for the presentation (as the name suggests), the former is the notebook which was actually used for modelling. Both of these notebooks are fairly large since they contain a lot of visualizations, so it might take some time to open them. 

While running the presentation notebook should run through without a problem (although taking some time), the modelling notebook contains some code that has potential to crash the kernel or takes extremely long to run (multiple hours). For this reason we have introduced run levels. You can find the definition for RunLevel enum and the currently set enum in one of the first code blocks of the notebook. While the enum has comments explaining all of the run levels, we will still give a short explanation here:

### **RunLevel.SAFE**: 
> When this run level is chosen, only code blocks / operations will be executed that will not crash the kernel and will not take extremely long (upwards of 20 mins).

###  **RunLevel.RESSOURCE_INTENSIVE**:
> When this run level is chosen, all operations permitted by the previous run levels will be executed. In addition to that, code blocks that will take a very long time to complete (upwards of 20 mins) and / or have a minor chance of crashing the kernel will be executed.

### **RunLevel.DANGEROUS**:
> When this run level is chosen, all oerations permitted by the previous run levels will be executed. In addition to that, code blocks that will most likely crash the kernel will be run as well. These codeblocks have been kept in the notebook because they produce valid results until a certain point or to demonstrate infeasibility for usage.