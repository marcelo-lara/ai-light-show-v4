"""
Modulation System

Epic 05: Modulation System
Defines audio and procedural modulation sources, mapping operations, and bindings.
"""

import math
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum


class ModulatorType(str, Enum):
    """Supported modulator types."""
    AUDIO_BAND = "audio_band"
    AUDIO_ONSET = "audio_onset"
    BEAT_PULSE = "beat_pulse"
    BEAT_PHASE = "beat_phase"
    BAR_PHASE = "bar_phase"
    PHRASE_PROGRESS = "phrase_progress"
    LFO = "lfo"
    RANDOM = "random"


class LFOWaveform(str, Enum):
    """LFO waveforms."""
    SINE = "sine"
    TRIANGLE = "triangle"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"


@dataclass
class ModulationContext:
    """
    Epic 05: Context for modulation evaluation.
    
    Provides audio analysis and time information needed by modulators.
    """
    frame_time: float
    beat_progress: float = 0.0  # 0-1 within current beat
    bar_progress: float = 0.0   # 0-1 within current bar
    phrase_progress: float = 0.0  # 0-1 within phrase
    fft_bands: Optional[List[float]] = None  # Normalized FFT band values (0-1)
    onset_detected: bool = False
    seed: int = 0


class Modulator(ABC):
    """
    Epic 05.B1-B2: Base class for modulation sources.
    
    Modulators produce time-varying values that can be bound to layer parameters.
    """
    
    def __init__(self, modulator_id: str):
        self.modulator_id = modulator_id
    
    @abstractmethod
    def evaluate(self, context: ModulationContext) -> float:
        """
        Evaluate this modulator at the given time/context.
        
        Epic 05.B6: Deterministic execution - same inputs produce same output.
        
        Returns:
            Float value (typically normalized to 0-1 range, but unconstrained)
        """
        pass


class AudioBandModulator(Modulator):
    """
    Epic 05.B1: Audio modulator - responds to FFT band energy.
    """
    
    def __init__(self, band_index: int = 0):
        super().__init__(f"audio_band_{band_index}")
        self.band_index = band_index
    
    def evaluate(self, context: ModulationContext) -> float:
        """Return energy in specified FFT band."""
        if context.fft_bands is None:
            return 0.0
        if self.band_index >= len(context.fft_bands):
            return 0.0
        return max(0.0, min(1.0, context.fft_bands[self.band_index]))


class OnsetModulator(Modulator):
    """
    Epic 05.B1: Audio modulator - responds to onset detection.
    """
    
    def __init__(self):
        super().__init__("audio_onset")
    
    def evaluate(self, context: ModulationContext) -> float:
        """Return 1.0 on onset, 0.0 otherwise."""
        return 1.0 if context.onset_detected else 0.0


class BeatPulseModulator(Modulator):
    """
    Epic 05.B1: Audio modulator - beat pulse (triangular envelope).
    """
    
    def __init__(self):
        super().__init__("beat_pulse")
    
    def evaluate(self, context: ModulationContext) -> float:
        """Return triangular pulse over beat duration."""
        # Triangular pulse: rise to peak at 0.5, fall back
        if context.beat_progress < 0.5:
            return context.beat_progress * 2  # 0 to 1
        else:
            return (1 - context.beat_progress) * 2  # 1 to 0


class BeatPhaseModulator(Modulator):
    """
    Epic 05.B1: Audio modulator - beat phase (sawtooth).
    """
    
    def __init__(self):
        super().__init__("beat_phase")
    
    def evaluate(self, context: ModulationContext) -> float:
        """Return linear phase through beat (0-1)."""
        return context.beat_progress


class BarPhaseModulator(Modulator):
    """
    Epic 05.B1: Audio modulator - bar phase.
    """
    
    def __init__(self):
        super().__init__("bar_phase")
    
    def evaluate(self, context: ModulationContext) -> float:
        """Return linear phase through bar (0-1)."""
        return context.bar_progress


class PhraseProgressModulator(Modulator):
    """
    Epic 05.B1: Audio modulator - phrase progress.
    """
    
    def __init__(self):
        super().__init__("phrase_progress")
    
    def evaluate(self, context: ModulationContext) -> float:
        """Return linear progress through phrase (0-1)."""
        return context.phrase_progress


class LFOModulator(Modulator):
    """
    Epic 05.B2: Procedural modulator - LFO (Low Frequency Oscillator).
    """
    
    def __init__(self, frequency: float = 1.0, waveform: LFOWaveform = LFOWaveform.SINE):
        super().__init__(f"lfo_{frequency}_{waveform.value}")
        self.frequency = frequency
        self.waveform = waveform
    
    def evaluate(self, context: ModulationContext) -> float:
        """Generate LFO output."""
        phase = (context.frame_time * self.frequency * 2 * math.pi) % (2 * math.pi)
        
        if self.waveform == LFOWaveform.SINE:
            return (math.sin(phase) + 1) / 2  # Normalize to 0-1
        elif self.waveform == LFOWaveform.TRIANGLE:
            # Triangle wave: -1 to 1
            normalized = (phase / (2 * math.pi))
            if normalized < 0.5:
                return normalized * 4 - 1  # -1 to 1
            else:
                return (1 - normalized) * 4 - 1  # 1 to -1
            return (abs(4 * normalized - 2) - 1) / 2 + 0.5  # Normalize to 0-1
        elif self.waveform == LFOWaveform.SQUARE:
            return 1.0 if phase < math.pi else 0.0
        elif self.waveform == LFOWaveform.SAWTOOTH:
            return (phase / (2 * math.pi))  # 0 to 1
        
        return 0.0


class RandomModulator(Modulator):
    """
    Epic 05.B2: Procedural modulator - seeded random source.
    """
    
    def __init__(self, rate: float = 1.0, seed_base: int = 0):
        super().__init__(f"random_{rate}_{seed_base}")
        self.rate = rate
        self.seed_base = seed_base
    
    def evaluate(self, context: ModulationContext) -> float:
        """
        Generate deterministic random value.
        
        Epic 05.B6: Deterministic - same frame_time + seed produces same random value.
        """
        # Seed based on frame index (derived from frame_time)
        frame_index = int(context.frame_time * self.rate)
        rng = random.Random()
        rng.seed(context.seed ^ self.seed_base ^ frame_index)
        return rng.random()


class MappingOperation(ABC):
    """
    Epic 05.B3-B4: Base class for mapping operations.
    
    Transforms modulator values before binding to parameters.
    """
    
    @abstractmethod
    def apply(self, value: float) -> float:
        """Apply mapping operation."""
        pass


class ScaleMapping(MappingOperation):
    """
    Epic 05.B3: Scale operation - multiply by factor.
    """
    
    def __init__(self, factor: float):
        self.factor = factor
    
    def apply(self, value: float) -> float:
        return value * self.factor


class ClampMapping(MappingOperation):
    """
    Epic 05.B3: Clamp operation - constrain to range.
    """
    
    def __init__(self, min_val: float, max_val: float):
        self.min_val = min_val
        self.max_val = max_val
    
    def apply(self, value: float) -> float:
        return max(self.min_val, min(self.max_val, value))


class InvertMapping(MappingOperation):
    """
    Epic 05.B3: Invert operation - flip value (1 - x).
    """
    
    def apply(self, value: float) -> float:
        return 1.0 - value


class CurveMapping(MappingOperation):
    """
    Epic 05.B4: Curve operation - apply power curve for smoothing.
    """
    
    def __init__(self, power: float = 2.0):
        self.power = power
    
    def apply(self, value: float) -> float:
        if value < 0:
            return -((-value) ** self.power)
        return value ** self.power


class SmoothMapping(MappingOperation):
    """
    Epic 05.B4: Smooth operation - exponential smoothing (low-pass filter).
    
    Note: This requires frame context which we don't have in a stateless mapper.
    For now, return value as-is with note about stateful implementation.
    """
    
    def __init__(self, smoothing_factor: float = 0.5):
        self.smoothing_factor = smoothing_factor
        self.last_value = 0.0
    
    def apply(self, value: float) -> float:
        # Stateful smoothing
        self.last_value = self.last_value * (1 - self.smoothing_factor) + value * self.smoothing_factor
        return self.last_value


class LagMapping(MappingOperation):
    """
    Epic 05.B4: Lag operation - delay/lag effect.
    """
    
    def __init__(self, lag_time: float = 0.1, sample_rate: float = 30.0):
        self.lag_samples = int(lag_time * sample_rate)
        self.buffer = [0.0] * max(1, self.lag_samples)
        self.index = 0
    
    def apply(self, value: float) -> float:
        self.buffer[self.index] = value
        self.index = (self.index + 1) % len(self.buffer)
        return sum(self.buffer) / len(self.buffer)


class QuantizeMapping(MappingOperation):
    """
    Epic 05.B4: Quantize operation - snap to discrete levels.
    """
    
    def __init__(self, levels: int = 4):
        self.levels = levels
    
    def apply(self, value: float) -> float:
        return round(value * self.levels) / self.levels


class ModulationChain:
    """
    Chain of mapping operations applied to a modulator value.
    
    Epic 05.B5: Mapping operations applied in declared order.
    """
    
    def __init__(self):
        self.mappings: List[MappingOperation] = []
    
    def add_mapping(self, mapping: MappingOperation) -> "ModulationChain":
        """Add a mapping operation to the chain."""
        self.mappings.append(mapping)
        return self
    
    def apply(self, value: float) -> float:
        """
        Epic 05.B3-B4: Apply all mappings in order.
        """
        for mapping in self.mappings:
            value = mapping.apply(value)
        return value


@dataclass
class ModulatorBinding:
    """
    Epic 05.B5: Binding of modulator to layer parameter.
    
    Defines which modulator is bound to which parameter with which mapping chain.
    """
    parameter_name: str
    modulator: Modulator
    mapping_chain: Optional[ModulationChain] = None
    
    def evaluate(self, context: ModulationContext) -> float:
        """Evaluate the modulator with mappings applied."""
        value = self.modulator.evaluate(context)
        if self.mapping_chain:
            value = self.mapping_chain.apply(value)
        return value


class ModulationSystem:
    """
    Epic 05: Complete modulation system.
    
    Manages modulators, bindings, and evaluation for preset parameters.
    """
    
    def __init__(self):
        self.modulators: Dict[str, Modulator] = {}
        self.bindings: List[ModulatorBinding] = []
        self._register_default_modulators()
    
    def _register_default_modulators(self) -> None:
        """Register default modulator sources."""
        defaults = [
            AudioBandModulator(0),
            AudioBandModulator(1),
            AudioBandModulator(2),
            AudioBandModulator(3),
            OnsetModulator(),
            BeatPulseModulator(),
            BeatPhaseModulator(),
            BarPhaseModulator(),
            PhraseProgressModulator(),
        ]
        for mod in defaults:
            self.modulators[mod.modulator_id] = mod
    
    def register_modulator(self, modulator: Modulator) -> None:
        """Register a custom modulator."""
        self.modulators[modulator.modulator_id] = modulator
    
    def create_lfo_modulator(self, frequency: float, waveform: LFOWaveform = LFOWaveform.SINE) -> Modulator:
        """Create and register an LFO modulator."""
        lfo = LFOModulator(frequency, waveform)
        self.register_modulator(lfo)
        return lfo
    
    def create_random_modulator(self, rate: float = 1.0, seed: int = 0) -> Modulator:
        """Create and register a random modulator."""
        rand_mod = RandomModulator(rate, seed)
        self.register_modulator(rand_mod)
        return rand_mod
    
    def bind_modulator(
        self,
        parameter_name: str,
        modulator_id: str,
        mapping_chain: Optional[ModulationChain] = None
    ) -> bool:
        """
        Epic 05.B5: Bind a modulator to a parameter.
        
        Returns True if successful, False if modulator not found.
        """
        if modulator_id not in self.modulators:
            return False
        
        modulator = self.modulators[modulator_id]
        binding = ModulatorBinding(parameter_name, modulator, mapping_chain)
        self.bindings.append(binding)
        return True
    
    def evaluate_bindings(self, context: ModulationContext) -> Dict[str, float]:
        """
        Evaluate all bindings for current context.
        
        Epic 05.B7: Debug output shape - returns modulator values.
        
        Returns:
            Dict mapping parameter names to evaluated modulation values
        """
        result: Dict[str, float] = {}
        for binding in self.bindings:
            value = binding.evaluate(context)
            result[binding.parameter_name] = value
        return result
    
    def get_debug_output(self, context: ModulationContext) -> Dict[str, Any]:
        """
        Epic 05.B7: Get structured debug output for modulator inspection.
        
        Returns diagnostic information for UI display.
        """
        return {
            "frame_time": context.frame_time,
            "beat_progress": context.beat_progress,
            "bar_progress": context.bar_progress,
            "phrase_progress": context.phrase_progress,
            "onset_detected": context.onset_detected,
            "fft_bands": context.fft_bands or [],
            "bindings": self.evaluate_bindings(context),
        }
