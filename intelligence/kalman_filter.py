import numpy as np

class KalmanFilter:
    def __init__(self, F=None, B=None, u=None, Q=None, H=None, R=None, x0=None, P0=None, tuning_period=None):
        """
        Initialize the Kalman Filter.
        F: State Transition model
        B: Control-input model
        u: Control vector
        Q: Process Noise Covariance
        H: Observation model
        R: Measurement Noise Covariance
        x0: Initial state estimate
        P0: Initial covariance estimate
        """
        self.F = F  # State transition matrix
        self.B = B  # Control input matrix
        self.u = u  # Control input
        self.Q = Q  # Process noise covariance
        self.H = H  # Observation matrix
        self.R = R  # Measurement noise covariance
        self.x = x0  # Initial state estimate
        self.P = P0  # Initial covariance estimate
        self.tuning_period = 60 #Mins
        self.is_tunning_done = False

    def predict(self):
        """
        Predict the state and state covariance.
        """
        # Predict the state
        self.x = np.dot(self.F, self.x) + np.dot(self.B, self.u) if self.B is not None else np.dot(self.F, self.x)
        # Predict the state covariance
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x

    def update(self, z):
        """
        Update the state by a new measurement z.
        """
        # Measurement residual
        y = z - np.dot(self.H, self.x)
        # Residual covariance
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        # Kalman gain
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        # Update the state estimate.
        self.x = self.x + np.dot(K, y)
        # Update the covariance estimate.
        I = np.eye(self.F.shape[1])  # Identity matrix
        self.P = np.dot(np.dot(I - np.dot(K, self.H), self.P), 
                        (I - np.dot(K, self.H)).T) + np.dot(np.dot(K, self.R), K.T)
        return self.x