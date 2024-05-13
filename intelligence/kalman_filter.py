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
        self.F = F
        self.B = B 
        self.u = u
        self.Q = Q
        self.H = H
        self.R = R 
        self.x = x0 
        self.P = P0 
        self.tuning_period = 60 #Mins
        self.is_tunning_done = False

    def predict(self):
        self.x = np.dot(self.F, self.x) + np.dot(self.B, self.u) if self.B is not None else np.dot(self.F, self.x)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x

    def update(self, z):
        y = z - np.dot(self.H, self.x)
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        self.x = self.x + np.dot(K, y)
        I = np.eye(self.F.shape[1])
        self.P = np.dot(np.dot(I - np.dot(K, self.H), self.P), 
                        (I - np.dot(K, self.H)).T) + np.dot(np.dot(K, self.R), K.T)
        return self.x