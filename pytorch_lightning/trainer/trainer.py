import distutils
import inspect
import os
import sys
import warnings
from argparse import ArgumentParser
from typing import Union, Optional, List, Dict, Tuple, Iterable, Any

import torch
import torch.distributed as torch_distrib
import torch.multiprocessing as mp
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from pytorch_lightning import _logger as log
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, Callback
from pytorch_lightning.core.lightning import LightningModule
from pytorch_lightning.loggers import LightningLoggerBase
from pytorch_lightning.profiler import SimpleProfiler, PassThroughProfiler, BaseProfiler
from pytorch_lightning.trainer.auto_mix_precision import TrainerAMPMixin
from pytorch_lightning.trainer.callback_config import TrainerCallbackConfigMixin
from pytorch_lightning.trainer.callback_hook import TrainerCallbackHookMixin
from pytorch_lightning.trainer.data_loading import TrainerDataLoadingMixin
from pytorch_lightning.trainer.deprecated_api import TrainerDeprecatedAPITillVer0_8, TrainerDeprecatedAPITillVer0_9
from pytorch_lightning.trainer.distrib_data_parallel import TrainerDDPMixin
from pytorch_lightning.trainer.distrib_parts import TrainerDPMixin, parse_gpu_ids, determine_root_gpu_device
from pytorch_lightning.trainer.evaluation_loop import TrainerEvaluationLoopMixin
from pytorch_lightning.trainer.logging import TrainerLoggingMixin
from pytorch_lightning.trainer.model_hooks import TrainerModelHooksMixin
from pytorch_lightning.trainer.optimizers import TrainerOptimizersMixin
from pytorch_lightning.trainer.supporters import TensorRunningMean
from pytorch_lightning.trainer.training_io import TrainerIOMixin
from pytorch_lightning.trainer.training_loop import TrainerTrainLoopMixin
from pytorch_lightning.trainer.training_tricks import TrainerTrainingTricksMixin
from pytorch_lightning.utilities.exceptions import MisconfigurationException

try:
    from apex import amp
except ImportError:
    APEX_AVAILABLE = False
else:
    APEX_AVAILABLE = True

try:
    import torch_xla
    import torch_xla.core.xla_model as xm
    import torch_xla.distributed.xla_multiprocessing as xmp
except ImportError:
    XLA_AVAILABLE = False
else:
    XLA_AVAILABLE = True


class Trainer(
    TrainerIOMixin,
    TrainerOptimizersMixin,
    TrainerAMPMixin,
    TrainerDPMixin,
    TrainerDDPMixin,
    TrainerLoggingMixin,
    TrainerModelHooksMixin,
    TrainerTrainingTricksMixin,
    TrainerDataLoadingMixin,
    TrainerEvaluationLoopMixin,
    TrainerTrainLoopMixin,
    TrainerCallbackConfigMixin,
    TrainerCallbackHookMixin,
    TrainerDeprecatedAPITillVer0_8,
    TrainerDeprecatedAPITillVer0_9,
):
    DEPRECATED_IN_0_8 = (
        'gradient_clip', 'nb_gpu_nodes', 'max_nb_epochs', 'min_nb_epochs',
        'add_row_log_interval', 'nb_sanity_val_steps'
    )
    DEPRECATED_IN_0_9 = ('use_amp', 'show_progress_bar')

    def __init__(
            self,
            logger: Union[LightningLoggerBase, Iterable[LightningLoggerBase], bool] = True,
            checkpoint_callback: Union[ModelCheckpoint, bool] = True,
            early_stop_callback: Optional[Union[EarlyStopping, bool]] = False,
            callbacks: List[Callback] = [],
            default_save_path: Optional[str] = None,
            gradient_clip_val: float = 0,
            process_position: int = 0,
            num_nodes: int = 1,
            gpus: Optional[Union[List[int], str, int]] = None,
            num_tpu_cores: Optional[int] = None,
            log_gpu_memory: Optional[str] = None,
            progress_bar_refresh_rate: int = 1,
            overfit_pct: float = 0.0,
            track_grad_norm: int = -1,
            check_val_every_n_epoch: int = 1,
            fast_dev_run: bool = False,
            accumulate_grad_batches: Union[int, Dict[int, int], List[list]] = 1,
            max_epochs: int = 1000,
            min_epochs: int = 1,
            max_steps: Optional[int] = None,
            min_steps: Optional[int] = None,
            train_percent_check: float = 1.0,
            val_percent_check: float = 1.0,
            test_percent_check: float = 1.0,
            val_check_interval: float = 1.0,
            log_save_interval: int = 100,
            row_log_interval: int = 10,
            add_row_log_interval=None,  # backward compatible, todo: remove in v0.8.0
            distributed_backend: Optional[str] = None,
            precision: int = 32,
            print_nan_grads: bool = False,  # backward compatible, todo: remove in v0.9.0
            weights_summary: Optional[str] = 'full',
            weights_save_path: Optional[str] = None,
            amp_level: str = 'O1',
            num_sanity_val_steps: int = 5,
            truncated_bptt_steps: Optional[int] = None,
            resume_from_checkpoint: Optional[str] = None,
            profiler: Optional[BaseProfiler] = None,
            benchmark: bool = False,
            reload_dataloaders_every_epoch: bool = False,
            gradient_clip=None,  # backward compatible, todo: remove in v0.8.0
            nb_gpu_nodes=None,  # backward compatible, todo: remove in v0.8.0
            max_nb_epochs=None,  # backward compatible, todo: remove in v0.8.0
            min_nb_epochs=None,  # backward compatible, todo: remove in v0.8.0
            use_amp=None,  # backward compatible, todo: remove in v0.9.0
            show_progress_bar=None,  # backward compatible, todo: remove in v0.9.0
            nb_sanity_val_steps=None,  # backward compatible, todo: remove in v0.8.0
            **kwargs
    ):
        r"""

        Customize every aspect of training via flags

        Args:
            logger: Logger (or iterable collection of loggers) for experiment tracking.

            checkpoint_callback: Callback for checkpointing.

            early_stop_callback (:class:`pytorch_lightning.callbacks.EarlyStopping`):

            callbacks: Add a list of callbacks.

            default_save_path: Default path for logs and weights when no logger/ckpt_callback passed

            gradient_clip_val: 0 means don't clip.

            gradient_clip:
                .. warning:: .. deprecated:: 0.7.0

                    Use `gradient_clip_val` instead. Will remove 0.9.0.

            process_position: orders the tqdm bar when running multiple models on same machine.

            num_nodes: number of GPU nodes for distributed training.

            nb_gpu_nodes:
                .. warning:: .. deprecated:: 0.7.0

                    Use `num_nodes` instead. Will remove 0.9.0.

            gpus: Which GPUs to train on.

            num_tpu_cores: How many TPU cores to train on (1 or 8).

            log_gpu_memory: None, 'min_max', 'all'. Might slow performance

            show_progress_bar:
                .. warning:: .. deprecated:: 0.7.2

                        Set `progress_bar_refresh_rate` to postive integer to enable. Will remove 0.9.0.

            progress_bar_refresh_rate: How often to refresh progress bar (in steps). Value ``0`` disables progress bar.

            overfit_pct: How much of training-, validation-, and test dataset to check.

            track_grad_norm: -1 no tracking. Otherwise tracks that norm

            check_val_every_n_epoch: Check val every n train epochs.

            fast_dev_run: runs 1 batch of train, test  and val to find any bugs (ie: a sort of unit test).

            accumulate_grad_batches: Accumulates grads every k batches or as set up in the dict.

            max_epochs: Stop training once this number of epochs is reached.

            max_nb_epochs:
                .. warning:: .. deprecated:: 0.7.0

                    Use `max_epochs` instead. Will remove 0.9.0.

            min_epochs: Force training for at least these many epochs

            min_nb_epochs:
                .. warning:: .. deprecated:: 0.7.0

                    Use `min_epochs` instead. Will remove 0.9.0.

            max_steps: Stop training after this number of steps. Disabled by default (None).

            min_steps: Force training for at least these number of steps. Disabled by default (None).

            train_percent_check: How much of training dataset to check.

            val_percent_check: How much of validation dataset to check.

            test_percent_check: How much of test dataset to check.

            val_check_interval: How often within one training epoch to check the validation set

            log_save_interval: Writes logs to disk this often

            row_log_interval: How often to add logging rows (does not write to disk)

            add_row_log_interval:
                .. warning:: .. deprecated:: 0.7.0

                    Use `row_log_interval` instead. Will remove 0.9.0.

            distributed_backend: The distributed backend to use.

            use_amp:
                .. warning:: .. deprecated:: 0.7.0

                    Use `precision` instead. Will remove 0.9.0.

            precision: Full precision (32), half precision (16).

            print_nan_grads:
                .. warning:: .. deprecated:: 0.7.2

                    Has no effect. When detected, NaN grads will be printed automatically.
                    Will remove 0.9.0.

            weights_summary: Prints a summary of the weights when training begins.

            weights_save_path: Where to save weights if specified.

            amp_level: The optimization level to use (O1, O2, etc...).

            num_sanity_val_steps: Sanity check runs n batches of val before starting the training routine.

            nb_sanity_val_steps:
                .. warning:: .. deprecated:: 0.7.0

                    Use `num_sanity_val_steps` instead. Will remove 0.8.0.

            truncated_bptt_steps: Truncated back prop breaks performs backprop every k steps of

            resume_from_checkpoint: To resume training from a specific checkpoint pass in the path here.

            profiler:  To profile individual steps during training and assist in

            reload_dataloaders_every_epoch: Set to True to reload dataloaders every epoch

            benchmark: If true enables cudnn.benchmark.
        """

        # Init callbacks
        self.callbacks = callbacks
        self.on_init_start()

        # benchmarking
        self.benchmark = benchmark
        if benchmark:
            torch.backends.cudnn.benchmark = True

        # Transfer params
        self.num_nodes = num_nodes
        # Backward compatibility, TODO: remove in v0.8.0
        if nb_gpu_nodes is not None:
            warnings.warn("Argument `nb_gpu_nodes` has renamed to `num_nodes` since v0.5.0"
                          " and this method will be removed in v0.8.0", DeprecationWarning)
            self.num_gpu_nodes = nb_gpu_nodes
        self.log_gpu_memory = log_gpu_memory

        self.gradient_clip_val = gradient_clip_val
        # Backward compatibility, TODO: remove in v0.8.0
        if gradient_clip is not None:
            warnings.warn("Argument `gradient_clip` has renamed to `gradient_clip_val` since v0.5.0"
                          " and this method will be removed in v0.8.0", DeprecationWarning)
            self.gradient_clip = gradient_clip

        self.progress_bar_refresh_rate = progress_bar_refresh_rate
        self.check_val_every_n_epoch = check_val_every_n_epoch
        self.track_grad_norm = track_grad_norm
        self.on_gpu = True if (gpus and torch.cuda.is_available()) else False

        # tpu config
        self.on_tpu = num_tpu_cores is not None
        self.num_tpu_cores = num_tpu_cores
        assert num_tpu_cores in [1, 8, None], 'num_tpu_cores can only be 1 or 8'

        self.process_position = process_position
        self.weights_summary = weights_summary

        self.max_epochs = max_epochs
        # Backward compatibility, TODO: remove in v0.8.0
        if max_nb_epochs is not None:
            warnings.warn("Argument `max_nb_epochs` has renamed to `max_epochs` since v0.5.0"
                          " and this method will be removed in v0.8.0", DeprecationWarning)
            self.max_nb_epochs = max_nb_epochs

        self.min_epochs = min_epochs
        # Backward compatibility, TODO: remove in v0.8.0
        if min_nb_epochs is not None:
            warnings.warn("Argument `min_nb_epochs` has renamed to `min_epochs` since v0.5.0"
                          " and this method will be removed in v0.8.0", DeprecationWarning)
            self.min_nb_epochs = min_nb_epochs

        self.max_steps = max_steps
        self.min_steps = min_steps

        self.num_sanity_val_steps = num_sanity_val_steps
        # Backward compatibility, TODO: remove in v0.8.0
        if nb_sanity_val_steps is not None:
            warnings.warn("Argument `nb_sanity_val_steps` has renamed to "
                          "`num_sanity_val_steps` since v0.5.0"
                          " and this method will be removed in v0.8.0", DeprecationWarning)
            self.nb_sanity_val_steps = nb_sanity_val_steps

        # Backward compatibility, TODO: remove in v0.9.0
        if print_nan_grads:
            warnings.warn("Argument `print_nan_grads` has no effect and will be removed in v0.9.0."
                          " NaN grads will be printed automatically when detected.",
                          DeprecationWarning)

        self.reload_dataloaders_every_epoch = reload_dataloaders_every_epoch

        self.truncated_bptt_steps = truncated_bptt_steps
        self.resume_from_checkpoint = resume_from_checkpoint
        self.shown_warnings = set()

        self.fast_dev_run = fast_dev_run
        if self.fast_dev_run:
            self.num_sanity_val_steps = 0
            self.max_epochs = 1
            log.info('Running in fast_dev_run mode: will run a full train,'
                     ' val and test loop using a single batch')

        # set default save path if user didn't provide one
        self.default_save_path = default_save_path
        if self.default_save_path is None:
            self.default_save_path = os.getcwd()

        # training bookeeping
        self.total_batch_idx = 0
        self.running_loss = TensorRunningMean(window_length=20)
        self.batch_idx = 0
        self.tqdm_metrics = {}
        self.callback_metrics = {}
        self.num_val_batches = 0
        self.num_training_batches = 0
        self.num_test_batches = 0
        self.train_dataloader = None
        self.test_dataloaders = None
        self.val_dataloaders = None

        # training state
        self.model = None
        self.testing = False
        self.disable_validation = False
        self.lr_schedulers = []
        self.optimizers = None
        self.optimizer_frequencies = []
        self.global_step = 0
        self.current_epoch = 0
        self.total_batches = 0
        self.interrupted = False

        # configure logger
        self.configure_logger(logger)

        # configure profiler
        if profiler is True:
            profiler = SimpleProfiler()
        self.profiler = profiler or PassThroughProfiler()

        # configure early stop callback
        # creates a default one if none passed in
        self.configure_early_stopping(early_stop_callback)

        # configure checkpoint callback
        self.checkpoint_callback = checkpoint_callback
        self.weights_save_path = weights_save_path

        # accumulated grads
        self.accumulate_grad_batches = accumulate_grad_batches
        self.configure_accumulated_gradients(accumulate_grad_batches)

        # allow int, string and gpu list
        self.gpus = gpus
        self.data_parallel_device_ids = parse_gpu_ids(self.gpus)
        self.root_gpu = determine_root_gpu_device(self.data_parallel_device_ids)
        self.root_device = torch.device("cpu")

        # tpu state flags
        self.use_tpu = False
        self.tpu_local_core_rank = None
        self.tpu_global_core_rank = None

        # distributed backend choice
        self.use_ddp = False
        self.use_ddp2 = False
        self.use_dp = False
        self.single_gpu = False
        self.distributed_backend = distributed_backend
        self.set_distributed_mode(distributed_backend, self.num_nodes)

        # override dist backend when using tpus
        if self.on_tpu:
            self.init_tpu()
            self.current_tpu_idx = None

        # init flags for SLURM+ddp to work
        self.proc_rank = 0
        self.world_size = 1
        self.node_rank = 0
        self.configure_slurm_ddp(self.num_nodes)

        # nvidia setup
        self.set_nvidia_flags(self.is_slurm_managing_tasks, self.data_parallel_device_ids)

        # can't init progress bar here because starting a new process
        # means the progress_bar won't survive pickling
        # backward compatibility
        if show_progress_bar is not None:
            self.show_progress_bar = show_progress_bar

        # logging
        self.log_save_interval = log_save_interval
        self.val_check_interval = val_check_interval

        # backward compatibility
        if add_row_log_interval is not None:
            warnings.warn("`add_row_log_interval` has renamed to `row_log_interval` since v0.5.0"
                          " and this method will be removed in v0.8.0", DeprecationWarning)
            if not row_log_interval:  # in case you did not set the proper value
                row_log_interval = add_row_log_interval
        self.row_log_interval = row_log_interval

        # how much of the data to use
        self.overfit_pct = overfit_pct
        self.determine_data_use_amount(train_percent_check, val_percent_check,
                                       test_percent_check, overfit_pct)

        # 16 bit mixed precision training using apex
        self.amp_level = amp_level
        self.precision = precision

        # Backward compatibility, TODO: remove in v0.9.0
        if use_amp is not None:
            warnings.warn("`use_amp` has been replaced by `precision` since v0.7.0"
                          " and this argument will be removed in v0.9.0", DeprecationWarning)
            self.precision = 16 if use_amp else 32

        assert self.precision in (16, 32), 'only 32 or 16 bit precision supported'

        if self.precision == 16 and self.num_tpu_cores is None:
            use_amp = True
        self.init_amp(use_amp)

        # Callback system
        self.on_init_end()

    @property
    def slurm_job_id(self) -> int:
        try:
            job_id = os.environ['SLURM_JOB_ID']
            job_id = int(job_id)
        except Exception:
            job_id = None
        return job_id

    @classmethod
    def default_attributes(cls):
        init_signature = inspect.signature(Trainer)

        args = {}
        for param_name in init_signature.parameters:
            value = init_signature.parameters[param_name].default
            args[param_name] = value

        return args

    @classmethod
    def get_init_arguments_and_types(cls) -> List[Tuple[str, Tuple, Any]]:
        r"""Scans the Trainer signature and returns argument names, types and default values.

        Returns:
            List with tuples of 3 values:
            (argument name, set with argument types, argument default value).

        Examples:
            >>> args = Trainer.get_init_arguments_and_types()
            >>> import pprint
            >>> pprint.pprint(sorted(args))  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            [('accumulate_grad_batches',
              (<class 'int'>, typing.Dict[int, int], typing.List[list]),
              1),
             ...
             ('callbacks', (<class 'pytorch_lightning.callbacks.base.Callback'>,), []),
             ('check_val_every_n_epoch', (<class 'int'>,), 1),
             ...
             ('max_epochs', (<class 'int'>,), 1000),
             ...
             ('precision', (<class 'int'>,), 32),
             ('print_nan_grads', (<class 'bool'>,), False),
             ('process_position', (<class 'int'>,), 0),
             ('profiler',
              (<class 'pytorch_lightning.profiler.profilers.BaseProfiler'>,
               <class 'NoneType'>),
              None),
             ...
        """
        trainer_default_params = inspect.signature(cls).parameters
        name_type_default = []
        for arg in trainer_default_params:
            arg_type = trainer_default_params[arg].annotation
            arg_default = trainer_default_params[arg].default
            try:
                arg_types = tuple(arg_type.__args__)
            except AttributeError:
                arg_types = (arg_type,)

            name_type_default.append((arg, arg_types, arg_default))

        return name_type_default

    @classmethod
    def get_deprecated_arg_names(cls) -> List:
        """Returns a list with deprecated Trainer arguments."""
        depr_arg_names = []
        for name, val in cls.__dict__.items():
            if name.startswith('DEPRECATED') and isinstance(val, (tuple, list)):
                depr_arg_names.extend(val)
        return depr_arg_names

    @classmethod
    def add_argparse_args(cls, parent_parser: ArgumentParser) -> ArgumentParser:
        r"""Extends existing argparse by default `Trainer` attributes.

        Args:
            parent_parser:
                The custom cli arguments parser, which will be extended by
                the Trainer default arguments.

        Only arguments of the allowed types (str, float, int, bool) will
        extend the `parent_parser`.
        """
        parser = ArgumentParser(parents=[parent_parser], add_help=False, )

        depr_arg_names = cls.get_deprecated_arg_names()

        allowed_types = (str, float, int, bool)
        # TODO: get "help" from docstring :)
        for arg, arg_types, arg_default in cls.get_init_arguments_and_types():
            if arg not in depr_arg_names:
                for allowed_type in allowed_types:
                    if allowed_type in arg_types:
                        if allowed_type is bool:
                            allowed_type = lambda x: bool(distutils.util.strtobool(x))
                        parser.add_argument(
                            f'--{arg}',
                            default=arg_default,
                            type=allowed_type,
                            dest=arg,
                            help='autogenerated by pl.Trainer'
                        )
                        break

        return parser

    @classmethod
    def from_argparse_args(cls, args):

        params = vars(args)
        return cls(**params)

    @property
    def num_gpus(self) -> int:
        gpus = self.data_parallel_device_ids
        if gpus is None:
            return 0
        return len(gpus)

    @property
    def data_parallel(self) -> bool:
        return self.use_dp or self.use_ddp or self.use_ddp2

    @property
    def training_tqdm_dict(self) -> dict:
        """Read-only for tqdm metrics.
        :return:
        """
        ref_model = self.model if not self.data_parallel else self.model.module

        return dict(**ref_model.get_tqdm_dict(), **self.tqdm_metrics)

    @property
    def tng_tqdm_dic(self):
        """Read-only for tqdm metrics.

        .. warning:: .. deprecated:: 0.5.0

            Use `training_tqdm_dict` instead. Will remove 0.8.0.

        """
        warnings.warn("`tng_tqdm_dic` has renamed to `training_tqdm_dict` since v0.5.0"
                      " and this method will be removed in v0.8.0", DeprecationWarning)
        return self.training_tqdm_dict

    # -----------------------------
    # MODEL TRAINING
    # -----------------------------
    def fit(
            self,
            model: LightningModule,
            train_dataloader: Optional[DataLoader] = None,
            val_dataloaders: Optional[DataLoader] = None,
            test_dataloaders: Optional[DataLoader] = None
    ):
        r"""
        Runs the full optimization routine.

        Args:
            model: Model to fit.

            train_dataloader: A Pytorch
                DataLoader with training samples. If the model has
                a predefined train_dataloader method this will be skipped.

            val_dataloaders: Either a single
                Pytorch Dataloader or a list of them, specifying validation samples.
                If the model has a predefined val_dataloaders method this will be skipped

            test_dataloaders: Either a single
                Pytorch Dataloader or a list of them, specifying validation samples.
                If the model has a predefined test_dataloaders method this will be skipped

        Example::

            # Option 1,
            # Define the train_dataloader(), test_dataloader() and val_dataloader() fxs
            # in the lightningModule
            # RECOMMENDED FOR MOST RESEARCH AND APPLICATIONS TO MAINTAIN READABILITY
            trainer = Trainer()
            model = LightningModule()
            trainer.fit(model)

            # Option 2
            # in production cases we might want to pass different datasets to the same model
            # Recommended for PRODUCTION SYSTEMS
            train, val, test = DataLoader(...), DataLoader(...), DataLoader(...)
            trainer = Trainer()
            model = LightningModule()
            trainer.fit(model, train_dataloader=train,
                        val_dataloader=val, test_dataloader=test)

            # Option 1 & 2 can be mixed, for example the training set can be
            # defined as part of the model, and validation/test can then be
            # feed to .fit()

        """
        # bind logger and other properties
        model.logger = self.logger
        self.copy_trainer_model_properties(model)

        # set up the passed in dataloaders (if needed)
        self.__attach_dataloaders(model, train_dataloader, val_dataloaders, test_dataloaders)

        # check that model is configured correctly
        self.check_model_configuration(model)

        # download the data and do whatever transforms we need
        # do before any spawn calls so that the model can assign properties
        # only on proc 0 because no spawn has happened yet
        model.prepare_data()

        # route to appropriate start method
        # when using multi-node or DDP within a node start each module in a separate process
        if self.use_ddp2:
            task = int(os.environ['SLURM_LOCALID'])
            self.ddp_train(task, model)

        elif self.use_ddp:
            if self.is_slurm_managing_tasks:
                task = int(os.environ['SLURM_LOCALID'])
                self.ddp_train(task, model)
            else:
                self.__set_random_port()

                # track for predict
                self.model = model

                # train
                mp.spawn(self.ddp_train, nprocs=self.num_gpus, args=(model,))

                # load weights if not interrupted
                self.load_spawn_weights(model)
                self.model = model

        # 1 gpu or dp option triggers training using DP module
        # easier to avoid NCCL issues
        elif self.use_dp:
            self.dp_train(model)

        elif self.single_gpu:
            self.single_gpu_train(model)

        elif self.use_tpu:  # pragma: no-cover
            log.info(f'training on {self.num_tpu_cores} TPU cores')

            #  COLAB_GPU is an env var available by default in Colab environments.
            start_method = 'fork' if os.getenv('COLAB_GPU') else 'spawn'

            # track for predict
            self.model = model

            # train
            xmp.spawn(self.tpu_train, args=(model,), nprocs=self.num_tpu_cores, start_method=start_method)

            # load weights if not interrupted
            self.load_spawn_weights(model)
            self.model = model

        # ON CPU
        else:
            # run through amp wrapper
            if self.use_amp:
                raise MisconfigurationException('amp + cpu is not supported.  Please use a GPU option')

            # CHOOSE OPTIMIZER
            # allow for lr schedulers as well
            self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

            self.run_pretrain_routine(model)

        # return 1 when finished
        # used for testing or when we need to know that training succeeded
        return 1

    def __set_random_port(self):
        """
        When running DDP NOT managed by SLURM, the ports might collide
        :return:
        """
        try:
            default_port = os.environ['MASTER_PORT']
        except Exception:
            import random
            default_port = random.randint(10000, 19000)
            os.environ['MASTER_PORT'] = str(default_port)

    def __attach_dataloaders(self, model, train_dataloader, val_dataloaders, test_dataloaders):
        # when dataloader is passed via fit, patch the train_dataloader
        # functions to overwrite with these implementations
        if train_dataloader is not None:
            model.train_dataloader = _PatchDataLoader(train_dataloader)

        if val_dataloaders is not None:
            model.val_dataloader = _PatchDataLoader(val_dataloaders)

        if test_dataloaders is not None:
            model.test_dataloader = _PatchDataLoader(test_dataloaders)

    def run_pretrain_routine(self, model: LightningModule):
        """Sanity check a few things before starting actual training.

        Args:
            model: The model to run sanity test on.
        """
        ref_model = model
        if self.data_parallel:
            ref_model = model.module

        # give model convenience properties
        ref_model.trainer = self

        # set local properties on the model
        self.copy_trainer_model_properties(ref_model)

        # log hyper-parameters
        if self.logger is not None:
            # save exp to get started
            if hasattr(ref_model, "hparams"):
                self.logger.log_hyperparams(ref_model.hparams)

            self.logger.save()

        if self.use_ddp or self.use_ddp2:
            torch_distrib.barrier()

        # wait for all models to restore weights
        if self.on_tpu and XLA_AVAILABLE:
            # wait for all processes to catch up
            torch_xla.core.xla_model.rendezvous("pl.Trainer.run_pretrain_routine")

        # register auto-resubmit when on SLURM
        self.register_slurm_signal_handlers()

        # print model summary
        # TODO: remove self.testing condition because model.summarize() is wiping out the weights
        if self.proc_rank == 0 and self.weights_summary is not None and not self.testing:
            if self.weights_summary in ['full', 'top']:
                ref_model.summarize(mode=self.weights_summary)
            else:
                raise MisconfigurationException("weights_summary can be None, 'full' or 'top'")

        # track model now.
        # if cluster resets state, the model will update with the saved weights
        self.model = model

        # set up checkpoint callback
        self.configure_checkpoint_callback()

        # restore training and model before hpc call
        self.restore_weights(model)

        # when testing requested only run test and return
        if self.testing:
            # only load test dataloader for testing
            # self.reset_test_dataloader(ref_model)
            self.run_evaluation(test_mode=True)
            return

        # check if we should run validation during training
        self.disable_validation = not (self.is_overriden('validation_step') and self.val_percent_check > 0) \
            and not self.fast_dev_run

        # run tiny validation (if validation defined)
        # to make sure program won't crash during val
        ref_model.on_sanity_check_start()
        if not self.disable_validation and self.num_sanity_val_steps > 0:
            self.reset_val_dataloader(ref_model)
            # init progress bars for validation sanity check
            pbar = tqdm(desc='Validation sanity check',
                        total=self.num_sanity_val_steps * len(self.val_dataloaders),
                        leave=False, position=2 * self.process_position,
                        disable=not self.progress_bar_refresh_rate, dynamic_ncols=True)
            self.main_progress_bar = pbar
            # dummy validation progress bar
            self.val_progress_bar = tqdm(disable=True)

            eval_results = self._evaluate(model,
                                          self.val_dataloaders,
                                          self.num_sanity_val_steps,
                                          False)
            _, _, _, callback_metrics, _ = self.process_output(eval_results)

            # close progress bars
            self.main_progress_bar.close()
            self.val_progress_bar.close()

            if self.enable_early_stop:
                self.early_stop_callback.check_metrics(callback_metrics)

        # init progress bar
        pbar = tqdm(leave=True, position=2 * self.process_position,
                    disable=not self.show_progress_bar, dynamic_ncols=True,
                    file=sys.stdout, smoothing=0)
        self.main_progress_bar = pbar

        # clear cache before training
        if self.on_gpu:
            torch.cuda.empty_cache()

        # CORE TRAINING LOOP
        self.train()

    def test(self, model: Optional[LightningModule] = None):
        r"""

        Separates from fit to make sure you never run on your test set until you want to.

        Args:
            model: The model to test.

        Example::

            # Option 1
            # run test after fitting
            trainer = Trainer()
            model = LightningModule()

            trainer.fit()
            trainer.test()

            # Option 2
            # run test from a loaded model
            model = LightningModule.load_from_checkpoint('path/to/checkpoint.ckpt')
            trainer = Trainer()
            trainer.test(model)
        """

        self.testing = True
        if model is not None:
            self.model = model
            self.fit(model)
        elif self.use_ddp or self.use_tpu:  # pragma: no-cover
            # attempt to load weights from a spawn
            path = os.path.join(self.default_save_path, '__temp_weight_ddp_end.ckpt')
            test_model = self.model
            if os.path.exists(path):
                test_model = self.load_spawn_weights(self.model)

            self.fit(test_model)
        else:
            self.run_evaluation(test_mode=True)

        self.testing = False

    def check_model_configuration(self, model: LightningModule):
        r"""
        Checks that the model is configured correctly before training is started.

        Args:
            model: The model to test.

        """
        # Check training_step, train_dataloader, configure_optimizer methods
        if not self.is_overriden('training_step', model):
            raise MisconfigurationException(
                'No `training_step()` method defined. Lightning `Trainer` expects as minimum a'
                ' `training_step()`, `training_dataloader()` and `configure_optimizers()` to be defined.')

        if not self.is_overriden('train_dataloader', model):
            raise MisconfigurationException(
                'No `train_dataloader()` method defined. Lightning `Trainer` expects as minimum a'
                ' `training_step()`, `training_dataloader()` and `configure_optimizers()` to be defined.')

        if not self.is_overriden('configure_optimizers', model):
            raise MisconfigurationException(
                'No `configure_optimizers()` method defined. Lightning `Trainer` expects as minimum a'
                ' `training_step()`, `training_dataloader()` and `configure_optimizers()` to be defined.')

        # Check val_dataloader, validation_step and validation_epoch_end
        if self.is_overriden('val_dataloader', model):
            if not self.is_overriden('validation_step', model):
                raise MisconfigurationException('You have passed in a `val_dataloader()`'
                                                ' but have not defined `validation_step()`.')
            else:
                if not self.is_overriden('validation_epoch_end', model):
                    warnings.warn('You have defined a `val_dataloader()` and have'
                                  ' defined a `validation_step()`, you may also want to'
                                  ' define `validation_epoch_end()` for accumulating stats.',
                                  RuntimeWarning)
        else:
            if self.is_overriden('validation_step', model):
                raise MisconfigurationException('You have defined `validation_step()`,'
                                                ' but have not passed in a val_dataloader().')

        # Check test_dataloader, test_step and test_epoch_end
        if self.is_overriden('test_dataloader', model):
            if not self.is_overriden('test_step', model):
                raise MisconfigurationException('You have passed in a `test_dataloader()`'
                                                ' but have not defined `test_step()`.')
            else:
                if not self.is_overriden('test_epoch_end', model):
                    warnings.warn('You have defined a `test_dataloader()` and'
                                  ' have defined a `test_step()`, you may also want to'
                                  ' define `test_epoch_end()` for accumulating stats.',
                                  RuntimeWarning)
        else:
            if self.is_overriden('test_step', model):
                raise MisconfigurationException('You have defined `test_step()`,'
                                                ' but have not passed in a `test_dataloader()`.')


class _PatchDataLoader(object):
    r"""
    Callable object for patching dataloaders passed into trainer.fit().
    Use this class to override model.*_dataloader() and be pickle-compatible.

    Args:
        dataloader: Dataloader object to return when called.

    """

    def __init__(self, dataloader: Union[List[DataLoader], DataLoader]):
        self.dataloader = dataloader

        # cannot pickle __code__ so cannot verify if PatchDataloader
        # exists which shows dataloader methods have been overwritten.
        # so, we hack it by using the string representation
        self.patch_loader_code = str(self.__call__.__code__)

    def __call__(self) -> Union[List[DataLoader], DataLoader]:
        return self.dataloader
