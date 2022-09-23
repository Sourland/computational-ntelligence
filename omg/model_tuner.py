import tensorflow as tf
import keras_tuner as kt
from tensorflow import keras
from keras import optimizers, losses, metrics, datasets
from RBFLayer import RBFLayer
from keras import layers
import numpy as np
from utilities import plot_metrics, calculate_rbf_elements
from sklearn.preprocessing import normalize
from metrics import rho_squared

(x_train, y_train), (x_test, y_test) = datasets.boston_housing.load_data(path="boston_housing.npz", test_split=.25)

validation_split = 0.2
RANDOM_VARIABLE = 42
# Importing Dataset
train_data_size = np.max(x_train.shape)
output_layer_size = 1

x_train = normalize(x_train)
x_test = normalize(x_test)


def build_model(hp):
    model = keras.Sequential()
    rbf_layer_size = hp.Choice('rbf_units', values=[.5, .15, .3, .5])
    hidden_layer_size = hp.Choice('hidden_layer_units', values=[32, 64, 128, 256])
    dropout_rates = hp.Choice('dropout_rate', values=[.2, .35, .5])

    total_clusters = int(np.floor(rbf_layer_size * np.max(x_train.shape)))

    center, betas = calculate_rbf_elements(x_train, total_clusters)

    rbf_layer = RBFLayer(total_clusters, initializer=tf.constant_initializer(center), betas=betas, input_shape=(13,))
    hidden_layer = layers.Dense(hidden_layer_size, )
    dropout_layer = layers.Dropout(rate=dropout_rates)
    output_layer = layers.Dense(output_layer_size, )

    model.add(rbf_layer)
    model.add(hidden_layer)
    model.add(dropout_layer)
    model.add(output_layer)

    model.compile(optimizer=optimizers.SGD(learning_rate=1e-3),
                  loss=losses.MeanSquaredError(),
                  metrics=[metrics.RootMeanSquaredError(), rho_squared]
                  )

    return model


total_epochs = 100

tuner = kt.RandomSearch(
    build_model,
    objective=kt.Objective("root_mean_squared_error", direction="min"),
    directory='keras_tuner_dir',
    project_name='rbf_tuning',
    overwrite=True
)

tuner.search(x_train, y_train,
             epochs=total_epochs,
             validation_split=0.2
             )

optimal_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]
rbf_layer_size = optimal_hyperparameters.get('rbf_units')
hidden_layer_size = optimal_hyperparameters.get('hidden_layer_units')
dropout_rate = optimal_hyperparameters.get('dropout_rate')

total_clusters = int(np.floor(rbf_layer_size * np.max(x_train.shape)))

center, betas = calculate_rbf_elements(x_train, total_clusters)
rbf_layer = RBFLayer(total_clusters, initializer=tf.constant_initializer(center), betas=betas, input_shape=(13,))
hidden_layer = layers.Dense(hidden_layer_size, )
dropout_layer = layers.Dropout(rate=dropout_rate)
output_layer = layers.Dense(output_layer_size, )

model = keras.Sequential()

model.add(rbf_layer)
model.add(hidden_layer)
model.add(dropout_layer)
model.add(output_layer)

model.compile(optimizer=optimizers.SGD(learning_rate=1e-3),
              loss=losses.MeanSquaredError(),
              metrics=[metrics.RootMeanSquaredError(), rho_squared]
              )

history = model.fit(x_train, y_train, epochs=100, batch_size=128, validation_split=validation_split)
plot_metrics(model_history=history, model_name="Tuned RBF network", model_class='rbf')

loss, root_mean_squared_error, rho_square = model.evaluate(x_test, y_test, verbose=0)
print('Test loss: ', loss)
print('Test RMSE: ', root_mean_squared_error)
print('Test coefficient of determination: ', rho_square)
