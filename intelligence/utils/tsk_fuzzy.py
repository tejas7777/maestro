class TSKFuzzySystem():
    def __init__(self,):
        self.rules = []

    def add_rule(self, antecedent, consequent_params):

        self.rules.append((antecedent, consequent_params))

    def evaluate(self, inputs):

        weighted_outputs = 0
        total_weights = 0
        for antecedent, params in self.rules:
            weight = antecedent(inputs)
            output = sum(p * inputs.get(var, 0) for p, var in zip(params[:-1], inputs.keys())) + params[-1]
            weighted_outputs += weight * output
            total_weights += weight

        if total_weights == 0:
            return 0
        return weighted_outputs / total_weights