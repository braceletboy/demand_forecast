#!/usr/bin/python 3.6
# -*-coding:utf-8-*-

'''
Utility functions
'''
import torch
import numpy as np
import os


def get_data_path():
    folder = os.path.dirname(__file__)
    return os.path.join(folder, "data")


def RSE(ypred, ytrue):
    rse = np.sqrt(np.square(ypred - ytrue).sum()) / \
        np.sqrt(np.square(ytrue - ytrue.mean()).sum())
    return rse


def quantile_loss(ytrue, ypred, qs):
    '''
    Quantile loss version 2
    Args:
    ytrue (batch_size, output_horizon)
    ypred (batch_size, output_horizon, num_quantiles)
    '''
    L = np.zeros_like(ytrue)
    for i, q in enumerate(qs):
        yq = ypred[:, :, i]
        diff = yq - ytrue
        L += np.max(q * diff, (q - 1) * diff)
    return L.mean()


def SMAPE(ytrue, ypred):
    ytrue = np.array(ytrue).ravel()
    ypred = np.array(ypred).ravel() + 1e-4
    mean_y = (ytrue + ypred) / 2.
    return np.mean(np.abs((ytrue - ypred)
                          / mean_y))


def MAPE(ytrue, ypred):
    ytrue = np.array(ytrue).ravel() + 1e-4
    ypred = np.array(ypred).ravel()
    return np.mean(np.abs((ytrue - ypred)
                          / ytrue))


def train_test_split(X, y, train_ratio=0.8):
    '''Split the dataset into train, test sets

    Parameters
    ----------
    X
        The input dataset
    y
        The label dataset
    train_ratio
        The ratio in which the dataset will be split into train and test
    '''
    num_periods, num_features = X.shape
    train_periods = int(num_periods * train_ratio)
    Xtr = X[:train_periods, :]
    ytr = y[:train_periods, :]
    Xte = X[train_periods:, :]
    yte = y[train_periods:, :]
    return Xtr, ytr, Xte, yte


class StandardScaler:

    def fit_transform(self, y):
        self.mean = np.mean(y)
        self.std = np.std(y) + 1e-4
        return (y - self.mean) / self.std

    def inverse_transform(self, y):
        return y * self.std + self.mean

    def transform(self, y):
        return (y - self.mean) / self.std


class MaxScaler:

    def fit_transform(self, y):
        self.max = np.max(y)
        return y / self.max

    def inverse_transform(self, y):
        return y * self.max

    def transform(self, y):
        return y / self.max


class MeanScaler:

    def fit_transform(self, y):
        self.mean = np.mean(y)
        return y / self.mean

    def inverse_transform(self, y):
        return y * self.mean

    def transform(self, y):
        return y / self.mean


class LogScaler:

    def fit_transform(self, y):
        return np.log1p(y)

    def inverse_transform(self, y):
        return np.expm1(y)

    def transform(self, y):
        return np.log1p(y)


def gaussian_likelihood_loss(z, mu, sigma):
    '''
    Gaussian Liklihood Loss
    Args:
    z (tensor): true observations, shape (num_ts, num_periods)
    mu (tensor): mean, shape (num_ts, num_periods)
    sigma (tensor): standard deviation, shape (num_ts, num_periods)

    likelihood: 
    (2 pi sigma^2)^(-1/2) exp(-(z - mu)^2 / (2 sigma^2))

    log likelihood:
    -1/2 * (log (2 pi) + 2 * log (sigma)) - (z - mu)^2 / (2 sigma^2)
    '''
    negative_likelihood = torch.log(
        sigma + 1) + (z - mu) ** 2 / (2 * sigma ** 2) + 6
    return negative_likelihood.mean()


def negative_binomial_loss(ytrue, mu, alpha):
    '''
    Negative Binomial Sample
    Args:
    ytrue (array like)
    mu (array like)
    alpha (array like)

    maximuze log l_{nb} = log Gamma(z + 1/alpha) - log Gamma(z + 1) - log Gamma(1 / alpha)
                - 1 / alpha * log (1 + alpha * mu) + z * log (alpha * mu / (1 + alpha * mu))

    minimize loss = - log l_{nb}

    Note: torch.lgamma: log Gamma function
    '''
    batch_size, seq_len = ytrue.size()
    likelihood = torch.lgamma(ytrue + 1. / alpha) - torch.lgamma(ytrue + 1) - torch.lgamma(1. / alpha) \
        - 1. / alpha * torch.log(1 + alpha * mu) \
        + ytrue * torch.log(alpha * mu / (1 + alpha * mu))
    return - likelihood.mean()
