import copy
import itertools
from typing import List, Optional

from candidate import Candidate


class GenerationProcess:
    def __init__(self):
        self._generation_trace: List[Optional[Candidate]] = []
        self._generation_time: int = -1

    def add_output(self, generation_index: int, generation_output: List[Optional[Candidate]]):
        generated_output_length: int = len(list(itertools.takewhile(lambda e: e is not None, generation_output)))
        print(f"corrected length output = {generated_output_length}")

        prev_generation_time: int = self._generation_time

        if generation_index > len(self._generation_trace):
            for _ in range(len(self._generation_trace), generation_index):
                self._generation_trace.append(None)

        for i in range(generated_output_length):
            output_cloned: Optional[Candidate] = copy.deepcopy(generation_output[i])
            if i + generation_index < len(self.generation_trace):
                self.generation_trace[generation_index + i] = output_cloned
            else:
                self.generation_trace.append(output_cloned)

        self._generation_time = generation_index + generated_output_length
        self._generation_trace = self._generation_trace[:self._generation_time]
        print(f"generation time: {prev_generation_time} --> {self._generation_time}")

    @property
    def generation_time(self):
        return self._generation_time

    def update_generation_time(self, new_time: int):
        self._generation_time = new_time

    @property
    def generation_trace(self):
        return self._generation_trace
