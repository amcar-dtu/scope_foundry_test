# generated with ScopeFoundry.tools
#
# pip install ScopeFoundry
# python -m ScopeFoundry.tools
#
# from h5_data_loaders import load, find_settings
# data = load('your_file_name.h5')

import functools
import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import h5py
import numpy as np

load_funcs = {}


def get_measurement_name(fname: str) -> str:
    with h5py.File(fname, "r") as file:
        if len(file["measurement"].keys()) == 1:
            return list(file["measurement"].keys())[0]
        return file.attrs["measurement"]


def load(fname: str) -> Any:
    mm_name = get_measurement_name(fname)
    return load_funcs[mm_name](fname)


def load_settings(fname: str) -> Dict[str, Any]:
    path = Path(fname)
    if not path.suffix == ".h5":
        return {}

    settings = {}
    visit_func = functools.partial(_settings_visitfunc, settings=settings)

    with h5py.File(fname, "r") as file:
        file.visititems(visit_func)
        for key, val in file.attrs.items():
            settings[key] = val        

    return settings


def find_settings(settings: Dict, pattern: str = "measurement/*") -> Dict:
    if type(settings) is str:
        settings = load_settings(settings)
    if hasattr(settings, "settings"):
        settings = settings.settings
    matching = [key for key in settings.keys() if fnmatch.fnmatch(key, pattern)]
    if not matching:
        print("no matching key found")
        return {}
    return {k: settings[k] for k in matching}


def _settings_visitfunc(name: str, node: h5py.Group, settings: Dict[str, Any]) -> None:
    if not name.endswith("settings"):
        return

    for key, val in node.attrs.items():
        lq_path = f"{name.replace('settings', key)}"
        settings[lq_path] = val


def get_mm_name(fname: str) -> str:
    with h5py.File(fname, "r") as file:
        if len(file["measurement"].keys()) == 1:
            return list(file["measurement"].keys())[0]
        return file.attrs["measurement"]


@dataclass
class NumberGenReadoutSimple:
    settings: dict
    y: np.ndarray


def load_number_gen_readout_simple(fname: str) -> NumberGenReadoutSimple:
    with h5py.File(fname, 'r') as file:
        m = file['measurement/number_gen_readout_simple']
        return NumberGenReadoutSimple(
            settings=load_settings(fname),
            y=m['y'][:] if 'y' in m else None,
        )


load_funcs['number_gen_readout_simple'] = load_number_gen_readout_simple


@dataclass
class NumberGenReadoutExtendableDataset:
    settings: dict
    y: np.ndarray


def load_number_gen_readout_extendable_dataset(fname: str) -> NumberGenReadoutExtendableDataset:
    with h5py.File(fname, 'r') as file:
        m = file['measurement/number_gen_readout_extendable_dataset']
        return NumberGenReadoutExtendableDataset(
            settings=load_settings(fname),
            y=m['y'][:] if 'y' in m else None,
        )


load_funcs['number_gen_readout_extendable_dataset'] = load_number_gen_readout_extendable_dataset


@dataclass
class NumberGenReadout:
    settings: dict
    y: np.ndarray


def load_number_gen_readout(fname: str) -> NumberGenReadout:
    with h5py.File(fname, 'r') as file:
        m = file['measurement/number_gen_readout']
        return NumberGenReadout(
            settings=load_settings(fname),
            y=m['y'][:] if 'y' in m else None,
        )


load_funcs['number_gen_readout'] = load_number_gen_readout
