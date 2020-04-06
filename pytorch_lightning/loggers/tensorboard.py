import csv
import os
from argparse import Namespace
from typing import Optional, Dict, Union, Any
from warnings import warn

import torch
from pkg_resources import parse_version
from torch.utils.tensorboard import SummaryWriter

from pytorch_lightning.loggers.base import LightningLoggerBase, rank_zero_only


class TensorBoardLogger(LightningLoggerBase):
    r"""

    Log to local file system in TensorBoard format

    Implemented using :class:`torch.utils.tensorboard.SummaryWriter`. Logs are saved to
    ``os.path.join(save_dir, name, version)``

    Example:
        .. code-block:: python

            logger = TensorBoardLogger("tb_logs", name="my_model")
            trainer = Trainer(logger=logger)
            trainer.train(model)

    Args:
        save_dir: Save directory
        name: Experiment name. Defaults to "default".  If it is the empty string then no per-experiment
            subdirectory is used.
        version: Experiment version. If version is not specified the logger inspects the save
            directory for existing versions, then automatically assigns the next available version.
            If it is a string then it is used as the run-specific subdirectory name,
            otherwise version_${version} is used.
        \**kwargs: Other arguments are passed directly to the :class:`SummaryWriter` constructor.

    """
    NAME_CSV_TAGS = 'meta_tags.csv'

    def __init__(
            self, save_dir: str, name: Optional[str] = "default",
            version: Optional[Union[int, str]] = None, **kwargs
    ):
        super().__init__()
        self.save_dir = save_dir
        self._name = name
        self._version = version

        self._experiment = None
        self.tags = {}
        self.kwargs = kwargs

    @property
    def root_dir(self) -> str:
        """
        Parent directory for all tensorboard checkpoint subdirectories.
        If the experiment name parameter is None or the empty string, no experiment subdirectory is used
        and checkpoint will be saved in save_dir/version_dir
        """
        if self.name is None or len(self.name) == 0:
            return self.save_dir
        else:
            return os.path.join(self.save_dir, self.name)

    @property
    def log_dir(self) -> str:
        """
        The directory for this run's tensorboard checkpoint.  By default, it is named 'version_${self.version}'
        but it can be overridden by passing a string value for the constructor's version parameter
        instead of None or an int
        """
        # create a pseudo standard path ala test-tube
        version = self.version if isinstance(self.version, str) else f"version_{self.version}"
        log_dir = os.path.join(self.root_dir, version)
        return log_dir

    @property
    def experiment(self) -> SummaryWriter:
        r"""

         Actual tensorboard object. To use tensorboard features do the following.

         Example::

             self.logger.experiment.some_tensorboard_function()

         """
        if self._experiment is not None:
            return self._experiment

        os.makedirs(self.root_dir, exist_ok=True)
        self._experiment = SummaryWriter(log_dir=self.log_dir, **self.kwargs)
        return self._experiment

    @rank_zero_only
    def log_hyperparams(self, params: Union[Dict[str, Any], Namespace]) -> None:
        params = self._convert_params(params)
        params = self._flatten_dict(params)
        sanitized_params = self._sanitize_params(params)

        if parse_version(torch.__version__) < parse_version("1.3.0"):
            warn(
                f"Hyperparameter logging is not available for Torch version {torch.__version__}."
                " Skipping log_hyperparams. Upgrade to Torch 1.3.0 or above to enable"
                " hyperparameter logging."
            )
        else:
            from torch.utils.tensorboard.summary import hparams
            exp, ssi, sei = hparams(sanitized_params, {})
            writer = self.experiment._get_file_writer()
            writer.add_summary(exp)
            writer.add_summary(ssi)
            writer.add_summary(sei)

        # some alternative should be added
        self.tags.update(sanitized_params)

    @rank_zero_only
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        for k, v in metrics.items():
            if isinstance(v, torch.Tensor):
                v = v.item()
            self.experiment.add_scalar(k, v, step)

    @rank_zero_only
    def save(self) -> None:
        try:
            self.experiment.flush()
        except AttributeError:
            # you are using PT version (<v1.2) which does not have implemented flush
            self.experiment._get_file_writer().flush()

        dir_path = self.log_dir
        if not os.path.isdir(dir_path):
            dir_path = self.save_dir

        # prepare the file path
        meta_tags_path = os.path.join(dir_path, self.NAME_CSV_TAGS)

        # save the metatags file
        with open(meta_tags_path, 'w', newline='') as csvfile:
            fieldnames = ['key', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'key': 'key', 'value': 'value'})
            for k, v in self.tags.items():
                writer.writerow({'key': k, 'value': v})

    @rank_zero_only
    def finalize(self, status: str) -> None:
        self.save()

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> int:
        if self._version is None:
            self._version = self._get_next_version()
        return self._version

    def _get_next_version(self):
        root_dir = os.path.join(self.save_dir, self.name)
        existing_versions = []
        for d in os.listdir(root_dir):
            if os.path.isdir(os.path.join(root_dir, d)) and d.startswith("version_"):
                existing_versions.append(int(d.split("_")[1]))

        if len(existing_versions) == 0:
            return 0

        return max(existing_versions) + 1
