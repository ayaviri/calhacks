import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


np.random.seed(0)  
X = np.random.rand(100).astype(np.float32)
y = 2 * X + 1 + np.random.normal(0, 0.1, 100).astype(np.float32)

plt.scatter(X, y)
plt.xlabel('X')
plt.ylabel('y')
plt.title('Dummy Data')
plt.show()

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(units=1, input_shape=[1])
])

model.compile(optimizer='sgd', loss='mean_squared_error')

history = model.fit(X, y, epochs=100, verbose=0)

plt.plot(history.history['loss'])
plt.xlabel('Epoch')
plt.ylabel('Validation Loss')
plt.title('Training Loss Over Time')
plt.show()

X_test = np.array([0.1, 0.5, 0.9])
y_pred = model.predict(X_test)

for i, x in enumerate(X_test):
    print(f"For x = {x}, predicted y = {y_pred[i][0]:.4f}")

y_true = 2 * X_test + 1
print("Actual y values:", y_true)
 
