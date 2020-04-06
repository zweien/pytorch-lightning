import glob
import logging as log
import os

import pytest
import torch

import tests.base.utils as tutils
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.utilities.exceptions import MisconfigurationException
from tests.base import (
    LightningTestModel,
    LightningTestModelWithoutHyperparametersArg,
    LightningTestModelWithUnusedHyperparametersArg
)


@pytest.mark.skipif(torch.cuda.device_count() < 2, reason="test requires multi-GPU machine")
def test_running_test_pretrained_model_ddp(tmpdir):
    """Verify `test()` on pretrained model."""

    tutils.reset_seed()
    tutils.set_random_master_port()

    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    # exp file to get meta
    logger = tutils.get_default_testtube_logger(tmpdir, False)

    # exp file to get weights
    checkpoint = tutils.init_checkpoint_callback(logger)

    trainer_options = dict(
        progress_bar_refresh_rate=0,
        max_epochs=1,
        train_percent_check=0.4,
        val_percent_check=0.2,
        checkpoint_callback=checkpoint,
        logger=logger,
        gpus=[0, 1],
        distributed_backend='ddp'
    )

    # fit model
    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)

    log.info(os.listdir(tutils.get_data_path(logger, path_dir=tmpdir)))

    # correct result and ok accuracy
    assert result == 1, 'training failed to complete'
    pretrained_model = tutils.load_model(logger,
                                         trainer.checkpoint_callback.dirpath,
                                         module_class=LightningTestModel)

    # run test set
    new_trainer = Trainer(**trainer_options)
    new_trainer.test(pretrained_model)

    dataloaders = model.test_dataloader()
    if not isinstance(dataloaders, list):
        dataloaders = [dataloaders]

    for dataloader in dataloaders:
        tutils.run_prediction(dataloader, pretrained_model)


def test_running_test_pretrained_model(tmpdir):
    """Verify test() on pretrained model."""
    tutils.reset_seed()

    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    # logger file to get meta
    logger = tutils.get_default_testtube_logger(tmpdir, False)

    # logger file to get weights
    checkpoint = tutils.init_checkpoint_callback(logger)

    trainer_options = dict(
        progress_bar_refresh_rate=0,
        max_epochs=4,
        train_percent_check=0.4,
        val_percent_check=0.2,
        checkpoint_callback=checkpoint,
        logger=logger
    )

    # fit model
    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)

    # correct result and ok accuracy
    assert result == 1, 'training failed to complete'
    pretrained_model = tutils.load_model(
        logger, trainer.checkpoint_callback.dirpath, module_class=LightningTestModel
    )

    new_trainer = Trainer(**trainer_options)
    new_trainer.test(pretrained_model)

    # test we have good test accuracy
    tutils.assert_ok_model_acc(new_trainer)


def test_load_model_from_checkpoint(tmpdir):
    """Verify test() on pretrained model."""
    tutils.reset_seed()

    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    trainer_options = dict(
        progress_bar_refresh_rate=0,
        max_epochs=2,
        train_percent_check=0.4,
        val_percent_check=0.2,
        checkpoint_callback=ModelCheckpoint(tmpdir, save_top_k=-1),
        logger=False,
        default_save_path=tmpdir,
    )

    # fit model
    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)
    trainer.test()

    # correct result and ok accuracy
    assert result == 1, 'training failed to complete'

    # load last checkpoint
    last_checkpoint = sorted(glob.glob(os.path.join(trainer.checkpoint_callback.dirpath, "*.ckpt")))[-1]
    pretrained_model = LightningTestModel.load_from_checkpoint(last_checkpoint)

    # test that hparams loaded correctly
    for k, v in vars(hparams).items():
        assert getattr(pretrained_model.hparams, k) == v

    # assert weights are the same
    for (old_name, old_p), (new_name, new_p) in zip(model.named_parameters(), pretrained_model.named_parameters()):
        assert torch.all(torch.eq(old_p, new_p)), 'loaded weights are not the same as the saved weights'

    new_trainer = Trainer(**trainer_options)
    new_trainer.test(pretrained_model)

    # test we have good test accuracy
    tutils.assert_ok_model_acc(new_trainer)


@pytest.mark.skipif(torch.cuda.device_count() < 2, reason="test requires multi-GPU machine")
def test_running_test_pretrained_model_dp(tmpdir):
    """Verify test() on pretrained model."""
    tutils.reset_seed()

    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    # logger file to get meta
    logger = tutils.get_default_testtube_logger(tmpdir, False)

    # logger file to get weights
    checkpoint = tutils.init_checkpoint_callback(logger)

    trainer_options = dict(
        max_epochs=2,
        train_percent_check=0.4,
        val_percent_check=0.2,
        checkpoint_callback=checkpoint,
        logger=logger,
        gpus=[0, 1],
        distributed_backend='dp'
    )

    # fit model
    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)

    # correct result and ok accuracy
    assert result == 1, 'training failed to complete'
    pretrained_model = tutils.load_model(logger,
                                         trainer.checkpoint_callback.dirpath,
                                         module_class=LightningTestModel)

    new_trainer = Trainer(**trainer_options)
    new_trainer.test(pretrained_model)

    # test we have good test accuracy
    tutils.assert_ok_model_acc(new_trainer)


@pytest.mark.skipif(torch.cuda.device_count() < 2, reason="test requires multi-GPU machine")
def test_dp_resume(tmpdir):
    """Make sure DP continues training correctly."""

    tutils.reset_seed()

    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    trainer_options = dict(
        max_epochs=1,
        gpus=2,
        distributed_backend='dp',
    )

    # get logger
    logger = tutils.get_default_testtube_logger(tmpdir, debug=False)

    # exp file to get weights
    # logger file to get weights
    checkpoint = tutils.init_checkpoint_callback(logger)

    # add these to the trainer options
    trainer_options['logger'] = logger
    trainer_options['checkpoint_callback'] = checkpoint

    # fit model
    trainer = Trainer(**trainer_options)
    trainer.is_slurm_managing_tasks = True
    result = trainer.fit(model)

    # track epoch before saving. Increment since we finished the current epoch, don't want to rerun
    real_global_epoch = trainer.current_epoch + 1

    # correct result and ok accuracy
    assert result == 1, 'amp + dp model failed to complete'

    # ---------------------------
    # HPC LOAD/SAVE
    # ---------------------------
    # save
    trainer.hpc_save(tmpdir, logger)

    # init new trainer
    new_logger = tutils.get_default_testtube_logger(tmpdir, version=logger.version)
    trainer_options['logger'] = new_logger
    trainer_options['checkpoint_callback'] = ModelCheckpoint(tmpdir)
    trainer_options['train_percent_check'] = 0.5
    trainer_options['val_percent_check'] = 0.2
    trainer_options['max_epochs'] = 1
    new_trainer = Trainer(**trainer_options)

    # set the epoch start hook so we can predict before the model does the full training
    def assert_good_acc():
        assert new_trainer.current_epoch == real_global_epoch and new_trainer.current_epoch > 0

        # if model and state loaded correctly, predictions will be good even though we
        # haven't trained with the new loaded model
        dp_model = new_trainer.model
        dp_model.eval()

        dataloader = trainer.train_dataloader
        tutils.run_prediction(dataloader, dp_model, dp=True)

    # new model
    model = LightningTestModel(hparams)
    model.on_train_start = assert_good_acc

    # fit new model which should load hpc weights
    new_trainer.fit(model)

    # test freeze on gpu
    model.freeze()
    model.unfreeze()


def test_model_saving_loading(tmpdir):
    """Tests use case where trainer saves the model, and user loads it from tags independently."""
    tutils.reset_seed()

    hparams = tutils.get_default_hparams()
    model = LightningTestModel(hparams)

    # logger file to get meta
    logger = tutils.get_default_testtube_logger(tmpdir, False)

    trainer_options = dict(
        max_epochs=1,
        logger=logger,
        checkpoint_callback=ModelCheckpoint(tmpdir)
    )

    # fit model
    trainer = Trainer(**trainer_options)
    result = trainer.fit(model)

    # traning complete
    assert result == 1, 'amp + ddp model failed to complete'

    # make a prediction
    dataloaders = model.test_dataloader()
    if not isinstance(dataloaders, list):
        dataloaders = [dataloaders]

    for dataloader in dataloaders:
        for batch in dataloader:
            break

    x, y = batch
    x = x.view(x.size(0), -1)

    # generate preds before saving model
    model.eval()
    pred_before_saving = model(x)

    # save model
    new_weights_path = os.path.join(tmpdir, 'save_test.ckpt')
    trainer.save_checkpoint(new_weights_path)

    # load new model
    tags_path = tutils.get_data_path(logger, path_dir=tmpdir)
    tags_path = os.path.join(tags_path, 'meta_tags.csv')
    model_2 = LightningTestModel.load_from_checkpoint(
        checkpoint_path=new_weights_path,
        tags_csv=tags_path
    )
    model_2.eval()

    # make prediction
    # assert that both predictions are the same
    new_pred = model_2(x)
    assert torch.all(torch.eq(pred_before_saving, new_pred)).item() == 1


def test_load_model_with_missing_hparams(tmpdir):
    trainer_options = dict(
        progress_bar_refresh_rate=0,
        max_epochs=1,
        checkpoint_callback=ModelCheckpoint(tmpdir, save_top_k=-1),
        logger=False,
        default_save_path=tmpdir,
    )

    # fit model
    trainer = Trainer(**trainer_options)

    model = LightningTestModelWithoutHyperparametersArg()
    trainer.fit(model)
    last_checkpoint = sorted(glob.glob(os.path.join(trainer.checkpoint_callback.dirpath, "*.ckpt")))[-1]

    # try to load a checkpoint that has hparams but model is missing hparams arg
    with pytest.raises(MisconfigurationException, match=r".*__init__ is missing the argument 'hparams'.*"):
        LightningTestModelWithoutHyperparametersArg.load_from_checkpoint(last_checkpoint)

    # create a checkpoint without hyperparameters
    # if the model does not take a hparams argument, it should not throw an error
    ckpt = torch.load(last_checkpoint)
    del(ckpt['hparams'])
    torch.save(ckpt, last_checkpoint)
    LightningTestModelWithoutHyperparametersArg.load_from_checkpoint(last_checkpoint)

    # load checkpoint without hparams again
    # warn if user's model has hparams argument
    with pytest.warns(UserWarning, match=r".*Will pass in an empty Namespace instead."):
        LightningTestModelWithUnusedHyperparametersArg.load_from_checkpoint(last_checkpoint)


# if __name__ == '__main__':
#     pytest.main([__file__])
