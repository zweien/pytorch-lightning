import pickle
from unittest.mock import MagicMock

import tests.base.utils as tutils
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import LightningLoggerBase, rank_zero_only, LoggerCollection
from tests.base import LightningTestModel


def test_logger_collection():
    mock1 = MagicMock()
    mock2 = MagicMock()

    logger = LoggerCollection([mock1, mock2])

    assert logger[0] == mock1
    assert logger[1] == mock2

    assert logger.experiment[0] == mock1.experiment
    assert logger.experiment[1] == mock2.experiment

    logger.close()
    mock1.close.assert_called_once()
    mock2.close.assert_called_once()


class CustomLogger(LightningLoggerBase):
    def __init__(self):
        super().__init__()
        self.hparams_logged = None
        self.metrics_logged = None
        self.finalized = False

    @property
    def experiment(self):
        return 'test'

    @rank_zero_only
    def log_hyperparams(self, params):
        self.hparams_logged = params

    @rank_zero_only
    def log_metrics(self, metrics, step):
        self.metrics_logged = metrics

    @rank_zero_only
    def finalize(self, status):
        self.finalized_status = status

    @property
    def name(self):
        return "name"

    @property
    def version(self):
        return "1"


def test_custom_logger(tmpdir):
    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    logger = CustomLogger()

    trainer_options = dict(
        max_epochs=1,
        train_percent_check=0.05,
        logger=logger,
        default_save_path=tmpdir
    )

    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)
    assert result == 1, "Training failed"
    assert logger.hparams_logged == hparams
    assert logger.metrics_logged != {}
    assert logger.finalized_status == "success"


def test_multiple_loggers(tmpdir):
    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    logger1 = CustomLogger()
    logger2 = CustomLogger()

    trainer_options = dict(
        max_epochs=1,
        train_percent_check=0.05,
        logger=[logger1, logger2],
        default_save_path=tmpdir
    )

    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)
    assert result == 1, "Training failed"

    assert logger1.hparams_logged == hparams
    assert logger1.metrics_logged != {}
    assert logger1.finalized_status == "success"

    assert logger2.hparams_logged == hparams
    assert logger2.metrics_logged != {}
    assert logger2.finalized_status == "success"


def test_multiple_loggers_pickle(tmpdir):
    """Verify that pickling trainer with multiple loggers works."""

    logger1 = CustomLogger()
    logger2 = CustomLogger()

    trainer_options = dict(max_epochs=1, logger=[logger1, logger2])

    trainer = Trainer(**trainer_options)
    pkl_bytes = pickle.dumps(trainer)
    trainer2 = pickle.loads(pkl_bytes)
    trainer2.logger.log_metrics({"acc": 1.0}, 0)

    assert logger1.metrics_logged != {}
    assert logger2.metrics_logged != {}


def test_adding_step_key(tmpdir):
    logged_step = 0

    def _validation_epoch_end(outputs):
        nonlocal logged_step
        logged_step += 1
        return {"log": {"step": logged_step, "val_acc": logged_step / 10}}

    def _training_epoch_end(outputs):
        nonlocal logged_step
        logged_step += 1
        return {"log": {"step": logged_step, "train_acc": logged_step / 10}}

    def _log_metrics_decorator(log_metrics_fn):
        def decorated(metrics, step):
            if "val_acc" in metrics:
                assert step == logged_step
            return log_metrics_fn(metrics, step)

        return decorated

    model, hparams = tutils.get_default_model()
    model.validation_epoch_end = _validation_epoch_end
    model.training_epoch_end = _training_epoch_end
    trainer_options = dict(
        max_epochs=4,
        default_save_path=tmpdir,
        train_percent_check=0.001,
        val_percent_check=0.01,
        num_sanity_val_steps=0,
    )
    trainer = Trainer(**trainer_options)
    trainer.logger.log_metrics = _log_metrics_decorator(trainer.logger.log_metrics)
    trainer.fit(model)
