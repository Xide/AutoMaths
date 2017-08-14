"""Main package, keep track of the experiments."""

import os
from sacred import Experiment
from sacred.observers import FileStorageObserver


ex = Experiment(
    'AutoMaths'
)

ex.observers.append(FileStorageObserver.create('data/runs'))


ex.add_config(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'model',
        'config.json'
    )
)


@ex.command
def train(_log):
    """Train the neural network."""
    _log.debug('Loading training dataset')
    ex.add_resource(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'train.csv'
        )
    )


@ex.automain
def main(foo):
    """Entry point."""
    pass
