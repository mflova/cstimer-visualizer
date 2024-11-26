from dataclasses import dataclass

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

sns.set_style("ticks",{'axes.grid' : True})


@dataclass(frozen=True)
class Plotter:
    df: pd.DataFrame

    def in_hue(self) -> None:
        sns.relplot(data=self.df, x="Datetime", y="Duration [s]", hue="Scramble Type", kind="line")

    def in_facets(self) -> None:
        sns.relplot(data=self.df, x="Datetime", y="Duration [s]",  row="Scramble Type", kind="line")