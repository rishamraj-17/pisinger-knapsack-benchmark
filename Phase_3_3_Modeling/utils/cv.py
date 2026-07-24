from typing import Dict, Generator, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from config import (
    CV5_N_SPLITS,
    FAMILIES,
    LOFO_N_FOLDS,
    N_BOOTSTRAP_RESAMPLES,
    RANDOM_SEED,
)


class LofoFoldSplitter:
    def __init__(self, family_col: str = "family"):
        self.family_col = family_col

    def split(
        self, df: pd.DataFrame
    ) -> Generator[Tuple[np.ndarray, np.ndarray, str], None, None]:
        families = df[self.family_col].values
        for held_out_family in FAMILIES:
            test_mask = families == held_out_family
            train_mask = ~test_mask
            train_idx = np.where(train_mask)[0]
            test_idx = np.where(test_mask)[0]
            if len(test_idx) == 0:
                continue
            yield train_idx, test_idx, held_out_family

    def get_n_splits(self) -> int:
        return LOFO_N_FOLDS


class FiveFoldStratifiedSplitter:
    def __init__(
        self,
        n_splits: int = CV5_N_SPLITS,
        random_state: int = RANDOM_SEED,
    ):
        self.n_splits = n_splits
        self.random_state = random_state

    def split(
        self, df: pd.DataFrame
    ) -> Generator[Tuple[np.ndarray, np.ndarray, int], None, None]:
        family_mode = (
            df["family"].astype(str)
            + "_"
            + df["capacity_mode"].astype(str)
        )
        skf = StratifiedKFold(
            n_splits=self.n_splits,
            shuffle=True,
            random_state=self.random_state,
        )
        for fold_idx, (train_idx, test_idx) in enumerate(
            skf.split(np.zeros(len(df)), family_mode)
        ):
            yield train_idx, test_idx, fold_idx

    def get_n_splits(self) -> int:
        return self.n_splits


def stratified_bootstrap(
    y: np.ndarray,
    family: np.ndarray,
    n_resamples: int = N_BOOTSTRAP_RESAMPLES,
    rng: Optional[np.random.Generator] = None,
) -> Generator[np.ndarray, None, None]:
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)

    unique_families, family_inv = np.unique(family, return_inverse=True)
    family_indices = {
        fam: np.where(family_inv == i)[0]
        for i, fam in enumerate(unique_families)
    }

    for _ in range(n_resamples):
        all_boot_idx = []
        for fam in unique_families:
            fam_idx = family_indices[fam]
            n_fam = len(fam_idx)
            boot_fam = rng.choice(fam_idx, size=n_fam, replace=True)
            all_boot_idx.append(boot_fam)
        resample_idx = np.concatenate(all_boot_idx)
        yield resample_idx
