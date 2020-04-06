.. role:: hidden
    :class: hidden-section

.. _callbacks:

Callbacks
=========

Lightning has a callback system to execute arbitrary code. Callbacks should capture NON-ESSENTIAL
logic that is NOT required for your :class:`~pytorch_lightning.core.LightningModule` to run.

An overall Lightning system should have:

1. Trainer for all engineering
2. LightningModule for all research code.
3. Callbacks for non-essential code.


Example:

.. doctest::

    >>> import pytorch_lightning as pl
    >>> class MyPrintingCallback(pl.Callback):
    ...
    ...     def on_init_start(self, trainer):
    ...         print('Starting to init trainer!')
    ...
    ...     def on_init_end(self, trainer):
    ...         print('trainer is init now')
    ...
    ...     def on_train_end(self, trainer, pl_module):
    ...         print('do something when training ends')
    ...
    >>> trainer = pl.Trainer(callbacks=[MyPrintingCallback()])
    Starting to init trainer!
    trainer is init now

We successfully extended functionality without polluting our super clean
:class:`~pytorch_lightning.core.LightningModule` research code.

---------

.. automodule:: pytorch_lightning.callbacks.base
   :noindex:
   :exclude-members:
        _del_model,
        _save_model,
        _abc_impl,
        check_monitor_top_k,

---------

.. automodule:: pytorch_lightning.callbacks.early_stopping
   :noindex:
   :exclude-members:
        _del_model,
        _save_model,
        _abc_impl,
        check_monitor_top_k,

---------

.. automodule:: pytorch_lightning.callbacks.model_checkpoint
   :noindex:
   :exclude-members:
        _del_model,
        _save_model,
        _abc_impl,
        check_monitor_top_k,

---------

.. automodule:: pytorch_lightning.callbacks.gradient_accumulation_scheduler
   :noindex:
   :exclude-members:
        _del_model,
        _save_model,
        _abc_impl,
        check_monitor_top_k,
