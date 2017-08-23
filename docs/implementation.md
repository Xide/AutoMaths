# Implementation

This section discuss some of the machine learning models and methods envisaged to
predict the proofs content from the definition.


## Training

I guess than since the quantity of datas is small, the best chance for a model
to predict proofs content is to use reinforcment learning and check the model
correctness using Coq directly.
This process enable the algorithm to solve training problems in any possible way, and not only
by outputing the exact same proof as the original one.

However, since the number of trial is expected to be very high, especially
at the beginning, we could use the original proof to guide learning :
The closest the model is from the original proof, the higher is the reward.
By lowering the original proof influence over time, we could achieve both
a faster bootstrap of the model and reinforcment learning freedom.

Moreover, train/test dataset split are more complex than a `sklearn.train_test_split`,
because the dataset is highly structured, we can't just take one random part as the test case.
We first need to retreive the different proofs in the dataset
(a python function has been developed in `srcs/utils/proofs.py` to iterate over them),
then we need to structurate the proofs to avoid using a testing proof at training step because it was
implicitly included in a dependency. We therefore need to ensure that proofs in the testing/validation dataset
cannot be included anywhere in the training set.

Lastly, the model will need ordering on the input datas:

1. Learn the axioms
2. Learn the context (e.g: proofs included in dependencies)
3. The definiton to be solved

## Models

The common point of those models is that they all are recurrent, this
is because the nature of the input and output are inherently sequential.


### Imagination Augmented Agents

This architecture, published by Deepmind, will in my opinion be the best fit for this problem.
The capacity of the agent to plan for the long term reward can, according to the result published in their
paper, divide the number of simulation steps required to solve a sokoban level by 25 (in comparison with optimized Monte Carlo Tree Search)

- Implementation - None at the moment.
- [Paper](https://arxiv.org/abs/1707.06203)
- [Deepmind blog post](https://deepmind.com/blog/agents-imagine-and-plan/)

### DNC framework
- [Implementation](https://github.com/deepmind/dnc)
- [Paper](https://www.nature.com/articles/nature20101.epdf?author_access_token=ImTXBI8aWbYxYQ51Plys8NRgN0jAjWel9jnR3ZoTv0MggmpDmwljGswxVdeocYSurJ3hxupzWuRNeGvvXnoO8o4jTJcnAyhGuZzXJ1GEaD-Z7E6X_a9R-xqJ9TfJWBqz)
- [Deepmind blog post](https://deepmind.com/blog/differentiable-neural-computers/)



# Limits

## Technical issues

- As i wasn't able to find a Coq parser in python, the parsing features had to
  be rewriten from scratch in python, this has two drawbacks:
      1. It is weaker than a parser, some issues with the lexing and the context
        require a lot of code to solve, and is more sensitive to bugs.
      2. As it is all written in Python, it take more time to process the data.
        This drawback is much less impacting than the first one, as the amount
         of avaliable Coq files is relatively ysmall and need to be processed
         only once.

 - The model could make use of categorical data instead of an unstructured character
 stream. We need to find a way to turn text data into categorical representations.
 We could use one-hot encoding to do so, by encoding differently free text (such
   as naming) and language operators to avoid confusion.

- A reinforcment learning model would have to have it's output tested against coq to
ensure the proof correctness, however this is an expensive process, it can easily
become the learning process bottleneck.

## Learning issues

- The token stream and raw text shouldn't be handled by different models.
This could be solved by training them with different kind of input datas,
as deepmind did on their DNC paper. Or we could encode the token type into the
model input along with the raw stream.

- The required number of simulations for reinforcment learning is high and the
simulations are costly.
