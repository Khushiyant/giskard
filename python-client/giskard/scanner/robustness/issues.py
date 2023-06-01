import pandas as pd
import numpy as np
from dataclasses import dataclass

from ..issues import Issue, IssueInfo
from ...models.base import BaseModel
from ...datasets.base import Dataset


@dataclass
class RobustnessIssueInfo(IssueInfo):
    feature: str
    perturbation_name: str
    fail_ratio: float
    perturbed_data_slice: Dataset
    fail_data_idx: list


class RobustnessIssue(Issue):
    group = "Robustness"
    info: RobustnessIssueInfo

    def __init__(self, model: BaseModel, dataset: Dataset, level: str, info: RobustnessIssueInfo):
        super().__init__(model, dataset, level, info)

    @property
    def is_major(self) -> bool:
        return self.level == "major"

    @property
    def domain(self) -> str:
        return f"Feature `{self.info.feature}`"

    @property
    def metric(self) -> str:
        return self.info.perturbation_name

    @property
    def deviation(self) -> str:
        return f"{self.info.fail_ratio * 100:.2f}% of samples changed prediction after perturbation"

    @property
    def description(self) -> str:
        return ""

    def examples(self, n=3) -> pd.DataFrame:
        idx = np.random.choice(self.info.fail_data_idx, min(len(self.info.fail_data_idx), n))

        pert_data = self.info.perturbed_data_slice.df.loc[idx, (self.info.feature, self.dataset.target)]
        examples = self.dataset.df.loc[idx]
        examples = examples.join(pert_data, rsuffix="_perturbed")

        return examples

    @property
    def importance(self) -> float:
        return self.info.fail_ratio
