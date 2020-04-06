# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## [unreleased] - YYYY-MM-DD

### Added

- Added parity test between a vanilla MNIST model and lightning model ([#1284](https://github.com/PyTorchLightning/pytorch-lightning/pull/1284))
- Added parity test between a vanilla RNN model and lightning model ([#1351](https://github.com/PyTorchLightning/pytorch-lightning/pull/1351))
- Added Reinforcement Learning - Deep Q-network (DQN) lightning example ([#1232](https://github.com/PyTorchLightning/pytorch-lightning/pull/1232))
- Added support for hierarchical `dict` ([#1152](https://github.com/PyTorchLightning/pytorch-lightning/pull/1152))
- Added `TrainsLogger` class ([#1122](https://github.com/PyTorchLightning/pytorch-lightning/pull/1122))
- Added type hints to `pytorch_lightning.core` ([#946](https://github.com/PyTorchLightning/pytorch-lightning/pull/946))
- Added support for `IterableDataset` in validation and testing ([#1104](https://github.com/PyTorchLightning/pytorch-lightning/pull/1104))
- Added support for non-primitive types in `hparams` for `TensorboardLogger` ([#1130](https://github.com/PyTorchLightning/pytorch-lightning/pull/1130))
- Added a check that stops the training when loss or weights contain `NaN` or `inf` values. ([#1097](https://github.com/PyTorchLightning/pytorch-lightning/pull/1097))
- Updated references to `self.forward()` to instead use the `__call__` interface. ([#1211](https://github.com/PyTorchLightning/pytorch-lightning/pull/1211))
- Added support for `IterableDataset` when `val_check_interval=1.0` (default), this will trigger validation at the end of each epoch. ([#1283](https://github.com/PyTorchLightning/pytorch-lightning/pull/1283))
- Added `summary` method to Profilers. ([#1259](https://github.com/PyTorchLightning/pytorch-lightning/pull/1259))
- Added informative errors if user defined dataloader has zero length ([#1280](https://github.com/PyTorchLightning/pytorch-lightning/pull/1280))
- Added testing for python 3.8 ([#915](https://github.com/PyTorchLightning/pytorch-lightning/pull/915)) 
- Added a `training_epoch_end` method which is the mirror of `validation_epoch_end`. ([#1357](https://github.com/PyTorchLightning/pytorch-lightning/pull/1357))
- Added model configuration checking ([#1199](https://github.com/PyTorchLightning/pytorch-lightning/pull/1199))
- Added support for optimizer frequencies through `LightningModule.configure_optimizers()` ([#1269](https://github.com/PyTorchLightning/pytorch-lightning/pull/1269))
- Added option to run without an optimizer by returning `None` from `configure_optimizers`. ([#1279](https://github.com/PyTorchLightning/pytorch-lightning/pull/1279))
- Added a warning when the number of data loader workers is small. ([#1378](https://github.com/PyTorchLightning/pytorch-lightning/pull/1378))

### Changed

- Changed `progress_bar_refresh_rate` trainer flag to disable progress bar when set to 0. ([#1108](https://github.com/PyTorchLightning/pytorch-lightning/pull/1108))
- Enhanced `load_from_checkpoint` to also forward params to the model ([#1307](https://github.com/PyTorchLightning/pytorch-lightning/pull/1307))
- Updated references to self.forward() to instead use the `__call__` interface. ([#1211](https://github.com/PyTorchLightning/pytorch-lightning/pull/1211))
- Changed default behaviour of `configure_optimizers` to use no optimizer rather than Adam. ([#1279](https://github.com/PyTorchLightning/pytorch-lightning/pull/1279))
- Allow to upload models on W&B ([#1339](https://github.com/PyTorchLightning/pytorch-lightning/pull/1339))
- On DP and DDP2 unsqueeze is automated now ([#1319](https://github.com/PyTorchLightning/pytorch-lightning/pull/1319))
- Did not always create a DataLoader during reinstantiation, but the same type as before (if subclass of DataLoader) ([#1346](https://github.com/PyTorchLightning/pytorch-lightning/pull/1346))
- Did not interfere with a default sampler ([#1318](https://github.com/PyTorchLightning/pytorch-lightning/pull/1318))
- Remove default Adam optimizer ([#1317](https://github.com/PyTorchLightning/pytorch-lightning/pull/1317))
- Give warnings for unimplemented required lightning methods ([#1317](https://github.com/PyTorchLightning/pytorch-lightning/pull/1317))
- Enhanced load_from_checkpoint to also forward params to the model ([#1307](https://github.com/PyTorchLightning/pytorch-lightning/pull/1307))
- Made `evaluate` method private >> `Trainer._evaluate(...)`. ([#1260](https://github.com/PyTorchLightning/pytorch-lightning/pull/1260))
- Simplify the PL examples structure (shallower and more readable) ([#1247](https://github.com/PyTorchLightning/pytorch-lightning/pull/1247))
- Changed min max gpu memory to be on their own plots ([#1358](https://github.com/PyTorchLightning/pytorch-lightning/pull/1358))
- Remove `.item` which causes sync issues ([#1254](https://github.com/PyTorchLightning/pytorch-lightning/pull/1254))
- Changed smoothing in TQDM to decrease variability of time remaining between training / eval ([#1194](https://github.com/PyTorchLightning/pytorch-lightning/pull/1194))
- Change default logger to dedicated one ([#1064](https://github.com/PyTorchLightning/pytorch-lightning/pull/1064))

### Deprecated

- Deprecated Trainer argument `print_nan_grads` ([#1097](https://github.com/PyTorchLightning/pytorch-lightning/pull/1097))
- Deprecated Trainer argument `show_progress_bar` ([#1108](https://github.com/PyTorchLightning/pytorch-lightning/pull/1108))

### Removed

- Removed duplicated module `pytorch_lightning.utilities.arg_parse` for loading CLI arguments ([#1167](https://github.com/PyTorchLightning/pytorch-lightning/issues/1167))
- Removed wandb logger's `finalize` method ([#1193](https://github.com/PyTorchLightning/pytorch-lightning/pull/1193))
- Dropped `torchvision` dependency in tests and added own MNIST dataset class instead ([#986](https://github.com/PyTorchLightning/pytorch-lightning/issues/986))

### Fixed

- Fixed `model_checkpoint` when saving all models ([#1359](https://github.com/PyTorchLightning/pytorch-lightning/pull/1359))
- `Trainer.add_argparse_args` classmethod fixed. Now it adds a type for the arguments ([#1147](https://github.com/PyTorchLightning/pytorch-lightning/pull/1147))
- Fixed bug related to type cheking of `ReduceLROnPlateau` lr schedulers([#1114](https://github.com/PyTorchLightning/pytorch-lightning/issues/1114))
- Fixed a bug to ensure lightning checkpoints to be backward compatible ([#1132](https://github.com/PyTorchLightning/pytorch-lightning/pull/1132))
- Fixed a bug that created an extra dataloader with active `reload_dataloaders_every_epoch` ([#1181](https://github.com/PyTorchLightning/pytorch-lightning/issues/1181)
- Fixed all warnings and errors in the docs build process ([#1191](https://github.com/PyTorchLightning/pytorch-lightning/pull/1191))
- Fixed an issue where `val_percent_check=0` would not disable validation ([#1251](https://github.com/PyTorchLightning/pytorch-lightning/pull/1251))
- Fixed average of incomplete `TensorRunningMean` ([#1309](https://github.com/PyTorchLightning/pytorch-lightning/pull/1309))
- Fixed `WandbLogger.watch` with `wandb.init()` ([#1311](https://github.com/PyTorchLightning/pytorch-lightning/pull/1311))
- Fixed an issue with early stopping that would prevent it from monitoring training metrics when validation is disabled / not implemented ([#1235](https://github.com/PyTorchLightning/pytorch-lightning/pull/1235)). 
- Fixed a bug that would cause `trainer.test()` to run on the validation set when overloading `validation_epoch_end ` and `test_end` ([#1353](https://github.com/PyTorchLightning/pytorch-lightning/pull/1353)).
- Fixed `WandbLogger.watch` - use of the watch method without importing `wandb` ([#1311](https://github.com/PyTorchLightning/pytorch-lightning/pull/1311))
- Fixed `WandbLogger` to be used with 'ddp' - allow reinits in sub-processes ([#1149](https://github.com/PyTorchLightning/pytorch-lightning/pull/1149), [#1360](https://github.com/PyTorchLightning/pytorch-lightning/pull/1360))
- Made `training_epoch_end` behave like `validation_epoch_end` ([#1357](https://github.com/PyTorchLightning/pytorch-lightning/pull/1357))
- Fixed `fast_dev_run` running validation twice ([#1365](https://github.com/PyTorchLightning/pytorch-lightning/pull/1365))
- Fixed pickle error from quick patch `__code__` ([#1352](https://github.com/PyTorchLightning/pytorch-lightning/pull/1352))
- Fixed memory leak on GPU0 ([#1094](https://github.com/PyTorchLightning/pytorch-lightning/pull/1094), [#1349](https://github.com/PyTorchLightning/pytorch-lightning/pull/1349))
- Fixed checkpointing interval ([#1272](https://github.com/PyTorchLightning/pytorch-lightning/pull/1272)) 
- Fixed validation and training loops run the partial dataset ([#1192](https://github.com/PyTorchLightning/pytorch-lightning/pull/1192))
- Fixed running `on_validation_end` only on main process in DDP ([#1125](https://github.com/PyTorchLightning/pytorch-lightning/pull/1125))
- Fixes `use_amp` issue ([#1145](https://github.com/PyTorchLightning/pytorch-lightning/pull/1145))
- Fixes using deprecated `use_amp` attribute ([#1145](https://github.com/PyTorchLightning/pytorch-lightning/pull/1145))

## [0.7.1] - 2020-03-07

### Fixed

- Fixes `print` issues and `data_loader` ([#1080](https://github.com/PyTorchLightning/pytorch-lightning/pull/1080))

## [0.7.0] - 2020-03-06

### Added

- Added automatic sampler setup. Depending on DDP or TPU, lightning configures the sampler correctly (user needs to do nothing) ([#926](https://github.com/PyTorchLightning/pytorch-lightning/pull/926))
- Added `reload_dataloaders_every_epoch=False` flag for trainer. Some users require reloading data every epoch ([#926](https://github.com/PyTorchLightning/pytorch-lightning/pull/926))
- Added `progress_bar_refresh_rate=50` flag for trainer. Throttle refresh rate on notebooks ([#926](https://github.com/PyTorchLightning/pytorch-lightning/pull/926))
- Updated governance docs
- Added a check to ensure that the metric used for early stopping exists before training commences ([#542](https://github.com/PyTorchLightning/pytorch-lightning/pull/542))
- Added `optimizer_idx` argument to `backward` hook ([#733](https://github.com/PyTorchLightning/pytorch-lightning/pull/733))
- Added `entity` argument to `WandbLogger` to be passed to `wandb.init` ([#783](https://github.com/PyTorchLightning/pytorch-lightning/pull/783))
- Added a tool for profiling training runs ([#782](https://github.com/PyTorchLightning/pytorch-lightning/pull/782))
- Improved flexibility for naming of TensorBoard logs, can now set `version` to a `str` to just save to that directory, and use `name=''` to prevent experiment-name directory ([#804](https://github.com/PyTorchLightning/pytorch-lightning/pull/804))
- Added option to specify `step` key when logging metrics ([#808](https://github.com/PyTorchLightning/pytorch-lightning/pull/808))
- Added `train_dataloader`, `val_dataloader` and `test_dataloader` arguments to `Trainer.fit()`, for alternative data parsing ([#759](https://github.com/PyTorchLightning/pytorch-lightning/pull/759))
- Added Tensor Processing Unit (TPU) support ([#868](https://github.com/PyTorchLightning/pytorch-lightning/pull/868))
- Added semantic segmentation example ([#751](https://github.com/PyTorchLightning/pytorch-lightning/pull/751),[#876](https://github.com/PyTorchLightning/pytorch-lightning/pull/876), [#881](https://github.com/PyTorchLightning/pytorch-lightning/pull/881))
- Split callbacks in multiple files ([#849](https://github.com/PyTorchLightning/pytorch-lightning/pull/849))
- Support for user defined callbacks ([#889](https://github.com/PyTorchLightning/pytorch-lightning/pull/889) and [#950](https://github.com/PyTorchLightning/pytorch-lightning/pull/950))
- Added support for multiple loggers to be passed to `Trainer` as an iterable (e.g. list, tuple, etc.) ([#903](https://github.com/PyTorchLightning/pytorch-lightning/pull/903))
- Added support for step-based learning rate scheduling ([#941](https://github.com/PyTorchLightning/pytorch-lightning/pull/941))
- Added support for logging `hparams` as dict ([#1029](https://github.com/PyTorchLightning/pytorch-lightning/pull/1029))
- Checkpoint and early stopping now work without val. step ([#1041](https://github.com/PyTorchLightning/pytorch-lightning/pull/1041))
- Support graceful training cleanup after Keyboard Interrupt ([#856](https://github.com/PyTorchLightning/pytorch-lightning/pull/856), [#1019](https://github.com/PyTorchLightning/pytorch-lightning/pull/1019))
- Added type hints for function arguments ([#912](https://github.com/PyTorchLightning/pytorch-lightning/pull/912), )
- Added default `argparser` for `Trainer` ([#952](https://github.com/PyTorchLightning/pytorch-lightning/pull/1023), [#1023](https://github.com/PyTorchLightning/pytorch-lightning/pull/1023))
- Added TPU gradient clipping ([#963](https://github.com/PyTorchLightning/pytorch-lightning/pull/963))
- Added max/min number of steps in `Trainer` ([#728](https://github.com/PyTorchLightning/pytorch-lightning/pull/728))

### Changed

- Improved `NeptuneLogger` by adding `close_after_fit` argument to allow logging after training([#908](https://github.com/PyTorchLightning/pytorch-lightning/pull/1084))
- Changed default TQDM to use `tqdm.auto` for prettier outputs in IPython notebooks ([#752](https://github.com/PyTorchLightning/pytorch-lightning/pull/752))
- Changed `pytorch_lightning.logging` to `pytorch_lightning.loggers` ([#767](https://github.com/PyTorchLightning/pytorch-lightning/pull/767))
- Moved the default `tqdm_dict` definition from Trainer to `LightningModule`, so it can be overridden by the user ([#749](https://github.com/PyTorchLightning/pytorch-lightning/pull/749))
- Moved functionality of `LightningModule.load_from_metrics` into `LightningModule.load_from_checkpoint` ([#995](https://github.com/PyTorchLightning/pytorch-lightning/pull/995))
- Changed Checkpoint path parameter from `filepath` to `dirpath` ([#1016](https://github.com/PyTorchLightning/pytorch-lightning/pull/1016))
- Freezed models `hparams` as `Namespace` property ([#1029](https://github.com/PyTorchLightning/pytorch-lightning/pull/1029))
- Dropped `logging` config in package init ([#1015](https://github.com/PyTorchLightning/pytorch-lightning/pull/1015))
- Renames model steps ([#1051](https://github.com/PyTorchLightning/pytorch-lightning/pull/1051))
  - `training_end` >> `training_epoch_end`
  - `validation_end` >> `validation_epoch_end`
  - `test_end` >> `test_epoch_end`
- Refactor dataloading, supports infinite dataloader ([#955](https://github.com/PyTorchLightning/pytorch-lightning/pull/955))
- Create single file in `TensorBoardLogger` ([#777](https://github.com/PyTorchLightning/pytorch-lightning/pull/777))

### Deprecated

- Deprecated `pytorch_lightning.logging` ([#767](https://github.com/PyTorchLightning/pytorch-lightning/pull/767))
- Deprecated `LightningModule.load_from_metrics` in favour of `LightningModule.load_from_checkpoint` ([#995](https://github.com/PyTorchLightning/pytorch-lightning/pull/995), [#1079](https://github.com/PyTorchLightning/pytorch-lightning/pull/1079))
- Deprecated `@data_loader` decorator ([#926](https://github.com/PyTorchLightning/pytorch-lightning/pull/926))
- Deprecated model steps `training_end`, `validation_end` and `test_end` ([#1051](https://github.com/PyTorchLightning/pytorch-lightning/pull/1051), [#1056](https://github.com/PyTorchLightning/pytorch-lightning/pull/1056))

### Removed

- Removed dependency on `pandas` ([#736](https://github.com/PyTorchLightning/pytorch-lightning/pull/736))
- Removed dependency on `torchvision` ([#797](https://github.com/PyTorchLightning/pytorch-lightning/pull/797))
- Removed dependency on `scikit-learn` ([#801](https://github.com/PyTorchLightning/pytorch-lightning/pull/801))

### Fixed

- Fixed a bug where early stopping `on_end_epoch` would be called inconsistently when `check_val_every_n_epoch == 0` ([#743](https://github.com/PyTorchLightning/pytorch-lightning/pull/743))
- Fixed a bug where the model checkpointer didn't write to the same directory as the logger ([#771](https://github.com/PyTorchLightning/pytorch-lightning/pull/771))
- Fixed a bug where the `TensorBoardLogger` class would create an additional empty log file during fitting ([#777](https://github.com/PyTorchLightning/pytorch-lightning/pull/777))
- Fixed a bug where `global_step` was advanced incorrectly when using `accumulate_grad_batches > 1` ([#832](https://github.com/PyTorchLightning/pytorch-lightning/pull/832))
- Fixed a bug when calling `self.logger.experiment` with multiple loggers ([#1009](https://github.com/PyTorchLightning/pytorch-lightning/pull/1009))
- Fixed a bug when calling `logger.append_tags` on a `NeptuneLogger` with a single tag ([#1009](https://github.com/PyTorchLightning/pytorch-lightning/pull/1009))
- Fixed sending back data from `.spawn` by saving and loading the trained model in/out of the process ([#1017](https://github.com/PyTorchLightning/pytorch-lightning/pull/1017)
- Fixed port collision on DDP ([#1010](https://github.com/PyTorchLightning/pytorch-lightning/pull/1010))
- Fixed/tested pass overrides ([#918](https://github.com/PyTorchLightning/pytorch-lightning/pull/918))
- Fixed comet logger to log after train ([#892](https://github.com/PyTorchLightning/pytorch-lightning/pull/892))
- Remove deprecated args to learning rate step function ([#890](https://github.com/PyTorchLightning/pytorch-lightning/pull/890))

## [0.6.0] - 2020-01-21

### Added

- Added support for resuming from a specific checkpoint via `resume_from_checkpoint` argument ([#516](https://github.com/PyTorchLightning/pytorch-lightning/pull/516))
- Added support for `ReduceLROnPlateau` scheduler ([#320](https://github.com/PyTorchLightning/pytorch-lightning/pull/320))
- Added support for Apex mode `O2` in conjunction with Data Parallel ([#493](https://github.com/PyTorchLightning/pytorch-lightning/pull/493))
- Added option (`save_top_k`) to save the top k models in the `ModelCheckpoint` class ([#128](https://github.com/PyTorchLightning/pytorch-lightning/pull/128))
- Added `on_train_start` and `on_train_end` hooks to `ModelHooks` ([#598](https://github.com/PyTorchLightning/pytorch-lightning/pull/598))
- Added `TensorBoardLogger` ([#607](https://github.com/PyTorchLightning/pytorch-lightning/pull/607))
- Added support for weight summary of model with multiple inputs ([#543](https://github.com/PyTorchLightning/pytorch-lightning/pull/543))
- Added `map_location` argument to `load_from_metrics` and `load_from_checkpoint` ([#625](https://github.com/PyTorchLightning/pytorch-lightning/pull/625))
- Added option to disable validation by setting `val_percent_check=0` ([#649](https://github.com/PyTorchLightning/pytorch-lightning/pull/649))
- Added `NeptuneLogger` class ([#648](https://github.com/PyTorchLightning/pytorch-lightning/pull/648))
- Added `WandbLogger` class ([#627](https://github.com/PyTorchLightning/pytorch-lightning/pull/627))

### Changed

- Changed the default progress bar to print to stdout instead of stderr ([#531](https://github.com/PyTorchLightning/pytorch-lightning/pull/531))
- Renamed `step_idx` to `step`, `epoch_idx` to `epoch`, `max_num_epochs` to `max_epochs` and `min_num_epochs` to `min_epochs` ([#589](https://github.com/PyTorchLightning/pytorch-lightning/pull/589))
- Renamed `total_batch_nb` to `total_batches`, `nb_val_batches` to `num_val_batches`, `nb_training_batches` to `num_training_batches`, `max_nb_epochs` to `max_epochs`, `min_nb_epochs` to `min_epochs`, `nb_test_batches` to `num_test_batches`, and `nb_val_batches` to `num_val_batches` ([#567](https://github.com/PyTorchLightning/pytorch-lightning/pull/567))
- Changed gradient logging to use parameter names instead of indexes ([#660](https://github.com/PyTorchLightning/pytorch-lightning/pull/660))
- Changed the default logger to `TensorBoardLogger` ([#609](https://github.com/PyTorchLightning/pytorch-lightning/pull/609))
- Changed the directory for tensorboard logging to be the same as model checkpointing ([#706](https://github.com/PyTorchLightning/pytorch-lightning/pull/706))

### Deprecated

- Deprecated `max_nb_epochs` and `min_nb_epochs` ([#567](https://github.com/PyTorchLightning/pytorch-lightning/pull/567))
- Deprecated the `on_sanity_check_start` hook in `ModelHooks` ([#598](https://github.com/PyTorchLightning/pytorch-lightning/pull/598))

### Removed

- Removed the `save_best_only` argument from `ModelCheckpoint`, use `save_top_k=1` instead ([#128](https://github.com/PyTorchLightning/pytorch-lightning/pull/128))

### Fixed

- Fixed a bug which ocurred when using Adagrad with cuda ([#554](https://github.com/PyTorchLightning/pytorch-lightning/pull/554))
- Fixed a bug where training would be on the GPU despite setting `gpus=0` or `gpus=[]` ([#561](https://github.com/PyTorchLightning/pytorch-lightning/pull/561))
- Fixed an error with `print_nan_gradients` when some parameters do not require gradient ([#579](https://github.com/PyTorchLightning/pytorch-lightning/pull/579))
- Fixed a bug where the progress bar would show an incorrect number of total steps during the validation sanity check when using multiple validation data loaders ([#597](https://github.com/PyTorchLightning/pytorch-lightning/pull/597))
- Fixed support for PyTorch 1.1.0 ([#552](https://github.com/PyTorchLightning/pytorch-lightning/pull/552))
- Fixed an issue with early stopping when using a `val_check_interval < 1.0` in `Trainer` ([#492](https://github.com/PyTorchLightning/pytorch-lightning/pull/492))
- Fixed bugs relating to the `CometLogger` object that would cause it to not work properly ([#481](https://github.com/PyTorchLightning/pytorch-lightning/pull/481))
- Fixed a bug that would occur when returning `-1` from `on_batch_start` following an early exit or when the batch was `None` ([#509](https://github.com/PyTorchLightning/pytorch-lightning/pull/509))
- Fixed a potential race condition with several processes trying to create checkpoint directories ([#530](https://github.com/PyTorchLightning/pytorch-lightning/pull/530))
- Fixed a bug where batch 'segments' would remain on the GPU when using `truncated_bptt > 1` ([#532](https://github.com/PyTorchLightning/pytorch-lightning/pull/532))
- Fixed a bug when using `IterableDataset` ([#547](https://github.com/PyTorchLightning/pytorch-lightning/pull/547))
- Fixed a bug where `.item` was called on non-tensor objects ([#602](https://github.com/PyTorchLightning/pytorch-lightning/pull/602))
- Fixed a bug where `Trainer.train` would crash on an uninitialized variable if the trainer was run after resuming from a checkpoint that was already at `max_epochs` ([#608](https://github.com/PyTorchLightning/pytorch-lightning/pull/608))
- Fixed a bug where early stopping would begin two epochs early ([#617](https://github.com/PyTorchLightning/pytorch-lightning/pull/617))
- Fixed a bug where `num_training_batches` and `num_test_batches` would sometimes be rounded down to zero ([#649](https://github.com/PyTorchLightning/pytorch-lightning/pull/649))
- Fixed a bug where an additional batch would be processed when manually setting `num_training_batches` ([#653](https://github.com/PyTorchLightning/pytorch-lightning/pull/653))
- Fixed a bug when batches did not have a `.copy` method ([#701](https://github.com/PyTorchLightning/pytorch-lightning/pull/701))
- Fixed a bug when using `log_gpu_memory=True` in Python 3.6 ([#715](https://github.com/PyTorchLightning/pytorch-lightning/pull/715))
- Fixed a bug where checkpoint writing could exit before completion, giving incomplete checkpoints ([#689](https://github.com/PyTorchLightning/pytorch-lightning/pull/689))
- Fixed a bug where `on_train_end` was not called when ealy stopping ([#723](https://github.com/PyTorchLightning/pytorch-lightning/pull/723))

## [0.5.3] - 2019-11-06

### Added

- Added option to disable default logger, checkpointer, and early stopping by passing `logger=False`, `checkpoint_callback=False` and `early_stop_callback=False` respectively
- Added `CometLogger` for use with Comet.ml
- Added `val_check_interval` argument to `Trainer` allowing validition to be performed at every given number of batches
- Added functionality to save and load hyperparameters using the standard checkpoint mechanism
- Added call to `torch.cuda.empty_cache` before training starts
- Added option for user to override the call t `backward`
- Added support for truncated backprop through time via the `truncated_bptt_steps` argument in `Trainer`
- Added option to operate on all outputs from `training_step` in DDP2
- Added a hook for modifying DDP init
- Added a hook for modifying Apex

### Changed

- Changed experiment version to be padded with zeros (e.g. `/dir/version_9` becomes `/dir/version_0009`)
- Changed callback metrics to include any metrics given in logs or progress bar
- Changed the default for `save_best_only` in `ModelCheckpoint` to `True`
- Added `tng_data_loader` for backwards compatibility
- Renamed `MLFlowLogger.client` to `MLFlowLogger.experiment` for consistency
- Moved `global_step` increment to happen after the batch has been processed
- Changed weights restore to first attempt HPC weights before restoring normally, preventing both weights being restored and running out of memory
- Changed progress bar functionality to add multiple progress bars for train/val/test
- Changed calls to `print` to use `logging` instead

### Deprecated

- Deprecated `tng_dataloader`

### Fixed

- Fixed an issue where the number of batches was off by one during training
- Fixed a bug that occured when setting a ckeckpoint callback and `early_stop_callback=False`
- Fixed an error when importing CometLogger
- Fixed a bug where the `gpus` argument had some unexpected behaviour
- Fixed a bug where the computed total number of batches was sometimes incorrect
- Fixed a bug where the progress bar would sometimes not show the total number of batches in test mode
- Fixed a bug when using the `log_gpu_memory='min_max'` option in `Trainer`
- Fixed a bug where checkpointing would sometimes erase the current directory

## [0.5.2] - 2019-10-10

### Added

- Added `weights_summary` argument to `Trainer` to be set to `full` (full summary), `top` (just top level modules) or other
- Added `tags` argument to `MLFlowLogger`

### Changed

- Changed default for `amp_level` to `O1`

### Removed

- Removed the `print_weights_summary` argument from `Trainer`

### Fixed

- Fixed a bug where logs were not written properly
- Fixed a bug where `logger.finalize` wasn't called after training is complete
- Fixed callback metric errors in DDP
- Fixed a bug where `TestTubeLogger` didn't log to the correct directory

## [0.5.1] - 2019-10-05

### Added

- Added the `LightningLoggerBase` class for experiment loggers
- Added `MLFlowLogger` for logging with `mlflow`
- Added `TestTubeLogger` for logging with `test_tube`
- Added a different implementation of DDP (`distributed_backed='ddp2'`) where every node has one model using all GPUs
- Added support for optimisers which require a closure (e.g. LBFGS)
- Added automatic `MASTER_PORT` defualt for DDP when not set manually
- Added new GPU memory logging options `'min_max'` (log only the min/max utilization) and `'all'` (log all the GPU memory)

### Changed

- Changed schedulers to always be called with the current epoch
- Changed `test_tube` to an optional dependency
- Changed data loaders to internally use a getter instead of a python property
- Disabled auto GPU loading when restoring weights to prevent out of memory errors
- Changed logging, early stopping and checkpointing to occur by default

### Fixed

- Fixed a bug with samplers that do not specify `set_epoch`
- Fixed a bug when using the `MLFlowLogger` with unsupported data types, this will now raise a warning
- Fixed a bug where gradient norms were alwasy zero using `track_grad_norm`
- Fixed a bug which causes a crash when logging memory

## [0.5.0] - 2019-09-26

### Changed

- Changed `data_batch` argument to `batch` throughout
- Changed `batch_i` argument to `batch_idx` throughout
- Changed `tng_dataloader` method to `train_dataloader`
- Changed `on_tng_metrics` method to `on_training_metrics`
- Changed `gradient_clip` argument to `gradient_clip_val`
- Changed `add_log_row_interval` to `row_log_interval`

### Fixed

- Fixed a bug with tensorboard logging in multi-gpu setup

## [0.4.9] - 2019-09-16

### Added

- Added the flag `log_gpu_memory` to `Trainer` to deactivate logging of GPU memory utilization
- Added SLURM resubmit functionality (port from test-tube)
- Added optional weight_save_path to trainer to remove the need for a checkpoint_callback when using cluster training
- Added option to use single gpu per node with `DistributedDataParallel`

### Changed

- Changed functionality of `validation_end` and `test_end` with multiple dataloaders to be given all of the dataloaders at once rather than in seperate calls
- Changed print_nan_grads to only print the parameter value and gradients when they contain NaN
- Changed gpu API to take integers as well (e.g. `gpus=2` instead of `gpus=[0, 1]`)
- All models now loaded on to CPU to avoid device and out of memory issues in PyTorch

### Fixed

- Fixed a bug where data types that implement `.to` but not `.cuda` would not be properly moved onto the GPU
- Fixed a bug where data would not be re-shuffled every epoch when using a `DistributedSampler`

## [0.4.8] - 2019-08-31

### Added

- Added `test_step` and `test_end` methods, used when `Trainer.test` is called
- Added `GradientAccumulationScheduler` callback which can be used to schedule changes to the number of accumulation batches
- Added option to skip the validation sanity check by setting `nb_sanity_val_steps = 0`

### Fixed

- Fixed a bug when setting `nb_sanity_val_steps = 0`

## [0.4.7] - 2019-08-24

### Changed

- Changed the default `val_check_interval` to `1.0`
- Changed defaults for `nb_val_batches`, `nb_tng_batches` and `nb_test_batches` to 0

### Fixed

- Fixed a bug where the full validation set as used despite setting `val_percent_check`
- Fixed a bug where an `Exception` was thrown when using a data set containing a single batch
- Fixed a bug where an `Exception` was thrown if no `val_dataloader` was given
- Fixed a bug where tuples were not properly transfered to the GPU
- Fixed a bug where data of a non standard type was not properly handled by the trainer
- Fixed a bug when loading data as a tuple
- Fixed a bug where `AttributeError` could be suppressed by the `Trainer`

## [0.4.6] - 2019-08-15

### Added

- Added support for data to be given as a `dict` or `list` with a single gpu
- Added support for `configure_optimizers` to return a single optimizer, two list (optimizers and schedulers), or a single list

### Fixed

- Fixed a bug where returning just an optimizer list (i.e. without schedulers) from `configure_optimizers` would throw an `Exception`

## [0.4.5] - 2019-08-13

### Added

- Added `optimizer_step` method that can be overridden to change the standard optimizer behaviour

## [0.4.4] - 2019-08-12

### Added

- Added supoort for multiple validation dataloaders
- Added support for latest test-tube logger (optimised for `torch==1.2.0`)

### Changed

- `validation_step` and `val_dataloader` are now optional
- `lr_scheduler` is now activated after epoch

### Fixed

- Fixed a bug where a warning would show when using `lr_scheduler` in `torch>1.1.0`
- Fixed a bug where an `Exception` would be thrown if using `torch.DistributedDataParallel` without using a `DistributedSampler`, this now throws a `Warning` instead

## [0.4.3] - 2019-08-10

### Fixed

- Fixed a bug where accumulate gradients would scale the loss incorrectly

## [0.4.2] - 2019-08-08

### Changed

- Changed install requirement to `torch==1.2.0`

## [0.4.1] - 2019-08-08

### Changed

- Changed install requirement to `torch==1.1.0`

## [0.4.0] - 2019-08-08

### Added

- Added 16-bit support for a single GPU
- Added support for training continuation (preserves epoch, global step etc.)

### Changed

- Changed `training_step` and `validation_step`, outputs will no longer be automatically reduced

### Removed

- Removed need for `Experiment` object in `Trainer`

### Fixed

- Fixed issues with reducing outputs from generative models (such as images and text)

## [0.3.6] - 2019-07-25

### Added

- Added a decorator to do lazy data loading internally

### Fixed

- Fixed a bug where `Experiment` object was not process safe, potentially causing logs to be overwritten

## [0.3.5] - 2019-MM-DD

## [0.3.4] - 2019-MM-DD

## [0.3.3] - 2019-MM-DD

## [0.3.2] - 2019-MM-DD

## [0.3.1] - 2019-MM-DD

## [0.2.x] - YYYY-MM-DD

## [0.1.x] - YYYY-MM-DD
