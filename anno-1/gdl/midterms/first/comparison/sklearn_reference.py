"""
Reference solution using sklearn's GaussianMixture.
Compares results with the custom GMM implementation.
"""
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

# Load data
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
train_df = pd.read_csv(os.path.join(script_dir, '..', 'train.csv'))
X = train_df.values
n, d = X.shape
print(f"Data: n={n}, d={d}\n")

# --- Model selection with BIC for k=1..6 ---
print("=" * 60)
print("sklearn GaussianMixture (covariance_type='diag')")
print("=" * 60)

best_bic = np.inf  # sklearn BIC is to be MINIMIZED (opposite sign)
best_k = None
best_model = None

for k in range(1, 7):
    gm = GaussianMixture(
        n_components=k,
        covariance_type='diag',  # diagonal covariance like our implementation
        n_init=10,               # 10 random restarts to avoid local minima
        max_iter=1000,
        tol=1e-8,
        random_state=9951,
    )
    gm.fit(X)

    # sklearn log_likelihood: total (not per-sample)
    ll = gm.score(X) * n
    # sklearn BIC (sign convention: lower is better)
    sk_bic = gm.bic(X)

    # Our BIC convention (higher is better):
    # BIC = ll - (|theta|/2) * log(n)
    # sklearn BIC = -2*ll + |theta|*log(n)
    # So: our_bic = -sklearn_bic / 2
    our_bic = -sk_bic / 2

    print(f"k={k}\tBIC(our conv.)={our_bic:.4f}\tlogP(X|θ)={ll:.4f}\t(sklearn BIC={sk_bic:.2f})")

    if sk_bic < best_bic:
        best_bic = sk_bic
        best_k = k
        best_model = gm

print(f"\nBest model: k={best_k}")
print(f"BIC (our convention): {-best_bic/2:.4f}")
print(f"logP(X|θ): {best_model.score(X) * n:.4f}")

# --- Print parameters ---
print(f"\nParameters (k={best_k}):")
for i in range(best_k):
    print(f"  π[{i}]: {best_model.weights_[i]:.6f}")
    print(f"  μ[{i}]: {best_model.means_[i]}")
    print(f"  σ²[{i}]: {best_model.covariances_[i]}")  # diag variances
    print()

# --- Verify BIC formula ---
print("=" * 60)
print("BIC formula verification")
print("=" * 60)
# Our formula: n_params = (K-1) + 2*K*d
n_params_ours = (best_k - 1) + 2 * best_k * d
# sklearn counts: K*d (means) + K*d (diag cov) + K-1 (weights) = same
print(f"n_params (our formula): {n_params_ours}")
print(f"sklearn n_parameters: {best_model._n_parameters()}")

ll_total = best_model.score(X) * n
our_bic_manual = ll_total - (n_params_ours / 2) * np.log(n)
print(f"BIC manual calc: {our_bic_manual:.4f}")
print(f"BIC from -sklearn/2: {-best_bic/2:.4f}")

# --- Compare with custom implementation results ---
print("\n" + "=" * 60)
print("Comparison with custom GMM (from notebook)")
print("=" * 60)
print("""
Custom GMM results (seed 9951):
  k=1  BIC=-8320.1771  ll=-8286.7541
  k=2  BIC=-8052.0416  ll=-7981.8532
  k=3  BIC=-7919.3844  ll=-7812.4306
  k=4  BIC=-7869.8688  ll=-7726.1496  <-- best
  k=5  BIC=-7899.1658  ll=-7718.6813
  k=6  BIC=-7916.2819  ll=-7699.0320

Notes:
- sklearn uses multiple random restarts (n_init=10), so it may find
  better local optima than a single-run custom EM.
- Both use diagonal covariance.
- Small differences in log-likelihood are expected due to different
  initialization strategies and convergence criteria.
- The key check is: do both select the same k? And are the cluster
  means/variances similar?
""")
