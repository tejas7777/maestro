import numpy as np

class EnsembleKalmanFilter():
    def __init__(self, ensemble_size, initial_state, process_noise_cov):
        self.ensemble_size = ensemble_size
        self.ensemble = np.array([initial_state + np.random.normal(0, 1) for _ in range(ensemble_size)])
        self.process_noise_cov = process_noise_cov

    def simulate_request_rate_dynamics(self, last_request_rate):
        if last_request_rate <= 0:
            #print(f"Warning: Non-positive rate detected ({last_request_rate}). Using a small positive value instead.")
            last_request_rate = 0.1

        predicted_requests = np.random.poisson(last_request_rate)
        return predicted_requests

    def predict(self):
        for i in range(self.ensemble_size):
            self.ensemble[i] = self.simulate_request_rate_dynamics(self.ensemble[i]) + np.random.normal(0, self.process_noise_cov)

    def update(self, observation):
        H = np.array([1])
        R = np.array([0.1])
        for i in range(self.ensemble_size):
            P = np.var(self.ensemble) + R
            K = P * H / (H * P * H + R)
            self.ensemble[i] += K * (observation - H * self.ensemble[i])

    def get_mean_prediction(self):
        return np.mean(self.ensemble)
