from typing import get_type_hints
import numpy as np
import math
import copy
from scratch_ml.utils import activation_functions
from scratch_ml.utils import Sigmoid, ReLU, LeakyReLU, Softmax, TanH


class Layer():
    """Base Layer class."""

    def set_input_shape(self, shape):
        """Sets the shape that the layer expects of the input."""
        self.input_shape = shape

    def output_shape(self):
        """The shape of the output produced by forward_pass."""
        return NotImplementedError()

    def layer_name(self):
        """The name of the layer"""
        return self.__class__.__name__

    def parameters(self):
        """The number of trainable parameters  parameters(used by the layer."""
        return 0

    def forward_pass(self, x, training):
        """Propogates the data forward in the network."""
        return NotImplementedError()

    def backward_pass(self, gradient):
        """ Propogates the gradient backwards in the network."""
        return NotImplementedError()


class Dense(Layer):

    def __init__(self, n_units, input_shape=None):
        """A fully-connected NN layer."""
        self.layer_input = None
        self.input_shape = input_shape
        self.n_units = n_units
        self.trainable = True
        self.w = None
        self.w0 = None

    def initialize(self, optimizer):
        # Initialize weights
        limit = 1 / math.sqrt(self.input_shape[0])
        self.w = np.random.uniform(-limit, limit,
                                   (self.input_shape[0], self.n_units))
        self.w0 = np.zeros((1, self.n_units))
        # Weight optimizers
        self.w_opt = copy.copy(optimizer)
        self.w0_opt = copy.copy(optimizer)

    def parameters(self):
        return np.prod(self.w.shape) + np.prod(self.w0.shape)

    def forward_pass(self, x, training):
        self.layer_input = x
        return x.dot(self.w) + self.w0

    def backward_pass(self, gradient):
        w = self.w
        if self.trainable:
            grad_w = self.layer_input.T.dot(gradient)
            grad_w0 = np.sum(gradient, axis=0, keepdims=True)
            self.w = self.w0_opt.update(self.w, grad_w)
            self.w0 = self.w_opt.update(self.w0, grad_w0)
        # Return accumulated gradient for next layer
        return gradient.dot(w.T)

    def output_shape(self):
        return (self.n_units, )


activation_functions = {
    'relu': ReLU,
    'sigmoid': Sigmoid,
    'softmax': Softmax,
    'leaky_relu': LeakyReLU,
    'tanh': TanH,
}


class Activation(Layer):
    """A layer that applies an activation operation to the input."""

    def __init__(self, name):
        self.activation_func = activation_functions[name]()
        self.trainable = True

    def layer_name(self):
        return "Activation %s" % (self.activation_func.__class__.__name__)

    def forward_pass(self, x, training):
        self.layer_input = x
        return self.activation_func(x)

    def backward_pass(self, gradient):
        return gradient * self.activation_func.gradient(self.layer_input)

    def output_shape(self):
        return self.input_shape