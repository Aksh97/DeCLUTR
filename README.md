![build](https://github.com/JohnGiorgi/declutr/workflows/build/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/JohnGiorgi/DeCLUTR/branch/master/graph/badge.svg)](https://codecov.io/gh/JohnGiorgi/DeCLUTR)

# DeCLUTR: Deep Contrastive Learning for Unsupervised Textual Representations

The corresponding code for our paper: [DeCLUTR: Deep Contrastive Learning for Unsupervised Textual Representations](https://arxiv.org/abs/2006.03659). Results on [SentEval](https://github.com/facebookresearch/SentEval) are presented below (as averaged scores on the downstream and probing task test sets), along with existing state-of-the-art methods.

| Model                                                                                                      | Requires labelled data? | Parameters | Embed. dim. | Downstream |  Probing  |    Avg.   |   Δ   |
|------------------------------------------------------------------------------------------------------------|:-----------------------:|:----------:|:-----------:|:----------:|:---------:|:---------:|:-----:|
| [InferSent V2](https://github.com/facebookresearch/InferSent)                                              |           Yes           |     38M    |     4096    |    76.46   |   72.58   |   75.07   | -1.55 |
| [Universal Sentence Encoder](https://tfhub.dev/google/universal-sentence-encoder-large/5)                  |           Yes           |    147M    |     512     |  79.13 |   66.70   |   74.69   | -1.94 |
| [Sentence Transformers](https://github.com/UKPLab/sentence-transformers)  ("roberta-base-nli-mean-tokens") |           Yes           |    125M    |     768     |    77.59   |   63.22   |   72.46   | -4.17 |
| Transformer-small ([DistilRoBERTa-base](https://huggingface.co/distilroberta-base))                        |            No           |     82M    |     768     |    72.69   | 74.27 |   73.25   | -3.38 |
| Transformer-base ([RoBERTa-base](https://huggingface.co/roberta-base))                                     |            No           |    125M    |     768     |    72.22   |   73.38   |   72.63   | -4.00 |
| DeCLUTR-small ([DistilRoBERTa-base](https://huggingface.co/distilroberta-base))                            |            No           |     82M    |     768     |    77.52   |   73.90   |   76.23   | -0.40 |
| DeCLUTR-base ([RoBERTa-base](https://huggingface.co/roberta-base))                                         |            No           |    125M    |     768     |    78.15   |   73.89   | __76.63__ |   --  |

> Transformer-* is the same underlying architecture and pretrained weights as DeCLUTR-* _before_ continued training with our contrastive objective. Transformer-* and DeCLUTR-* use mean pooling on their token-level embeddings to produce a fixed-length sentence representation.

## Table of contents

- [Notebooks](#notebooks)
- [Installation](#installation)
- [Usage](#usage)
  - [Training](#training)
  - [Embedding](#embedding)
  - [Evaluating with SentEval](#evaluating-with-senteval)
- [Citing](#citing)

## Notebooks

The easiest way to get started is to follow along with one of our [notebooks](notebooks):

- Training your own model [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JohnGiorgi/DeCLUTR/blob/master/notebooks/training.ipynb)
- Embedding text with a pretrained model [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JohnGiorgi/DeCLUTR/blob/master/notebooks/embedding.ipynb)

## Installation

This repository requires Python 3.6.1 or later.

### Setting up a virtual environment

Before installing, you should create and activate a Python virtual environment. See [here](https://github.com/allenai/allennlp#installing-via-pip) for detailed instructions.

### Installing the library and dependencies

First, clone the repository locally

```bash
git clone https://github.com/JohnGiorgi/DeCLUTR.git
```

Then, install

```bash
cd DeCLUTR
pip install --editable .
```

#### Gotchas

- For the time being, please install [AllenNLP](https://github.com/allenai/allennlp) [from source](https://github.com/allenai/allennlp#installing-from-source).
- If you plan on training your own model, you should also install [PyTorch](https://pytorch.org/) with [CUDA](https://developer.nvidia.com/cuda-zone) support by following the instructions for your system [here](https://pytorch.org/get-started/locally/).

## Usage

### Preparing a dataset

A dataset is simply a file containing one item of text (a document, a scientific paper, etc.) per line. For demonstration purposes, we have provided a script that will download the [WikiText-103](https://www.salesforce.com/products/einstein/ai-research/the-wikitext-dependency-language-modeling-dataset/) dataset and match our minimal preprocessing

```bash
python scripts/preprocess_wikitext_103.py path/to/output/wikitext-103/train.txt --min-length 2048
```

> See [scripts/preprocess_openwebtext.py](scripts/preprocess_openwebtext.py) for a script that can be used to recreate the (much larger) dataset used in our paper.

You can specify the train set path in the [configs](configs) under `"train_data_path"`.

#### Gotchas

- A training dataset should contain documents with a minimum of `num_anchors * max_span_len * 2` whitespace tokens. This is required to sample spans according to our sampling procedure. See the [dataset reader](declutr/dataset_reader.py) and/or [our paper]((https://arxiv.org/abs/2006.03659)) for more details on these hyperparameters.

### Training

To train the model, use the [`allennlp train`](https://docs.allennlp.org/master/api/commands/train/) command with our [`declutr.jsonnet`](configs/declutr.jsonnet) config. For example, to train DeCLUTR-small, run the following

```bash
# This can be (almost) any model from https://huggingface.co/ that supports masked language modelling.
TRANSFORMER_MODEL="distilroberta-base"

allennlp train "configs/declutr.jsonnet" \
    --serialization-dir "output" \
    --overrides "{'train_data_path': 'path/to/your/dataset/train.txt'}" \
    --include-package "declutr"
```

The `--overrides` flag allows you to override any field in the config with a JSON-formatted string, but you can equivalently update the config itself if you prefer. During training, models, vocabulary, configuration, and log files will be saved to the directory provided by `--serialization-dir`. This can be changed to any directory you like. 

#### Gotchas

By default, `allennlp train` will create a vocabulary from our dataset (which can be slow depending on dataset size). Because our model comes with a pretrained vocabulary, we can skip this step by creating a new `"vocabulary"` directory which contains a single file `"non_padded_namespaces.txt"`

```bash
mkdir -p "path/to/your/dataset/vocabulary"
echo "*tags\n*labels" > "path/to/your/dataset/vocabulary/non_padded_namespaces.txt"
```

and then specify this vocabulary in the call to `allennlp train`

```bash
--overrides "{'vocabulary': {'type': 'from_files', 'directory': 'path/to/your/dataset/vocabulary'}}"
```

#### Multi-GPU training

To train on more than one GPU, provide a list of CUDA devices in your call to `allennlp train`. For example, to train with four CUDA devices with IDs `0, 1, 2, 3`

```bash
--overrides "{'distributed.cuda_devices': [0, 1, 2, 3]}"
```

#### Training with mixed-precision

If you want to train with [mixed-precision](https://devblogs.nvidia.com/mixed-precision-training-deep-neural-networks/) (strongly recommended if your GPU supports it), you will need to [install Apex with CUDA and C++ extensions](https://github.com/NVIDIA/apex#quick-start). Once installed, you need only to set `"opt_level"` to `"O1"` in your training [config](configs), or, equivalently, pass the following flag to `allennlp train`

```bash
--overrides "{'trainer.opt_level': 'O1'}"
```

#### Gotchas

- Mixed-precision training will cause an error with the [PyTorch Metric Learning](https://github.com/KevinMusgrave/pytorch-metric-learning) library. See [here](https://github.com/JohnGiorgi/DeCLUTR/issues/60) for a discussion on the issue, along with the suggested fix.

### Embedding

You can embed text with a trained model in one of three ways:

1. [As a library](#as-a-library): import and initialize an object from this repo, which can be used to embed sentences/paragraphs.
2. [🤗 Transformers](#🤗-transformers): load our pretrained model with the [🤗 Transformers library](https://github.com/huggingface/transformers).
3. [Bulk embed](#bulk-embed-a-file): embed all text in a given text file with a simple command-line interface.

#### As a library

To use the model as a library, import `Encoder` and pass it some text (it accepts both strings and lists of strings)

```python
from declutr import Encoder

# This can be a path on disk to a model you have trained yourself OR
# the name of one of our pretrained models.
pretrained_model_or_path = "declutr-small"

encoder = Encoder(pretrained_model_or_path)
embeddings = encoder([
    "A smiling costumed woman is holding an umbrella.",
    "A happy woman in a fairy costume holds an umbrella."
])
```

these embeddings can then be used, for example, to compute the semantic similarity between some number of sentences or paragraphs

```python
from scipy.spatial.distance import cosine

semantic_sim = 1 - cosine(embeddings[0], embeddings[1])
```

See the list of available `PRETRAINED_MODELS` in [declutr/encoder.py](declutr/encoder.py)

```bash
python -c "from declutr.encoder import PRETRAINED_MODELS ; print(list(PRETRAINED_MODELS.keys()))"
```

#### 🤗 Transformers

Our pretrained models are also hosted with 🤗 Transformers, so they can be used like any other model in that library. Here is a simple example:

```python
import torch
from scipy.spatial.distance import cosine

from transformers import AutoModel, AutoTokenizer

# Load the model
tokenizer = AutoTokenizer.from_pretrained("johngiorgi/declutr-small")
model = AutoModel.from_pretrained("johngiorgi/declutr-small")

# Prepare some text to embed
text = [
    "A smiling costumed woman is holding an umbrella.",
    "A happy woman in a fairy costume holds an umbrella.",
]
inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

# Embed the text
with torch.no_grad():
    sequence_output, _ = model(**inputs, output_hidden_states=False)

# Mean pool the token-level embeddings to get sentence-level embeddings
embeddings = torch.sum(
    sequence_output * inputs["attention_mask"].unsqueeze(-1), dim=1
) / torch.clamp(torch.sum(inputs["attention_mask"], dim=1, keepdims=True), min=1e-9)

# Compute a semantic similarity via the cosine distance
semantic_sim = 1 - cosine(embeddings[0], embeddings[1])
```

Currently available models:

- [johngiorgi/declutr-small](https://huggingface.co/johngiorgi/declutr-small)
- johngiorgi/declutr-base (:soon:)

#### Bulk embed a file

To embed all text in a given file with a trained model, run the following command

```bash
allennlp predict "output" "path/to/input.txt" \
 --output-file "output/embeddings.jsonl" \
 --batch-size 32 \
 --cuda-device 0 \
 --use-dataset-reader \
 --overrides "{'dataset_reader.num_anchors': null}" \
 --include-package "declutr"
```

This will:

1. Load the model serialized to `"output"` with the "best" weights (i.e. the ones that achieved the lowest loss during training).
2. Use that model to embed the text in the provided input file (`"path/to/input.txt"`).
3. Save the embeddings to disk as a [JSON lines](http://jsonlines.org/) file (`"output/embeddings.jsonl"`)

The text embeddings are stored in the field `"embeddings"` in `"output/embeddings.jsonl"`.

### Evaluating with SentEval

[SentEval](https://github.com/facebookresearch/SentEval) is a library for evaluating the quality of sentence embeddings. We provide a script to evaluate our model against SentEval.

First, clone the SentEval repository and download the transfer task datasets (you only need to do this once)

```bash
git clone https://github.com/facebookresearch/SentEval.git
cd SentEval/data/downstream/
./get_transfer_data.bash
cd ../../../
```

> See the [SentEval](https://github.com/facebookresearch/SentEval) repository for full details.

Then you can run our [script](scripts/run_senteval.py) to evaluate a trained model against SentEval

```bash
python scripts/run_senteval.py allennlp "SentEval" "output"
 --output-filepath "output/senteval_results.json" \
 --cuda-device 0  \
 --include-package "declutr"
```

The results will be saved to `"output/senteval_results.json"`. This can be changed to any path you like.

> Pass the flag `--prototyping-config` to get a proxy of the results while dramatically reducing computation time.

For a list of commands, run

```bash
python scripts/run_senteval.py --help
```

For help with a specific command, e.g. `allennlp`, run

```
python scripts/run_senteval.py allennlp --help
```

#### Gotchas

- Evaluating the `"SNLI"` task of SentEval will fail without [this fix](https://github.com/facebookresearch/SentEval/pull/52).

## Citing

If you use DeCLUTR in your work, please consider citing our preprint

```
@article{Giorgi2020DeCLUTRDC,
  title={DeCLUTR: Deep Contrastive Learning for Unsupervised Textual Representations},
  author={John M Giorgi and Osvald Nitski and Gary D. Bader and Bo Wang},
  journal={ArXiv},
  year={2020},
  volume={abs/2006.03659}
}
```
