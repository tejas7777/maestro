import numpy as np


class EnsembleKalmanFilterCompute:
    def __init__(self, ensemble_size, initial_state, process_noise_cov, prediction_steps=2):
        self.ensemble_size = ensemble_size
        self.ensemble = np.array([initial_state + np.random.normal(0, 10) for _ in range(ensemble_size)])
        self.process_noise_cov = process_noise_cov
        self.prediction_steps = prediction_steps

    def simulate_compute_load_dynamics(self, last_compute_load):
        drift = 0.05 * last_compute_load
        predicted_compute_load = max(0, last_compute_load + drift)
        return np.random.poisson(predicted_compute_load)

    def predict(self):
        for _ in range(self.prediction_steps):
            for i in range(self.ensemble_size):
                self.ensemble[i] = self.simulate_compute_load_dynamics(self.ensemble[i]) + np.random.normal(0,
                                                                                                            self.process_noise_cov)

    def update(self, observation):
        """ Update ensemble members based on observation of actual compute load. """
        H = np.array([1])  # Simple observation model
        R = np.array([5])  # Higher observation noise if compute load measurements are noisy
        for i in range(self.ensemble_size):
            P = np.var(self.ensemble) + R
            K = P * H / (H * P * H + R)
            self.ensemble[i] += K * (observation - H * self.ensemble[i])

    def get_mean_prediction(self):
        """ Calculate mean of ensemble to get a single prediction. """
        return np.mean(self.ensemble)

    def get_predictions_for_future(self):
        """ Return predictions directly for all steps predicted. """
        predictions = []
        temp_ensemble = np.copy(self.ensemble)
        for _ in range(self.prediction_steps):
            for i in range(self.ensemble_size):
                temp_ensemble[i] = self.simulate_compute_load_dynamics(temp_ensemble[i]) + np.random.normal(0,
                                                                                                            self.process_noise_cov)
            predictions.append(np.mean(temp_ensemble))
        return predictions
