import numpy as np
from scipy.integrate import solve_ivp
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

class SimulationError(Exception):
    """Exception raised for errors in the simulation."""
    pass

class SimulationWarning(Warning):
    """Warning raised for issues in the simulation that do not stop execution."""
    pass

class Phototransduction:
    
    MAX_SOLVE_ATTEMPTS = 20
    
    def __init__(self, dt=0.001, responseDuration=1.5, stimulusOffset=0.1, darkCurrent=15):
        self._dt = dt
        self.stimulusOffset = stimulusOffset
        self._responseDuration = responseDuration
        self._fs = 1 / dt
        self._maxStep = np.inf
        
        self.param = {
            'betaDark': 4.1,         # s^-1
            'concCaDark': 0.3,       # µM
            'concCgDark': 4,         # µM
            'fChCa': 0.12,           
            'colArea': 0.28,         # µm²/photon
            'betaSub': 0.021,        
            'xi':  0.45 / 2.5,              
            'muRa': 28,              # s^-1
            'muTa': 23,            # s^-1
            'muPa': 5,               # s^-1
            'nAlpha': 2,             
            'KAlpha': 0.14,          # µM
            'rAlpha': 0.033,         
            'nCh': 2.5,              
            'KCh': 20,               # µM
            'KEx': 1.6,              # µM
            'muCa': 50,
            'iDark': darkCurrent     # pA
        }

        self._stimulusIntensities = np.array([1]) / self.param['colArea'] / 0.01
        self._stimulusDurations = np.array([0.01])
        self._pigmentActivations = np.array([1])

        self._results = None

    @property
    def time(self):
        return np.arange(-self.stimulusOffset, self._responseDuration - self.stimulusOffset, self._dt)

    @property
    def dt(self):
        return self._dt

    @dt.setter
    def dt(self, value):
        self._dt = value
        self._fs = 1 / value

    @property
    def fs(self):
        return self._fs

    @fs.setter
    def fs(self, value):
        self._fs = value
        self._dt = 1 / value

    @property
    def responseDuration(self):
        return self._responseDuration

    @responseDuration.setter
    def responseDuration(self, value):
        self._responseDuration = value

    @property
    def stimulusIntensities(self):
        return self._stimulusIntensities

    @stimulusIntensities.setter
    def stimulusIntensities(self, value):
        value = np.atleast_1d(value)
        self._stimulusIntensities = value
        self._adjust_stimulus_durations('intensity')
        self._adjust_pigment_activations()

    @property
    def pigmentActivations(self):
        return self._pigmentActivations

    @pigmentActivations.setter
    def pigmentActivations(self, value):
        value = np.atleast_1d(value)
        self._pigmentActivations = value
        self._adjust_stimulus_durations('activation')
        self._adjust_stimulus_intensities()

    @property
    def stimulusDurations(self):
        return self._stimulusDurations

    @stimulusDurations.setter
    def stimulusDurations(self, value):
        value = np.atleast_1d(value)
        num_activations = len(self._pigmentActivations)
        
        if len(value) == 1:
            value = np.full(num_activations, value[0])
        elif len(value) < num_activations:
            value = np.pad(value, (0, num_activations - len(value)), mode='edge')
        else:
            num_durations = len(value)
            self._pigmentActivations = np.pad(self._pigmentActivations, (0, num_durations - num_activations), mode='edge')
        
        self._stimulusDurations = value
        self._adjust_stimulus_intensities()

    @property
    def darkCurrent(self):
        return self.param['iDark']

    @darkCurrent.setter
    def darkCurrent(self, value):
        self.param['iDark'] = value

    @property
    def maxStep(self):
        return self._maxStep
    
    @maxStep.setter
    def maxStep(self,value):
        self._maxStep = float(value)
    
    @property
    def results(self):
        return self._results

    def _adjust_stimulus_durations(self, target_name):
        if target_name == "intensity":
            target = self._stimulusIntensities
        else:
            target = self._pigmentActivations
        if len(self._stimulusDurations) < len(target):
            repeats = -(-len(target) // len(self._stimulusDurations))
            newDur = np.tile(self._stimulusDurations, repeats)
            self._stimulusDurations = newDur[:len(target)]
        elif len(self._stimulusDurations) > len(target):
            self._stimulusDurations = self._stimulusDurations[:len(target)]
        
    def _adjust_pigment_activations(self, n=None):
        if n:
            # provided from duration setter
            if n > len(self._pigmentActivations):
                repeats = -(-n // len(self._pigmentActivations))
                newStims = np.tile(self._pigmentActivations, repeats)
                self.pigmentActivations = newStims[:n]
            elif n < len(self._pigmentActivations):
                self.pigmentActivations = self._pigmentActivations[:n]
        else:
            self._pigmentActivations = self._stimulusIntensities * self._stimulusDurations * self.param['colArea']

    def _adjust_stimulus_intensities(self, n=None):
        if n:
            # provided from duration setter
            if n > len(self._stimulusIntensities):
                repeats = -(-n // len(self._stimulusIntensities))
                newStims = np.tile(self._stimulusIntensities, repeats)
                self.stimulusIntensities = newStims[:n]
            elif n < len(self._stimulusIntensities):
                self.stimulusIntensities = self._stimulusIntensities[:n]
        else:
            self._stimulusIntensities = self._pigmentActivations / (self.param['colArea'] * self._stimulusDurations)

    def setParam(self, **kwargs):
        for key, value in kwargs.items():
            new_value = np.atleast_1d(value)
            if key in self.param:
                if len(new_value) > 1:
                    self.param[key] = new_value
                    self.__truncate_params(exclude=key)
                else:
                    self.param[key] = value
    
    def light_stimulus(self, stimulusIntensity, stimulusTime):
        time = self.time
        lightStimulus = np.zeros(time.shape)
        if stimulusIntensity > 0:
            suppress_time = 1 - self.suppress_interval(1, time, stimulusTime[0], stimulusTime[1], 0.0002)
            lightStimulus += stimulusIntensity * suppress_time * 1.05
        return lightStimulus

    def suppress_interval(self, suppressFactor, matrix, pstart, pend, sensitivity):
        return 1 - suppressFactor * (np.tanh((matrix - pstart) / sensitivity) - np.tanh((matrix - pend) / sensitivity)) / 2

    def diff_eq(self, t, u, lightStimulus, param):
        betaDark = param['betaDark']
        muRa = param['muRa']
        muTa = param['muTa']
        muPa = param['muPa']
        xi = param['xi']
        nAlpha = param['nAlpha']
        rAlpha = param['rAlpha']
        KAlpha = param['KAlpha'] / param['concCaDark']
        
        nCh = param['nCh']
        KEx = param['KEx'] / param['concCaDark']
        KCh = param['KCh'] / param['concCgDark']
        muCa = param['muCa']
        colArea = param['colArea']
        
        indTime = int((t + self.stimulusOffset) / self.dt)
        stimAmplitude = lightStimulus[indTime]

        ca = np.exp(-u[4])
        alpha = (1 + KAlpha**nAlpha) / (rAlpha + KAlpha**nAlpha) * (rAlpha * ca**nAlpha + KAlpha**nAlpha) / (ca**nAlpha + KAlpha**nAlpha)

        dudt = np.zeros_like(u)
        dudt[0] = muRa * (colArea * xi * stimAmplitude - u[0])
        dudt[1] = muTa * (u[0] - u[1])
        dudt[2] = muPa * (u[1] - u[2])
        dudt[3] = u[2] - betaDark * (np.exp(u[3]) * alpha - 1)
        dudt[4] = muCa * (
            (1 + KEx) / (ca + KEx) * ca - (1 + KCh**nCh) / (np.exp(-nCh * u[3]) + KCh**nCh) * np.exp(-nCh * u[3])
        ) * np.exp(u[4])
        return dudt

    def simulate_once(self, stimulusIntensity, stimulusTime, pigmentActivation,param=None):
        if param is None:
            param = self.__generate_parameters()
        time = self.time
        lightStimulus = self.light_stimulus(stimulusIntensity, stimulusTime)

        init_values = np.zeros(5)
        attempt = 0
        max_step = self.maxStep # np.inf  # Initial max step size

        while attempt < self.MAX_SOLVE_ATTEMPTS:
            attempt += 1
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always", RuntimeWarning)
                    solution = solve_ivp(
                        lambda t, y: self.diff_eq(t, y, lightStimulus, param),
                        [time[0], time[-1]],
                        init_values,
                        t_eval=time,
                        method='RK45',  # Use RK45 solver
                        vectorized=True,
                        rtol=1e-6,       # Relative tolerance
                        atol=1e-8,       # Absolute tolerance
                        max_step=max_step  # Set max step size
                    )

                    if not any(item.category == RuntimeWarning for item in w):
                        break  # Exit loop if no warning was raised

            except Exception as e:
                raise SimulationError(f"Attempt {attempt} failed with error: {e}")

            max_step = 0.01 if max_step == np.inf else max_step / 2  # Decrease max step size for the next attempt

        if attempt == self.MAX_SOLVE_ATTEMPTS:
            warnings.warn("Simulation completed with warnings due to repeated overflow warnings.", SimulationWarning)

        sol = solution.y.T

        cG = np.exp(-sol[:, 3])
        ca = np.exp(-sol[:, 4])

        # Extracellular (suction) currents
        extracellularCurrentCh = 2 / (param['fChCa'] + 2) * (1 + param['KCh']**param['nCh']) / (cG**param['nCh'] + param['KCh']**param['nCh']) * cG**param['nCh']
        extracellularCurrentEx = param['fChCa'] / (param['fChCa'] + 2) * (1 + param['KEx']) / (ca + param['KEx']) * ca
        extracellularCurrent = extracellularCurrentCh + extracellularCurrentEx

        # Intracellular (whole-cell patch) currents
        intracellularCurrentCh = 2 / (param['fChCa'] + 2) * (1 - (1 + param['KCh']**param['nCh']) / (cG**param['nCh'] + param['KCh']**param['nCh']) * cG**param['nCh'])
        intracellularCurrentEx = param['fChCa'] / (param['fChCa'] + 2) * (1 - (1 + param['KEx']) / (ca + param['KEx']) * ca)
        intracellularCurrent = intracellularCurrentCh + intracellularCurrentEx

        return {
            'time': time,
            'PDEstar': sol[:, 2] / param['betaSub'],
            'Tstar': sol[:, 1] * param['muPa'] / (param['betaSub'] * param['muTa']),
            'Pstar': sol[:, 0] / (param['muRa'] * param['xi']),
            'cGMP': cG,
            'Ca': ca,
            'extracellularCurrentNorm': extracellularCurrent,
            'extracellularCurrentChNorm': extracellularCurrentCh,
            'extracellularCurrentExNorm': extracellularCurrentEx,
            'intracellularCurrentNorm': intracellularCurrent,
            'intracellularCurrentChNorm': intracellularCurrentCh,
            'intracellularCurrentExNorm': intracellularCurrentEx,
            'extracellularCurrentScaled': extracellularCurrent * param['iDark'],
            'extracellularCurrentChScaled': extracellularCurrentCh * param['iDark'],
            'extracellularCurrentExScaled': extracellularCurrentEx * param['iDark'],
            'intracellularCurrentScaled': intracellularCurrent * param['iDark'],
            'intracellularCurrentChScaled': intracellularCurrentCh * param['iDark'],
            'intracellularCurrentExScaled': intracellularCurrentEx * param['iDark'],
            'lightStimulus': lightStimulus,
            'stimulusIntensity': stimulusIntensity,
            'pigmentActivation': pigmentActivation,
            'modelParameters': {key: np.copy(value) for key, value in param.items() if key != 'time'}
        }

    def simulate(self, stimulusIntensities=None, stimulusDurations=None):
        if stimulusIntensities is not None:
            self.stimulusIntensities = stimulusIntensities
        if stimulusDurations is not None:
            self.stimulusDurations = stimulusDurations

        # Determine Stimulus Times
        stimulusTimes = [(np.float64(0), d) for d in self.stimulusDurations]
        params = self.__generate_parameters()
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
        self._results = []  # Clear previous results
        results = []
        with ThreadPoolExecutor() as executor:
            futures = []
            # Loop through stimuli
            for intensity, time, activation in zip(self.stimulusIntensities, stimulusTimes, self.pigmentActivations):
                # Loop through parameter sweep
                if nSweep:
                    for i in range(nSweep):
                        param_set = {
                            key:np.copy(value) for key,value in params.items()
                            } # copy the parameters
                        param_set[sweep_key] = np.asarray(sweep_param[sweep_key][i])
                        label = f"{activation} (R*); {param_set[sweep_key]} ({sweep_key})"
                        futures.append(
                            (
                                executor.submit(
                                    self.simulate_once,
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
                                self.simulate_once,
                                intensity,
                                time,
                                activation,
                                params
                                ),
                            label
                        )
                    )
            
            for future in as_completed([fut for fut, _ in futures]):
                # Find the corresponding label
                label = next(label for fut, label in futures if fut == future)
                result = future.result()
                result['label'] = label
                results.append(result)

        self._results = sorted(results, key=lambda x: x['stimulusIntensity'])

    def export(self, *fields):
        if self._results is None:
            warnings.warn("No simulation results available.", SimulationWarning)
            return None
        
        data = {}
        for result in self._results:
            for field in fields:
                key = f"{field}_P*{result['pigmentActivation']}"
                data[key] = np.copy(result[field])

        return np.array([data[key] for key in sorted(data.keys())]).T

    
    def getResult(self, x, y, opts={}):
        if not self.results:
            warnings.warn("No simulation results available.", SimulationWarning)
            return []
        valid_keys = self.getLabels()
        if x not in valid_keys or y not in valid_keys:
            warnings.warn(f"Invalid keys: {x}, {y}", SimulationWarning)
            return []
        # for now, opts is empty, but we will use it to gather different sorting or grouping values and set other plot options
        # return {label:{x:label (unit), y: label (unit)}, data: [{x:data,y:data,label:stim R*}]
        data = []
        for result in self.results:
            result_copy = {key: np.copy(value) for key, value in result.items()}
            data.append(
                {
                    "x": result_copy[x],
                    "y": result_copy[y],
                    "label": result_copy['label'] if 'label' in result_copy else f"{result_copy['pigmentActivation']} R*"
                }
            )
        return {
            "label": {
                "x": self.__get_axes_label(x), "y": self.__get_axes_label(y)
            },
            "data": data
        }

    
    def getParameters(self):
        return {
            'stimulusConfiguration': {
                'dt': self.dt,
                'stimulusOffset': self.stimulusOffset,
                'fs': self.fs,
                'responseDuration': self.responseDuration,
                'stimulusIntensities': self.stimulusIntensities,
                'pigmentActivations': self.pigmentActivations,
                'stimulusDurations': self.stimulusDurations
            },
            'modelParameters': self.__generate_parameters()
        }

    def getLabels(self):
        return [
            'time',
            'PDEstar',
            'Tstar',
            'Pstar',
            'cGMP',
            'Ca',
            'extracellularCurrentNorm',
            'extracellularCurrentChNorm',
            'extracellularCurrentExNorm',
            'intracellularCurrentNorm',
            'intracellularCurrentChNorm',
            'intracellularCurrentExNorm',
            'extracellularCurrentScaled',
            'extracellularCurrentChScaled',
            'extracellularCurrentExScaled',
            'intracellularCurrentScaled',
            'intracellularCurrentChScaled',
            'intracellularCurrentExScaled',
            'lightStimulus'
        ]
    
    def getValidSortKeys(self):
        keys = ['lightStimulus','stimulusIntensity','pigmentActivation']
        for key,_ in self.param.items():
            keys.append(key)
        return keys
    
    def __truncate_params(self,exclude=None):
        for key, value in self.param.items():
            new_value = np.atleast_1d(value)
            if key != exclude and len(new_value) > 1:
                self.param[key] = new_value[0]
    
    def __generate_parameters(self):
        return {key: np.copy(value) for key, value in self.param.items()}
    
    def __get_axes_label(self,key):
        labels = {
            'time': 'Time (s)',
            'PDEstar': 'PDE*',
            'Tstar': 'T*',
            'Rstar': 'R*',
            'cGMP': 'cGMP',
            'Ca': 'Calcium (Ca)',
            'extracellularCurrentNorm': 'Ext. Current (norm.)',
            'extracellularCurrentChNorm': 'Ext. Channel (norm.)',
            'extracellularCurrentExnorm': 'Ext. Exchanger (norm.)',
            'intracellularCurrentNorm': 'Int. Current (norm.)',
            'intracellularCurrentChNorm': 'Int Channel (norm.)',
            'intracellularCurrentExNorm': 'Int. Exchanger (norm.)',
            'extracellularCurrentScaled': 'Ext. Current (pA)',
            'extracellularCurrentChScaled': 'Ext. Channel (pA)',
            'extracellularCurrentExScaled': 'Ext. Exchanger (pA)',
            'intracellularCurrentScaled': 'Int. Current (pA)',
            'intracellularCurrentChScaled': 'Int. Channel (pA)',
            'intracellularCurrentExScaled': 'Int. Exchanger (pA)',
            'lightStimulus': 'Light Stimulus (photons/µm²/s)'
        }
        return labels.get(key,key)
        
    def __get_unit(self, key):
        units = {
            'betaDark': 's⁻¹',
            'concCaDark': 'µM',
            'concCgDark': 'µM',
            'fChCa': '',
            'colArea': 'µm²/photon',
            'betaSub': '',
            'xi': '',
            'muRa': 's⁻¹',
            'muTa': 's⁻¹',
            'muPa': 's⁻¹',
            'nAlpha': '',
            'KAlpha': 'µM',
            'rAlpha': '',
            'nCh': '',
            'KCh': 'µM',
            'KEx': 'µM',
            'muCa': '',
            'time': 's',
            
        }
        return units.get(key, '')
    
    def __repr__(self):
        return f"Phototransduction(\n" \
            f"  stimulusIntensities={self._stimulusIntensities} (photons/µm²),\n" \
            f"  stimulusDurations={self._stimulusDurations} (s),\n" \
            f"  pigmentActivations={self._pigmentActivations} (P*),\n" \
            f"  sampleRate={self._fs} (Hz),\n" \
            f"  dt={self._dt} (s),\n" \
            f"  responseDuration={self._responseDuration} (s),\n" \
            f"  stimulusOffset={self.stimulusOffset} (s),\n" \
            f"  darkCurrent={self.param['iDark']} (pA),\n" \
            f"  params={{{', '.join([f'{key}: {value}' for key, value in self.param.items() if key != 'time'])}}}\n" \
            f")"

    def __str__(self):
        return f"Stimulus Intensities: {self._stimulusIntensities} (photons/µm²)\n" \
            f"Stimulus Durations: {self._stimulusDurations} (s)\n" \
            f"Pigment Activations: {self._pigmentActivations} (P*)\n" \
            f"Sample Rate: {self._fs} (Hz)\n" \
            f"dt: {self._dt} (s)\n" \
            f"Response Duration: {self._responseDuration} (s)\n" \
            f"Stimulus Offset: {self.stimulusOffset} (s)\n" \
            f"Dark Current: {self.param['iDark']} (pA)\n" \
            f"Model Parameters:\n" + \
            '\n'.join([f"  {key}: {value}" for key, value in self.param.items() if key != 'time'])