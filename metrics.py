import numpy as np
import tensorflow as tf
from keras import backend as K


def accuracy(y_pred, y_true):
    correct_prediction = K.equal(K.argmax(y_pred, 1), tf.cast(y_true, tf.int64))
    return K.mean(tf.cast(correct_prediction, tf.float32))


def recall(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    return true_positives / (possible_positives + K.epsilon())


def precision(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    return true_positives / (predicted_positives + K.epsilon())


def f_measure(y_true, y_pred):
    model_precision = precision(y_true, y_pred)
    model_recall = recall(y_true, y_pred)
    return 2 * ((model_precision * model_recall) / (model_precision + model_recall + K.epsilon()))
