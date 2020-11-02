# -*- coding: utf-8 -*-

import unicodedata
import seaborn as sns
import matplotlib.pyplot as plt
from functools import lru_cache


@lru_cache(maxsize=1024)
def ispunct(token):
    return all(unicodedata.category(char).startswith('P')
               for char in token)


@lru_cache(maxsize=1024)
def isfullwidth(token):
    return all(unicodedata.east_asian_width(char) in ['W', 'F', 'A']
               for char in token)


@lru_cache(maxsize=1024)
def islatin(token):
    return all('LATIN' in unicodedata.name(char)
               for char in token)


@lru_cache(maxsize=1024)
def isdigit(token):
    return all('DIGIT' in unicodedata.name(char)
               for char in token)


@lru_cache(maxsize=1024)
def tohalfwidth(token):
    return unicodedata.normalize('NFKC', token)


@lru_cache(maxsize=1024)
def has_number(token):
    has_num = False
    num_set = set(range(10))
    for char in token:
        if char in num_set:
            has_num = True
            break
    return has_num


def stripe(x, n, w, offset=(0, 0), dim=1):
    """
    Returns a diagonal stripe of the tensor.

    Args:
        x (torch.Tensor): the input tensor with 2 or more dims.
        n (int): the length of the stripe.
        w (int): the width of the stripe.
        offset (tuple): the offset of the first two dims.
        dim (int): 0 if returns a horizontal stripe; 1 otherwise.

    Returns:
        a diagonal stripe of the tensor.

    Examples:
        >>> x = torch.arange(25).view(5, 5)
        >>> x
        tensor([[ 0,  1,  2,  3,  4],
                [ 5,  6,  7,  8,  9],
                [10, 11, 12, 13, 14],
                [15, 16, 17, 18, 19],
                [20, 21, 22, 23, 24]])
        >>> stripe(x, 2, 3, (1, 1))
        tensor([[ 6,  7,  8],
                [12, 13, 14]])
        >>> stripe(x, 2, 3, dim=0)
        tensor([[ 0,  5, 10],
                [ 6, 11, 16]])
    """

    x, seq_len = x.contiguous(), x.size(1)
    stride, numel = list(x.stride()), x[0, 0].numel()
    stride[0] = (seq_len + 1) * numel
    stride[1] = (1 if dim == 1 else seq_len) * numel
    return x.as_strided(size=(n, w, *x.shape[2:]),
                        stride=stride,
                        storage_offset=(offset[0]*seq_len+offset[1])*numel)


def pad(tensors, padding_value=0, total_length=None):
    size = [len(tensors)] + [max(tensor.size(i) for tensor in tensors)
                             for i in range(len(tensors[0].size()))]
    if total_length is not None:
        assert total_length >= size[1]
        size[1] = total_length
    out_tensor = tensors[0].data.new(*size).fill_(padding_value)
    for i, tensor in enumerate(tensors):
        out_tensor[i][[slice(0, i) for i in tensor.size()]] = tensor
    return out_tensor


def heatmap(corr, labels=None, name='matrix'):
    sns.set(style="white")

    shape = corr.t().shape
    assert len(shape) == 2
    shape = (shape[0] * 2, shape[1])

    # Set up the matplotlib figure
    f, ax = plt.subplots(ncols=2, figsize=shape)

    cmap = "RdBu"

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr / (corr.sum(0)[None, :] + 1e-6), cmap=cmap, center=0, ax=ax[0],
                square=True, linewidths=.5,
                xticklabels=False if labels is None else labels, yticklabels=False,
                cbar=False)
    sns.heatmap(corr / (corr.sum(1)[: ,None] + 1e-6), cmap=cmap, center=0, ax=ax[1],
                square=True, linewidths=.5,
                xticklabels=False if labels is None else labels, yticklabels=False,
                cbar=False)
    plt.savefig(f'{name}.png')
    plt.close()