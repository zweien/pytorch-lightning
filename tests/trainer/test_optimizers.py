import pytest
import torch

import tests.base.utils as tutils
from pytorch_lightning import Trainer

from tests.base import (
    TestModelBase,
    LightTrainDataloader,
    LightValidationStepMixin,
    LightValidationMixin,
    LightTestOptimizerWithSchedulingMixin,
    LightTestMultipleOptimizersWithSchedulingMixin,
    LightTestOptimizersWithMixedSchedulingMixin,
    LightTestReduceLROnPlateauMixin,
    LightTestNoneOptimizerMixin
)


def test_optimizer_with_scheduling(tmpdir):
    """ Verify that learning rate scheduling is working """
    tutils.reset_seed()

    class CurrentTestModel(
            LightTestOptimizerWithSchedulingMixin,
            LightTrainDataloader,
            TestModelBase):
        pass

    hparams = tutils.get_default_hparams()
    model = CurrentTestModel(hparams)

    # logger file to get meta
    trainer_options = dict(
        default_save_path=tmpdir,
        max_epochs=1,
        val_percent_check=0.1,
        train_percent_check=0.2
    )

    # fit model
    trainer = Trainer(**trainer_options)
    results = trainer.fit(model)

    init_lr = hparams.learning_rate
    adjusted_lr = [pg['lr'] for pg in trainer.optimizers[0].param_groups]

    assert len(trainer.lr_schedulers) == 1, \
        'lr scheduler not initialized properly, it has %i elements instread of 1' % len(trainer.lr_schedulers)

    assert all(a == adjusted_lr[0] for a in adjusted_lr), \
        'Lr not equally adjusted for all param groups'
    adjusted_lr = adjusted_lr[0]

    assert init_lr * 0.1 == adjusted_lr, \
        'Lr not adjusted correctly, expected %f but got %f' % (init_lr * 0.1, adjusted_lr)


def test_multi_optimizer_with_scheduling(tmpdir):
    """ Verify that learning rate scheduling is working """
    tutils.reset_seed()

    class CurrentTestModel(
            LightTestMultipleOptimizersWithSchedulingMixin,
            LightTrainDataloader,
            TestModelBase):
        pass

    hparams = tutils.get_default_hparams()
    model = CurrentTestModel(hparams)

    # logger file to get meta
    trainer_options = dict(
        default_save_path=tmpdir,
        max_epochs=1,
        val_percent_check=0.1,
        train_percent_check=0.2
    )

    # fit model
    trainer = Trainer(**trainer_options)
    results = trainer.fit(model)

    init_lr = hparams.learning_rate
    adjusted_lr1 = [pg['lr'] for pg in trainer.optimizers[0].param_groups]
    adjusted_lr2 = [pg['lr'] for pg in trainer.optimizers[1].param_groups]

    assert len(trainer.lr_schedulers) == 2, \
        'all lr scheduler not initialized properly, it has %i elements instread of 1' % len(trainer.lr_schedulers)

    assert all(a == adjusted_lr1[0] for a in adjusted_lr1), \
        'Lr not equally adjusted for all param groups for optimizer 1'
    adjusted_lr1 = adjusted_lr1[0]

    assert all(a == adjusted_lr2[0] for a in adjusted_lr2), \
        'Lr not equally adjusted for all param groups for optimizer 2'
    adjusted_lr2 = adjusted_lr2[0]

    assert init_lr * 0.1 == adjusted_lr1 and init_lr * 0.1 == adjusted_lr2, \
        'Lr not adjusted correctly, expected %f but got %f' % (init_lr * 0.1, adjusted_lr1)


def test_multi_optimizer_with_scheduling_stepping(tmpdir):
    tutils.reset_seed()

    class CurrentTestModel(
            LightTestOptimizersWithMixedSchedulingMixin,
            LightTrainDataloader,
            TestModelBase):
        pass

    hparams = tutils.get_default_hparams()
    model = CurrentTestModel(hparams)

    # logger file to get meta
    trainer_options = dict(
        default_save_path=tmpdir,
        max_epochs=1,
        val_percent_check=0.1,
        train_percent_check=0.2
    )

    # fit model
    trainer = Trainer(**trainer_options)
    results = trainer.fit(model)

    init_lr = hparams.learning_rate
    adjusted_lr1 = [pg['lr'] for pg in trainer.optimizers[0].param_groups]
    adjusted_lr2 = [pg['lr'] for pg in trainer.optimizers[1].param_groups]

    assert len(trainer.lr_schedulers) == 2, \
        'all lr scheduler not initialized properly'

    assert all(a == adjusted_lr1[0] for a in adjusted_lr1), \
        'lr not equally adjusted for all param groups for optimizer 1'
    adjusted_lr1 = adjusted_lr1[0]

    assert all(a == adjusted_lr2[0] for a in adjusted_lr2), \
        'lr not equally adjusted for all param groups for optimizer 2'
    adjusted_lr2 = adjusted_lr2[0]

    # Called ones after end of epoch
    assert init_lr * 0.1 ** 0 == adjusted_lr1, \
        'lr for optimizer 1 not adjusted correctly'
    # Called every 3 steps, meaning for 1 epoch of 11 batches, it is called 3 times
    assert init_lr * 0.1 == adjusted_lr2, \
        'lr for optimizer 2 not adjusted correctly'


def test_reduce_lr_on_plateau_scheduling(tmpdir):
    tutils.reset_seed()

    class CurrentTestModel(
            LightTestReduceLROnPlateauMixin,
            LightTrainDataloader,
            LightValidationMixin,
            LightValidationStepMixin,
            TestModelBase):
        pass

    hparams = tutils.get_default_hparams()
    model = CurrentTestModel(hparams)

    # logger file to get meta
    trainer_options = dict(
        default_save_path=tmpdir,
        max_epochs=1,
        val_percent_check=0.1,
        train_percent_check=0.2
    )

    # fit model
    trainer = Trainer(**trainer_options)
    results = trainer.fit(model)

    assert trainer.lr_schedulers[0] == \
        dict(scheduler=trainer.lr_schedulers[0]['scheduler'], monitor='val_loss',
             interval='epoch', frequency=1, reduce_on_plateau=True), \
        'lr schduler was not correctly converted to dict'


def test_optimizer_return_options():
    tutils.reset_seed()

    trainer = Trainer()
    model, hparams = tutils.get_default_model()

    # single optimizer
    opt_a = torch.optim.Adam(model.parameters(), lr=0.002)
    opt_b = torch.optim.SGD(model.parameters(), lr=0.002)
    scheduler_a = torch.optim.lr_scheduler.StepLR(opt_a, 10)
    scheduler_b = torch.optim.lr_scheduler.StepLR(opt_b, 10)

    # single optimizer
    model.configure_optimizers = lambda: opt_a
    optim, lr_sched, freq = trainer.init_optimizers(model)
    assert len(optim) == 1 and len(lr_sched) == 0 and len(freq) == 0

    # opt tuple
    model.configure_optimizers = lambda: (opt_a, opt_b)
    optim, lr_sched, freq = trainer.init_optimizers(model)
    assert len(optim) == 2 and optim[0] == opt_a and optim[1] == opt_b
    assert len(lr_sched) == 0 and len(freq) == 0

    # opt list
    model.configure_optimizers = lambda: [opt_a, opt_b]
    optim, lr_sched, freq = trainer.init_optimizers(model)
    assert len(optim) == 2 and optim[0] == opt_a and optim[1] == opt_b
    assert len(lr_sched) == 0 and len(freq) == 0

    # opt tuple of 2 lists
    model.configure_optimizers = lambda: ([opt_a], [scheduler_a])
    optim, lr_sched, freq = trainer.init_optimizers(model)
    assert len(optim) == 1 and len(lr_sched) == 1 and len(freq) == 0
    assert optim[0] == opt_a
    assert lr_sched[0] == dict(scheduler=scheduler_a, interval='epoch',
                               frequency=1, reduce_on_plateau=False, monitor='val_loss')

    # opt single dictionary
    model.configure_optimizers = lambda: {"optimizer": opt_a, "lr_scheduler": scheduler_a}
    optim, lr_sched, freq = trainer.init_optimizers(model)
    assert len(optim) == 1 and len(lr_sched) == 1 and len(freq) == 0
    assert optim[0] == opt_a
    assert lr_sched[0] == dict(scheduler=scheduler_a, interval='epoch',
                               frequency=1, reduce_on_plateau=False, monitor='val_loss')

    # opt multiple dictionaries with frequencies
    model.configure_optimizers = lambda: (
        {"optimizer": opt_a, "lr_scheduler": scheduler_a, "frequency": 1},
        {"optimizer": opt_b, "lr_scheduler": scheduler_b, "frequency": 5},
    )
    optim, lr_sched, freq = trainer.init_optimizers(model)
    assert len(optim) == 2 and len(lr_sched) == 2 and len(freq) == 2
    assert optim[0] == opt_a
    assert lr_sched[0] == dict(scheduler=scheduler_a, interval='epoch',
                               frequency=1, reduce_on_plateau=False, monitor='val_loss')
    assert freq == [1, 5]


def test_none_optimizer_warning():
    tutils.reset_seed()

    trainer = Trainer()
    model, hparams = tutils.get_default_model()

    model.configure_optimizers = lambda: None

    with pytest.warns(UserWarning, match='will run with no optimizer'):
        _, __, ___ = trainer.init_optimizers(model)


def test_none_optimizer(tmpdir):
    tutils.reset_seed()

    class CurrentTestModel(
            LightTestNoneOptimizerMixin,
            LightTrainDataloader,
            TestModelBase):
        pass

    hparams = tutils.get_default_hparams()
    model = CurrentTestModel(hparams)

    # logger file to get meta
    trainer_options = dict(
        default_save_path=tmpdir,
        max_epochs=1,
        val_percent_check=0.1,
        train_percent_check=0.2
    )

    # fit model
    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)

    # verify training completed
    assert result == 1
