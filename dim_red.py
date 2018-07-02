import pandas as pd
from sklearn import preprocessing, manifold, datasets, decomposition

from enum import Enum
class Method(Enum):
    PCA = 1
    ISOMAP = 2
    TSNE = 3
    MDS = 4

class Dataset(Enum):
    IRIS = 1
    CALIFORNIA_HOUSING = 2
    BREAS_CANCER_WISCONSIN = 3

# PARAMETER
OUTPUT_CSV : str = 'atom_pca.csv'
DR_METHOD : enumerate = Method.PCA
DATASET : enumerate or str = "example/atom.csv"




# load dataset
# IRIS
if DATASET == Dataset.IRIS:
    iris = datasets.load_iris()
    data_scaled = pd.DataFrame(iris.data, columns=iris.feature_names)
    #data_scaled = pd.DataFrame(preprocessing.scale(data_scaled), columns=data_scaled.columns)

# CALIFORNIA HOUSING
elif DATASET == Dataset.CALIFORNIA_HOUSING:
    data = datasets.fetch_california_housing()
    data_scaled = pd.DataFrame(data=data.data, columns=data.feature_names)
    #data_scaled = pd.DataFrame(preprocessing.scale(data_scaled), columns=data_scaled.columns)

# BREAST CANCER WISCONSIN
elif DATASET == Dataset.BREAS_CANCER_WISCONSIN:
    data = datasets.load_breast_cancer()
    data_scaled = pd.DataFrame(data=data.data, columns=data.feature_names)
    #data_scaled = pd.DataFrame(preprocessing.scale(data_scaled), columns=data_scaled.columns)


else:
    data_scaled = pd.read_csv(DATASET)
    
    # UCI Isolet
    #data_scaled = pd.read_csv('example/isolet.csv')

# Approaches

if DR_METHOD is Method.PCA:
    X_r = decomposition.PCA(n_components=2).fit_transform(data_scaled)
elif DR_METHOD is Method.ISOMAP:
    X_r = manifold.Isomap().fit_transform(data_scaled)
elif DR_METHOD is Method.TSNE:
    X_r = manifold.TSNE(n_components=2, random_state=1).fit_transform(data_scaled)
elif DR_METHOD is Method.MDS:
    X_r = manifold.MDS().fit_transform(data_scaled)
else:
    print("IOERROR")
    raise IOError
    pass
# Normalizing with MinMax
#X_r = preprocessing.MinMaxScaler().fit_transform(X_r)

# Simple Scale
X_r = (X_r-X_r.min())/(X_r.max()-X_r.min())

tmp = pd.DataFrame(X_r, columns=['dred1', 'dred2'])
new_csv = pd.concat([tmp, data_scaled], axis=1)
print(new_csv)
pd.DataFrame.to_csv(new_csv, OUTPUT_CSV, index=int, header=None)

