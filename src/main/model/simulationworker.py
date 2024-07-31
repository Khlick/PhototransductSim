from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

class SimulationWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)  # Progress signal

    def __init__(self, model, selections):
        super().__init__()
        self.model = model
        self._selections = selections
        self._is_running = True
        self._sort_key = 'stimulusIntensity'

    @property
    def selections(self):
        return self._selections

    @selections.setter
    def selections(self, value):
        if not isinstance(value, dict):
            raise ValueError("Selections must be a dictionary.")
        if 'x' not in value or 'y' not in value:
            raise ValueError("Selections dictionary must contain 'x' and 'y' keys.") 
        self._selections = value

    @property
    def sort_key(self):
        return self._sort_key
    
    @sort_key.setter
    def sort_key(self, key):
        # validate value in model
        if key not in self.model.getValidSortKeys():
            raise ValueError("Invalid Sort Key.")
        self._sort_key = key
    
    @pyqtSlot()
    def run(self):
        try:
            self._is_running = True
            results = []

            # Determine Stimulus Times
            stimulusTimes = [(np.float64(0), d) for d in self.model.stimulusDurations]
            params = self.model.getParameters()['modelParameters']
            
            # Identify parameter sweeps
            sweep_param = {
                k: v for k, v in params.items() if np.ndim(v) > 0 and len(v) > 1
            }
            sweep_key = list(sweep_param.keys())
            nSweepKeys = len(sweep_key)
            nSweep = 0
            if nSweepKeys:
                sweep_key = sweep_key.pop()
                nSweep = len(sweep_param[sweep_key])

            # Run simulations
            total = len(self.model.stimulusIntensities) * max(1, nSweep)
            futures = []

            with ThreadPoolExecutor() as executor:
                # Loop through stimuli
                for intensity, time, activation in zip(self.model.stimulusIntensities, stimulusTimes, self.model.pigmentActivations):
                    # Loop through parameter sweep
                    if nSweep:
                        for i in range(nSweep):
                            param_set = {
                                key: np.copy(value) for key, value in params.items()
                            }  # copy the parameters
                            param_set[sweep_key] = np.asarray(sweep_param[sweep_key][i])
                            label = f"{activation} (R*); {param_set[sweep_key]} ({sweep_key})"
                            futures.append(
                                (
                                    executor.submit(
                                        self.model.simulate_once,
                                        intensity,
                                        time,
                                        activation,
                                        param_set
                                    ),
                                    label
                                )
                            )
                    else:
                        label = f"{activation} (R*)"
                        futures.append(
                            (
                                executor.submit(
                                    self.model.simulate_once,
                                    intensity,
                                    time,
                                    activation,
                                    params
                                ),
                                label
                            )
                        )

                completed = 0
                for future in as_completed([fut for fut, _ in futures]):
                    if not self._is_running:
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise RuntimeError("Simulation was stopped.")
                    label = next(label for fut, label in futures if fut == future)
                    result = future.result()
                    result['label'] = label
                    results.append(result)
                    completed += 1
                    progress = int((completed / total) * 100)
                    self.progress.emit(progress)

            self.model._results = sorted(results, key=lambda x: x[self.sort_key])
            if self._is_running:
                final_results = self.model.getResult(self.selections['x'], self.selections['y'])
                self.result.emit(final_results)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._is_running = False
