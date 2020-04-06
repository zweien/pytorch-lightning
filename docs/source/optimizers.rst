Optimization
===============

Learning rate scheduling
-------------------------------------
Every optimizer you use can be paired with any `LearningRateScheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_.

.. code-block:: python

   # no LR scheduler
   def configure_optimizers(self):
      return Adam(...)

   # Adam + LR scheduler
   def configure_optimizers(self):
      return [Adam(...)], [ReduceLROnPlateau()]

   # Two optimziers each with a scheduler
   def configure_optimizers(self):
      return [Adam(...), SGD(...)], [ReduceLROnPlateau(), LambdaLR()]

   # Same as above with additional params passed to the first scheduler
   def configure_optimizers(self):
      optimizers = [Adam(...), SGD(...)]
      schedulers = [
         {
            'scheduler': ReduceLROnPlateau(mode='max', patience=7),
            'monitor': 'val_recall', # Default: val_loss
            'interval': 'epoch',
            'frequency': 1
         },
         LambdaLR()
      ]
      return optimizers, schedulers


Use multiple optimizers (like GANs)
-------------------------------------
To use multiple optimizers return > 1 optimizers from :meth:`pytorch_lightning.core.LightningModule.configure_optimizers`

.. code-block:: python

   # one optimizer
   def configure_optimizers(self):
      return Adam(...)

   # two optimizers, no schedulers
   def configure_optimizers(self):
      return Adam(...), SGD(...)

   # Two optimizers, one scheduler for adam only
   def configure_optimizers(self):
      return [Adam(...), SGD(...)], [ReduceLROnPlateau()]

Lightning will call each optimizer sequentially:

.. code-block:: python

   for epoch in epochs:
      for batch in data:
         for opt in optimizers:
            train_step(opt)
            opt.step()

      for scheduler in scheduler:
         scheduler.step()


Step optimizers at arbitrary intervals
----------------------------------------
To do more interesting things with your optimizers such as learning rate warm-up or odd scheduling,
override the :meth:`optimizer_step` function.

For example, here step optimizer A every 2 batches and optimizer B every 4 batches

.. code-block:: python

    def optimizer_step(self, current_epoch, batch_nb, optimizer, optimizer_i, second_order_closure=None):
        optimizer.step()
        optimizer.zero_grad()

    # Alternating schedule for optimizer steps (ie: GANs)
    def optimizer_step(self, current_epoch, batch_nb, optimizer, optimizer_i, second_order_closure=None):
        # update generator opt every 2 steps
        if optimizer_i == 0:
            if batch_nb % 2 == 0 :
                optimizer.step()
                optimizer.zero_grad()

        # update discriminator opt every 4 steps
        if optimizer_i == 1:
            if batch_nb % 4 == 0 :
                optimizer.step()
                optimizer.zero_grad()

        # ...
        # add as many optimizers as you want

Here we add a learning-rate warm up

.. code-block:: python

    # learning rate warm-up
    def optimizer_step(self, current_epoch, batch_nb, optimizer, optimizer_i, second_order_closure=None):
        # warm up lr
        if self.trainer.global_step < 500:
            lr_scale = min(1., float(self.trainer.global_step + 1) / 500.)
            for pg in optimizer.param_groups:
                pg['lr'] = lr_scale * self.hparams.learning_rate

        # update params
        optimizer.step()
        optimizer.zero_grad()
