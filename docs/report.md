# AutoMaths

## Context

### HoTT
[Free online HoTT book](https://hott.github.io/book/nightly/hott-online-1075-g3c53219.pdf)
### Limits

## Architecture

### Data preprocessing

Data sources :
- [HoTT source code](https://github.com/HoTT/HoTT)
- [UniMath repository](https://github.com/UniMath/UniMath)


1. Download data from the Git repositories
2. Iterate over the files in repositories to parse the file name and
the package the file (and therefore it's constructs) are located in.
3. Use the `pygments` lexer to turn source code into raw token stream
4. Store that token stream to filesystem, keeping only metadatas
5. Resolve dependencies for each [`Lemma`/`Definition`/`Theorem`]
6. Package each one into a separated self-contained csv file

Metadatas:
- File name
- File package
- File definitions
- File dependencies
- Definitions dependencies

#### Exemple
Raw input:
```
Definition equiv_ind_comp `{IsEquiv A B f} (P : B -> Type)
  (df : forall x:A, P (f x)) (x : A)
  : equiv_ind f P df (f x) = df x.
Proof.
  unfold equiv_ind.
  rewrite eisadj.
  rewrite <- transport_compose.
  exact (apD df (eissect f x)).
Defined.
```

Token stream exemple (Proof only here):
```
Keyword.Namespace 'Proof'
Operator '.'
Keyword 'unfold'
Name 'equiv_ind'
Operator '.'
Keyword 'rewrite'
Name 'eisadj'
Operator '.'
Keyword 'rewrite'
Operator '<-'
Name 'transport_compose'
Operator '.'
Keyword.Pseudo 'exact'
Operator '('
Name 'apD'
Name 'df'
Operator '('
Name 'eissect'
Name 'f'
Name 'x'
Operator ')'
Operator ')'
Operator '.'
Keyword.Namespace 'Defined'
```


### Neural network
#### DNC framework
- [Implementation](https://github.com/deepmind/dnc)
- [Paper](https://www.nature.com/articles/nature20101.epdf?author_access_token=ImTXBI8aWbYxYQ51Plys8NRgN0jAjWel9jnR3ZoTv0MggmpDmwljGswxVdeocYSurJ3hxupzWuRNeGvvXnoO8o4jTJcnAyhGuZzXJ1GEaD-Z7E6X_a9R-xqJ9TfJWBqz)
- [Blog post](https://deepmind.com/blog/differentiable-neural-computers/)

## Training

## Issues

- The token stream and raw text shouldn't be handled by different networks.
This could be solved by training the network with different kind of input datas,
as deepmind did on the DNC paper. Or we could encode the token type into the
neural network input along with the raw stream.

- The network should learn categorical data instead of an unstructured character
stream. We need to find a way to turn text data into categorical representations.
We could use one-hot encoding to do so, by encoding differently free text (such
  as naming) and language operators to avoid confusion.

- There is no Coq parser avaliable in Python, therefore, the dependencies parsing
will be done using regex, which is weaker than a generated `Yacc` parser. However
as Coq was developped on the top of ML language, there is no centralised BNF grammar
avaliable.
