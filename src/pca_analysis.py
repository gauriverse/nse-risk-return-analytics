import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_pca(returns: pd.DataFrame): # Returns loadings, explained variance, daily PC scores
    scaled = StandardScaler().fit_transform(returns)
    pca = PCA()
    scores = pca.fit_transform(scaled)

    cols = [f"PC{i + 1}" for i in range(pca.n_components_)]
    loadings = pd.DataFrame(pca.components_.T, index=returns.columns, columns=cols)
    explained = pd.Series(pca.explained_variance_ratio_, index=cols)
    scores = pd.DataFrame(scores, columns=cols, index=returns.index)

    if loadings["PC1"].sum() < 0:
        loadings["PC1"] *= -1
        scores["PC1"] *= -1
    return loadings,explained,scores