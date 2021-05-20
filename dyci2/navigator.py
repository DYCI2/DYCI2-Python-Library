# -*-coding:Utf-8 -*

####################################################################################
# navigator.py
# Parameters and methods to navigate through a symbolic sequence.
# Jérôme Nika, Ken Déguernel - IRCAM STMS Lab
# copyleft 2016 - 2018
####################################################################################

# TODO
# ICI ET DANS LES MODEL NAVIGATORS : TESTER SI LE REQUIRED LABEL EST BIEN DU MEME TYPE QUE LES LABELS DANS LE MODEL

"""
Navigator
===================

This module defines parameters and methods to navigate through a symbolic sequence.
The classes defined in this module are used in association with models (cf. :mod:`Model`) when creating
**model navigator** classes (cf. :mod:`ModelNavigator`).

"""

import random
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Dict, Tuple

from candidate import Candidate
from dyci2.intervals import *
# POUR SEQUENCE ET LABELS :
# ET AUSSI POUR HISTORY_AND_TABOOS QUI DEPEND DE LA TAILLE D'AILLEURS !
# TODO : que faire si on apprend un nouvel élément ? il faut agrandir listes !
# TODO : surchager set use_taboo pour que tous les -1 passent à 0 si on passe à FALSE
# self.avoid_repetitions_mode = 1
# TODO : mode 0 : répétitions authorisées, mode 1 = on prend le min, mode 2, interdire les déjà passés
# TODO : SURCHARGER POUR INTERDIRE LES AUTRES
# TODO : QUAND ON GENERE, DEBUT OU NON ? SOIT INTEGRER DANS PARAMETRES FONCTIONS SOIT DECIDER QU'ON APPELLE
#  reinit_navigation_param si c'est le début
from label import Label
from memory import MemoryEvent, Memory
from utils import noneIsInfinite


class Navigator(ABC):
    def __init__(self, memory: Memory, equiv: Callable = (lambda x, y: x == y)):
        self.memory: Memory = memory
        self.equiv: Callable = equiv

    @abstractmethod
    def learn_sequence(self, sequence: List[MemoryEvent], equiv: Optional[Callable] = None):
        # FIXME[MergeState]: A[x], B[x], C[x], D[x], E[]
        """ TODO """

    @abstractmethod
    def learn_event(self, event: MemoryEvent, equiv: Optional[Callable] = None):
        # FIXME[MergeState]: A[x], B[x], C[x], D[x], E[]
        """ TODO """

    @abstractmethod
    def rewind_generation(self, index_state: int):
        # FIXME[MergeState]: A[x], B[x], C[x], D[x], E[]
        """ TODO """

    @abstractmethod
    def weight_candidates(self, candidates: List[Candidate]) -> List[Candidate]:
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """ TODO """

    @abstractmethod
    def clear(self):
        # FIXME[MergeState]: A[x], B[x], C[x], D[x], E[]
        """ TODO """


# noinspection PyIncorrectDocstring
class FactorOracleNavigator(Navigator):
    """
    The class :class:`~Navigator.Navigator` implements **parameters and methods that are used to navigate through a
    model of sequence**.
    These parameters and methods are **model-independent**.
    This class defines in particular the naive versions of the methods :meth:`Navigator.simply_guided_navigation`
    and :meth:`Navigator.free_navigation` handling the navigation through a sequence when it is respectively guided by
    target labels and free.
    These methods are overloaded by model-dependant versions (and other model-dependent parameters or methods can be
    added) when creating a **model navigator** class (cf. :mod:`ModelNavigator`).
    This class is not supposed to be used alone, only in association with a model within a model navigator. Therefore
    its attributes are only "flags" that can be used when defining a model navigator.

    # :param sequence: sequence learnt in the model.
    :type sequence: list or str
    # :param labels: sequence of labels chosen to describe the sequence.
    :type labels: list or str
    :param equiv: comparison function given as a lambda function, default if no parameter is given: self.equiv.
    :type equiv: function

    # :param current_navigation_index: current length of the navigation
    :type current_navigation_index: int

    #:param current_position_in_sequence: current position of the readhead in the model. ** When this attribute receives
    a new value, :meth:`Navigator.record_execution_trace` is called to update :attr:`self.execution_trace`, and
    :meth:`Navigator.update_history_and_taboos` is called to update :attr:`self.history_and_taboos`.**
    :type current_position_in_sequence: int
    #:param current_continuity: current number of consecutive elements retrieved in the sequence at the current step of
    generation
    :type current_continuity: int
    :param max_continuity: limitation of the length of the sub-sequences that can be retrieved from the sequence.
    :type max_continuity: int
    #:param no_empty_event: authorize or not to output empty events.
    :type no_empty_event: bool
    #:param avoid_repetitions_mode: 0: authorize repetitions; 1: favor less previously retrieved events;
    2: forbid repetitions.
    :type avoid_repetitions_mode: int
    :param control_parameters: list of the slots of the class that are considered as "control parameters" i.e. that can
    be used by a user to author / monitor the generation processes.
    :type control_parameters: list(str)
    :param execution_trace_parameters: list of the slots of the class that are stored in the execution trace used in
    :meth:`Generator.go_to_anterior_state_using_execution_trace`.
    :type control_parameters: list(str)
    #:param execution_trace: History of the previous runs of the generation model. The list of the parameters of the
    model whose values are stored in the execution trace is defined in :attr:`self.execution_trace_parameters`.
    :type execution_trace: dict
    """

    def __init__(self, memory: Memory, equiv: Optional[Callable] = (lambda x, y: x == y), max_continuity=20,
                 control_parameters=(), execution_trace_parameters=()):
        super().__init__(memory, equiv)
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        self.sequence: List[MemoryEvent] = memory.events
        self.labels: List[Label] = [e.label() for e in memory.events]
        self.equiv: Callable = equiv
        self.no_empty_event = True
        self.max_continuity = max_continuity
        self.avoid_repetitions_mode = 0
        self.execution_trace = {}

        self.history_and_taboos: List[Optional[int]] = [0] * (len(self.sequence))
        self.current_continuity: int = -1
        self.current_position_in_sequence: int = -1
        self.current_navigation_index: int = -1
        self.reinit_navigation_param_old_modelnavigator()

        self.control_parameters = ["avoid_repetitions_mode", "max_continuity"]
        if type(control_parameters) != type(None):
            print("argument control_parameters = {}".format(control_parameters))
            for param in control_parameters:
                # TODO : PLUTOT FAIRE AVEC UN TRY ASSERT... POUR ETRE PLUS PROPRE
                if param in self.__dict__.keys():
                    self.control_parameters.append(param)
        else:
            print("argument control_parameters = None")

        self.execution_trace_parameters = ["current_position_in_sequence", "history_and_taboos", "current_continuity"]
        for param in execution_trace_parameters:
            # TODO : TRY ASSERT... POUR ETRE PLUS PROPRE
            if param in self.__dict__.keys():
                self.execution_trace_parameters.append(param)

    def __setattr__(self, name_attr, val_attr):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        # super.__setattr__(self, name_attr, val_attr)
        object.__setattr__(self, name_attr, val_attr)
        # TODO : SUPPRIMER TRACE AVANT TEMPS PERFORMANCE

    def rewind_generation(self, index_state: int):
        self._go_to_anterior_state_using_execution_trace(index_in_navigation=index_state)

    def weight_candidates(self, candidates: List[Candidate], model_direct_transitions: Dict[int, Tuple[Label, int]],
                          shift_index: int, sequence: List[Optional[MemoryEvent]], required_label: Optional[Label],
                          print_info: bool = False) -> List[Candidate]:
        str_print_info: str = f"{shift_index} " \
                              f"(cont. = {self.current_continuity}/{self.max_continuity})" \
                              f": {self.current_position_in_sequence}"

        candidates: List[Candidate] = self.filter_using_history_and_taboos(candidates)

        # Case 1: Transition to state immediately following the previous one
        candidates = self._follow_continuation_using_transition(candidates, model_direct_transitions)
        if len(candidates) > 0:
            # TODO[C]: Remove this once follow_continuation_using_transition returns all candidates.
            str_print_info += f" -{candidates[0].event.label()}-> {candidates[0].index}"
        else:
            # Case 2: Transition to any other state in the list of candidates
            # TODO[C]: NOTE! This one will remove the actual candidate selected in the previous step if called.
            # TODO[B]: Migrate the random choice performed in this step to top level
            candidates = self._follow_continuation_with_jump(candidates, model_direct_transitions)

            if len(candidates) > 0:
                prev_index: int = candidates[0].index - 1
                str_print_info += f" ...> {prev_index} - {model_direct_transitions.get(prev_index)[0]} " \
                                  f"-> {model_direct_transitions.get(prev_index)[1]}"

            else:
                # Case 3: Select from all valid candidates.
                # Exclude first (None) and last element from list of candidates
                candidates = [Candidate(e, i, 1.0, None) for (i, e) in enumerate(sequence[1:-1], start=1)]
                candidates = self.filter_using_history_and_taboos(candidates)
                if required_label is not None:
                    candidates = self.find_matching_label_without_continuation(required_label, candidates, equiv)
                else:
                    candidates = self._follow_continuation_with_jump(candidates, model_direct_transitions)

                if len(candidates) > 0:
                    str_print_info += f" xxnothingxx - random: {candidates[0].index}"
                else:
                    str_print_info += " xxnothingxx"

        if print_info:
            print(str_print_info)

        return candidates

    def find_prefix_matching_with_labels(self, use_intervals, labels, list_of_labels, continuity_with_future,
                                         authorized_indexes, authorized_transformations, sequence_to_interval_fun,
                                         equiv_interval, equiv):
        # FIXME[MergeState]: A[], B[], C[], D[], E[]
        # TODO[A]: This should probably return a list of candidates

        # print("LOOKING FOR PREFIXES OF {}".format(list_of_labels))

        if use_intervals:
            index_delta_prefixes, max_length = filtered_prefix_indexing_intervals(sequence=labels,
                                                                                  pattern=list_of_labels,
                                                                                  length_interval=continuity_with_future,
                                                                                  authorized_indexes=authorized_indexes,
                                                                                  authorized_intervals=authorized_transformations,
                                                                                  sequence_to_interval_fun=sequence_to_interval_fun,
                                                                                  equiv=equiv_interval,
                                                                                  print_info=False)
        # index_delta_prefixes, max_length = filtered_prefix_indexing_intervals(sequence = self.memory.labels,
        #     pattern = list_of_labels, length_interval = self.continuity_with_future,
        #     authorized_indexes = authorized_indexes,
        #     authorized_intervals = self.authorized_tranformations ,
        #     sequence_to_interval_fun = self.sequence_to_interval_fun,
        #     equiv_mod_interval = self.equiv_mod_interval, print_info = False)

        else:
            index_delta_prefixes, max_length = PrefixIndexing \
                .filtered_prefix_indexing(sequence=labels, pattern=list_of_labels,
                                          length_interval=continuity_with_future, authorized_indexes=authorized_indexes,
                                          equiv=equiv, print_info=False)

        # TODO : FAIRE LE PRINT COMME POUR LE RESTE DE LA NAVIGATION
        # TODO : FILTRER LISTES DES PREFIXES
        # TODO : MODULARISER FAIRE UNE FONCTION POUR LE CHOIX, ET PLUS DE POSSIBILITES QUE RANDOM
        #  (e.g. longueur prefixe)...
        #  ON EN EST OU DU FILTRAGE PAR POSITIONS OU IL Y A DES SUFFIX LINKS ?
        # TODO : STOCKER ALTERNATIVE_PATHS ICI, IE TOUS LES PREFIXES --> MELANGE SOMAX

        # print("SCENARIO ONE PHASE 2")
        s, t, length_selected_prefix = self.choose_prefix_from_list(index_delta_prefixes, pattern=list_of_labels)
        return s, t, length_selected_prefix

    def _go_to_anterior_state_using_execution_trace(self, index_in_navigation):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        This method is called when the run of a new query rewrites previously generated anticipations.
        It uses :attr:`self.execution_trace` to go back at the state where the navigator was at the "tiling time".

        :param index_in_navigation: "tiling index" in the generated sequence
        :type index_in_navigation: int

        :see also: The list of the parameters of the model whose values are stored in the execution trace is defined in
        :attr:`self.execution_trace_parameters`.

        """

        print("GO TO ANTERIOR STATE USING EXECUTION TRACE\nGoing back to state when {} was generated:\n{}".format(
            index_in_navigation, self.execution_trace[index_in_navigation]))
        history_after_generating_prev = self.execution_trace[index_in_navigation]
        for name_slot, value_slot in history_after_generating_prev.items():
            self.__dict__[name_slot] = value_slot

    # This function is supposedly never called as it is overwritten
    # def reinit_navigation_param_old_navigator(self):
    #     # FIXME[MergeState]: A[x], B[], C[], D[], E[]
    #     """ (Re)initializes the navigation parameters (current navigation index, history of retrieved indexes,
    #     current continuity,...)."""
    #     self.history_and_taboos = [0] * (len(self.sequence))
    #     self.current_continuity = -1
    #     self.current_position_in_sequence = -1
    #     self.current_navigation_index = - 1
    #     self._forbid_indexes([len(self.labels) - 1])

    # TODO[B]: Why are those two so different?
    def clear(self):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """ (Re)initializes the navigation parameters (current navigation index, history of retrieved indexes,
        current continuity,...). """
        # self.history_and_taboos = [None] + [0] * (len(self.sequence) - 1)   # TODO[A] Breaking change, old here
        self.history_and_taboos = [None] + [0] * len(self.sequence)
        self.current_continuity = 0
        self.current_position_in_sequence = -1
        self.current_navigation_index = - 1
        self.no_empty_event = True

    def learn_sequence(self, sequence: List[MemoryEvent], equiv: Optional[Callable] = None):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Learns (appends) a new sequence in the model.

        :param sequence: sequence learnt in the Factor Oracle automaton
        :type sequence: list or str
        # :param labels: sequence of labels chosen to describe the sequence
        # :type labels: list or str
        :param equiv: Compararison function given as a lambda function, default if no parameter is given: self.equiv.
        :type equiv: function

        :!: **equiv** has to be consistent with the type of the elements in labels.

        """
        if equiv is None:
            equiv = self.equiv

        for event in sequence:
            self.learn_event(event, equiv)

    def learn_event(self, event: MemoryEvent, equiv: Callable = None):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        if equiv is None:
            equiv = self.equiv

        # TODO : TEST TO AVOID "UNDEF"
        current_last_idx = len(self.history_and_taboos) - 1
        self._authorize_indexes([current_last_idx])
        self.history_and_taboos.append(None)

    def filter_using_history_and_taboos(self, candidates: List[Candidate]) -> List[Candidate]:
        # FIXME[MergeState]: A[], B[], C[], D[], E[]
        # TODO[A2] This one probably has to remain public until filtering is moved to GH
        filtered_list = [c for c in candidates
                         if (not (self.history_and_taboos[c.index] is None)
                             and (self.avoid_repetitions_mode < 2 or self.avoid_repetitions_mode >= 2
                                  and self.history_and_taboos[c.index] == 0))]
        # print("Possible next indexes = {}, filtered list = {}".format(list_of_indexes, filtered_list))
        return filtered_list

    ################################################################################################################
    #   PRIVATE
    ################################################################################################################

    def _record_execution_trace(self, index_in_navigation):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Stores in :attr:`self.execution_trace` the values of different parameters of the model when generating the
        event in the sequence at the index given in argument.

        :param index_in_navigation:
        :type index_in_navigation: int

        :see also: The list of the parameters of the model whose values are stored in the execution trace is defined
        in :attr:`self.execution_trace_parameters`.

        """
        trace_index = {}
        for name_slot in self.execution_trace_parameters:
            # trace_index[name_slot] = copy.deepcopy(self.__dict__[name_slot])
            trace_index[name_slot] = deepcopy(self.__dict__[name_slot])

        self.execution_trace[index_in_navigation] = trace_index

    def _follow_continuation_using_transition(self, candidates: List[Candidate],
                                              direct_transitions: Dict[int, Tuple[Label, int]]) -> List[Candidate]:
        # FIXME[MergeState]: A[], B[], C[], D[], E[]
        # TODO[A] This should return a list of candidates (that for stage A1 may be of length 1)
        """
        Continuation using direct transition from self.current_position_in_sequence.

        In the method free_generation, this method is called with authorized_indexes = possible continuations
        filtered to satisfy the constraints of taboos and repetitions.
        In the method simply_guided_generation, this method is called with authorized_indexes = possible continuations
        **matching the required label** filtered to satisfy the constraints of taboos and repetitions.

        # :param authorized_indexes: list of authorized indexes to filter taboos, repetitions, and label when needed.
        # :type authorized_indexes: list(int)
        :return: index of the state
        :rtype: int

        """

        direct_transition: Optional[Tuple[Label, int]] = direct_transitions.get(self.current_position_in_sequence)

        if direct_transition is not None and self.current_continuity < self.max_continuity:
            # TODO[B]: Assign a value to a match instead of returning it directly
            return [candidate for candidate in candidates if candidate.index == direct_transition[1]]
        return []

    def _continuations_with_jump(self, candidates: List[Candidate],
                                 direct_transitions: Dict[int, Tuple[Label, int]]) -> List[Candidate]:
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        List of continuations with jumps to indexes with similar contexts direct transition from
        self.current_position_in_sequence.

        In the method free_generation, this method is called with authorized_indexes = possible continuations filtered
        to satisfy the constraints of taboos and repetitions.
        In the method simply_guided_generation, this method is called with authorized_indexes = possible continuations
        **matching the required label** filtered to satisfy the constraints of taboos and repetitions.

        # :param authorized_indexes: list of authorized indexes to filter taboos, repetitions, and label when needed.
        # :type authorized_indexes: list(int)
        :return: indexes of the states
        :rtype: list(int)

        """
        direct_transition: Optional[Tuple[Label, int]] = direct_transitions.get(self.current_position_in_sequence)

        if direct_transition:
            # TODO[C]: Note! This step is not compatible the idea of a list of candidates as it will actually remove
            #          the candidate selected in the previous step (_follow_continuation_using_transition)
            candidates = [c for c in candidates if candidates.index != direct_transition[1]]

        if len(candidates) > 0:
            if self.avoid_repetitions_mode > 0:
                print(f"\nTrying to avoid repetitions: possible continuations {[c.index for c in candidates]}...")
                # TODO[D]: This nested list comprehension could be optimized
                minimum_history_taboo_value: int = min([self.history_and_taboos[ch.index] for ch in candidates],
                                                       key=noneIsInfinite)
                candidates = [c for c in candidates if self.history_and_taboos[c.index] == minimum_history_taboo_value]
                print(f"... reduced to {[c.index for c in candidates]}.")

        return candidates

    # TODO : autres modes que random choice
    def _follow_continuation_with_jump(self, candidates: List[Candidate],
                                       direct_transitions: Dict[int, Tuple[Label, int]]) -> List[Candidate]:
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Random selection of a continuation with jump to indexes with similar contexts direct transition from
        self.current_position_in_sequence.

        In the method free_generation, this method is called with authorized_indexes = possible continuations filtered
        to satisfy the constraints of taboos and repetitions.
        In the method simply_guided_generation, this method is called with authorized_indexes = possible continuations
        **matching the required label** filtered to satisfy the constraints of taboos and repetitions.

        # :param authorized_indexes: list of authorized indexes to filter taboos, repetitions, and label when needed.
        # :type authorized_indexes: list(int)
        :return: index of the state
        :rtype: int

        """
        candidates = self._continuations_with_jump(candidates, direct_transitions)
        if len(candidates) > 0:
            # TODO[B]: Migrate this choice to top level
            random_choice: int = random.randint(0, len(candidates) - 1)
            return [candidates[random_choice]]
        return []

    def _update_history_and_taboos(self, index_in_sequence):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Increases the value associated to the index given in argument in :attr:`self.history_and_taboos`.
        Handles the taboos linked to :attr:`self.max_continuity`.

        :param index_in_sequence:
        :type index_in_sequence: int


        """
        # print("Record history_and_taboos for index {} in sequence.\nPREVIOUSLY:\n{}".format(index_in_sequence,
        #                                                                                     self.history_and_taboos))
        if not self.history_and_taboos[index_in_sequence] is None:
            self.history_and_taboos[index_in_sequence] += 1
        # print("Increases history of selected index.\nNew self.history_and_taboos = {}".format(self.history_and_taboos))
        previous_continuity = None
        previous_position_in_sequence = None
        previous_previous_continuity_in_sequence = None

        if self.current_navigation_index > 0:
            previous_continuity = self.execution_trace[self.current_navigation_index - 1]["current_continuity"]
            # print("Current continuity = {}, previous continuity = {}".format(self.current_continuity, previous_continuity))
            previous_position_in_sequence = self.execution_trace[self.current_navigation_index - 1][
                "current_position_in_sequence"]
            # print("Previous position in sequence = {}".format(previous_position_in_sequence))
            if self.current_navigation_index > 1:
                previous_previous_continuity_in_sequence = self.execution_trace[self.current_navigation_index - 2][
                    "current_continuity"]

        if self.current_continuity == self.max_continuity - 1 and self.current_position_in_sequence + 1 < self.index_last_state():
            self._forbid_indexes([self.current_position_in_sequence + 1])
        # print("Continuity reaches (self.max_continuity - 1). \n"
        #       "New self.history_and_taboos = {}".format(self.history_and_taboos))

        elif not previous_previous_continuity_in_sequence is None \
                and self.current_continuity == 0 \
                and not previous_position_in_sequence is None \
                and previous_position_in_sequence < self.index_last_state() \
                and not previous_continuity is None:  # and previous_continuity > 0:
            self.history_and_taboos[previous_position_in_sequence + 1] = previous_previous_continuity_in_sequence
        # print("Delete taboo set because of max_continuity at last step. \n"
        #       "New self.history_and_taboos = {}".format(self.history_and_taboos))

    def _forbid_indexes(self, indexes):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Introduces "taboos" (events that cannot be retrieved) in the navigation mechanisms.

        :param indexes: indexes of forbidden indexes (/!\ depending on the model the first event can be at index 0 or 1).
        :type indexes: list(int)

        """
        for i in indexes:
            self.history_and_taboos[i] = None

    def _authorize_indexes(self, indexes):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Delete the "taboos" (events that cannot be retrieved) in the navigation mechanisms for the states listed in
        the parameter indexes.

        :param indexes: indexes of authorized indexes (/!\ depending on the model the first event can be at index 0 or 1).
        :type indexes: list(int)

        """
        for i in indexes:
            self.history_and_taboos[i] = 0

    def _is_taboo(self, index):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        return self.history_and_taboos[index] is None

    def _delete_taboos(self):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """
        Delete all the "taboos" (events that cannot be retrieved) in the navigation mechanisms.
        """
        s = []
        for i in range(len(self.sequence)):
            if self._is_taboo(i):
                s.append(i)
        self._authorize_indexes(s)

    def find_matching_label_without_continuation(self, required_label: Label, candidates: List[Candidate],
                                                 equiv: Optional[Callable] = None) -> List[Candidate]:
        # FIXME[MergeState]: A[], B[], C[], D[], E[]
        # TODO[A]: This should probably return a list of candidates
        """
        Random state in the sequence matching required_label if self.no_empty_event is True (else None).

        :param required_label: label to read
        # :param authorized_indexes: list of authorized indexes to filter taboos, repetitions, and label when needed.
        # :type authorized_indexes: list(int)
        :param equiv: Compararison function given as a lambda function, default: self.equiv.
        :type equiv: function
        :return: index of the state
        :rtype: int

        :!: **equiv** has to be consistent with the type of the elements in labels.

        """
        if equiv is None:
            equiv = self.equiv

        if self.no_empty_event:
            candidates = [c for c in candidates if equiv(c.event.label(), required_label)]
            if len(candidates) > 0:
                random_choice: int = random.randint(0, len(candidates) - 1)
                return [candidates[random_choice]]
        return []

    ################################################################################################################
    #   LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY LEGACY   #
    ################################################################################################################

    def choose_prefix_from_list(self, index_delta_prefixes, pattern=()):
        # TODO[A1] This needs to be stereotyped and return a list of candidates (which may be of length 1)
        s = None
        t = 0
        length_selected_prefix = None
        # print("*¨*¨*¨*¨*¨*¨*¨")
        # print(index_delta_prefixes)
        if len(index_delta_prefixes.keys()) > 0:
            # TODO : MAX PAS FORCEMENT BONNE IDEE
            # length_selected_prefix = index_delta_prefixes.keys()[random.randint(0, len(index_delta_prefixes.keys())-1)]

            max_length = max(index_delta_prefixes.keys())
            # print(max_length)
            # accepted_lengths = [l for l in index_delta_prefixes.keys() if l > int(0.33*max_length)]
            # print(accepted_lengths)
            # length_selected_prefix = accepted_lengths[random.randint(0,len(accepted_lengths)-1)]
            # print(length_selected_prefix)
            # s = index_delta_prefixes[length_selected_prefix][random.randint(0, len(index_delta_prefixes[length_selected_prefix])-1)]
            # print(s)

            length_selected_prefix = max(index_delta_prefixes.keys())
            s = index_delta_prefixes[length_selected_prefix][
                random.randint(0, len(index_delta_prefixes[length_selected_prefix]) - 1)]
            if type(s) == list:
                t = s[1]
                s = s[0]
        else:
            print("No prefix found")

        return s, t, length_selected_prefix

    def index_last_state(self):
        # FIXME[MergeState]: A[x], B[], C[], D[], E[]
        """ Index of the last state in the model."""
        return len(self.labels) - 1

    def set_current_position_in_sequence_with_sideeffects(self, val_attr: Optional[int]):
        self.current_position_in_sequence = val_attr
        if val_attr is not None and val_attr > -1:
            self.current_navigation_index += 1
            print("\nNEW POSITION IN SEQUENCE: {}".format(val_attr))
            print("NEW NAVIGATION INDEX: {}".format(self.current_navigation_index))
            print("OLD LEN EXECUTION TRACE: {}".format(len(self.execution_trace)))

            if self.current_navigation_index > 0 and val_attr == \
                    self.execution_trace[self.current_navigation_index - 1]["current_position_in_sequence"] + 1:
                self.current_continuity += 1
                print("Continuity + 1 = {}".format(self.current_continuity))
            else:
                self.current_continuity = 0
                print("Continuity set to 0")

            self._update_history_and_taboos(val_attr)
            self._record_execution_trace(self.current_navigation_index)
            print("NEW LEN EXECUTION TRACE: {}".format(len(self.execution_trace)))
        # print("NEW EXECUTION TRACE: {}".format(self.execution_trace))
