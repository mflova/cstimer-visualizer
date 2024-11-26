import json
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from lazy_type_hint import LazyTypeHintLive
from matplotlib import pyplot as plt
from typing_extensions import Any, Self

from cstimer_visualizer.plotter import Plotter
from cstimer_visualizer.type_aliaes import PathLike


@dataclass
class CSTimerData:

    df: pd.DataFrame

    @staticmethod
    def _from_mapping_to_df(mapping: Mapping[str, Any]) -> pd.DataFrame:
        data: dict[str, list[Any]] = defaultdict(list)
        for session_id, session_data in mapping["properties"]["sessionData"].items():
            # session_data[]
            scramble_type = session_data["opt"]["scrType"] if session_data["opt"] else "3x3"
            for solve in mapping[f"session{session_id}"]:
                intervals = solve[0]
                data["Duration [s]"].append((intervals[1] + intervals[0])/1_000 if intervals[0] >= 0 else np.nan)
                data["Scramble"].append(solve[1])
                data["Was +2"].append(bool(intervals[0] == 2))
                data["Datetime"].append(pd.to_datetime(solve[3], unit="s"))
                data["Scramble Type"].append(scramble_type)

        # return pd.DataFrame(data, dtype={"scramble_type": "category"})
        return pd.DataFrame(data).set_index("Datetime").sort_index()

    
    @classmethod
    def _parse_txt(cls, path: PathLike) -> pd.DataFrame:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = json.loads(path.read_text(encoding="utf-8"))
        content["properties"]["sessionData"] = json.loads(content["properties"]["sessionData"])
        content["properties"]["scrFlt"] = json.loads(content["properties"]["scrFlt"])
        return cls._from_mapping_to_df(content)

    @classmethod
    def from_txt(cls, path: PathLike) -> Self:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        return cls(df=cls._parse_txt(path))

    @classmethod
    def from_folder(cls, path: PathLike) -> Self:
        path = Path(path)
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")
        
        dfs: list[pd.DataFrame] = []
        for file in path.iterdir():
            if file.suffix == ".txt":
                dfs.append(cls._parse_txt(file))

        if not dfs:
            raise FileNotFoundError(f"No .txt files found in directory: {path}")

        df = pd.concat(dfs)
        df = df.loc[~df.index.duplicated(keep=False)]
        return cls(df=df)

    @property
    def plot(self) -> Plotter:
        return Plotter(self.df)

