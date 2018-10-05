.. DYCI2 documentation master file, created by
   sphinx-quickstart on Fri Feb 24 16:11:35 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DYCI2's documentation
=================================

.. toctree::
   :caption: Table of Contents
   :name: mastertoc
   :numbered:


**Introduction**
===================

This version of the *DYCI2 library* is the first release of a work in progress: a set of models and tools for creative generation of sequences (and in particular musical sequences) from models of sequences. It implements several models, generative heuristics, time management strategies, and architectures of interactive agents.

Repository: https://forge.ircam.fr/p/DYCI2_library/

DYCI2 ("Creative Dynamics of Improvised Interaction") is a collaborative research and development project funded by the French National Research Agency (ANR). It explores the creative dynamics of improvised interactions between human and artificial agents, featuring an informed artificial listening scheme, a musical structure discovery and learning scheme, and a generalized interaction / knowledge / decision dynamics scheme (see http://repmus.ircam.fr/dyci2/home). The *DYCI2 library* is part of the DYCI2 project, it is conceived as an autonomous and easily extensible Python library, and can also be used in association with audio or midi listeners and renderers to form *DYCI2 agents* (see directory *"MaxPatches"*).

More information on the project: refer to **Nika, Déguernel, Chemla--Romeu-Santos, Vincent, Assayag, "DYCI2 agents: merging the "free", "reactive", and "scenario-based" music generation paradigms", in Proceedings of International Computer Music Conference 2017** (https://hal.archives-ouvertes.fr/hal-01583089/document) (please mention this paper to mention the library).

To use the library: see the tutorials in the root directory.

In this version:
   * Definitive architecture of the library: classes Model, Navigator, MetaModelNavigator, Query, Generator, GenerationHandler, and OSCAgent.
   * *Models*: Naive sequence navigation, Factor Oracle automaton.
   * *Associated navigation strategies*: free generation ("Omax-like"), single target generation, scenario-based generation ("ImproteK-like").
   * *Architectures of generative agent*: Generator and GenerationHandler (see doc), demand-driven generative agents processing queries expressed in "events". The (short-term and long-term) queries communicate through a shared execution trace to maintain consistency of the generated sequence when rewriting previously generated anticipations. 
   * *Communication*: OSC agents embedding the generative agents.
   * *Alphabets*: Generic list labels, Chord Labels.
   * *Documentation*: modules Model, Navigator, PrefixIndexing, MetaModelNavigator, Generator, GeneratorBuilder.
   * *Tutorials*: FactorOracle, PrefixIndexing, Intervals, MetaModelNavigator, FactorOracleNavigator, Generator, GenerationHandler, Tutorial "Text OSCAgent", Tutorials "Audio OSCAgent".

Next steps: 
   * *Models*: N-gram.
   * *Associated navigation strategies*: Navigator including a notion of "activity profile", free generation and single target generation using this navigator  ("Somax-like").
   * *Architectures of generative agent*: "Algebra" of queries, queries expressed in "ms". output of the queries not directly outputted but redirected to a choice method that will be in charge of outputting the result --> new playing modes "hard hybrid guidance" (long-term queries > short-term queries) and "soft hybrid guidance" (short-term queries > long-term queries).
   * *Alphabets*: Class "Content".
   * *Documentation*: modules Label, Transforms, Intervals, ParseAnnotationFiles, CorpusBuilder, OSCAgent, Audiotools.
   * *Tutorials*: GeneratorBuilder, OSCAgent_Tutorial_3 (midi), AudioTools, ParseAnnotationFiles.


**Overview**
===================

.. inheritance-diagram:: Model.FactorOracle
   :parts: 1 
   :caption: :class:`~Model.Model` is an abstract class. Any new model of sequence must inherit from this class. The classes inheriting from this class are minimal and only implement the construction algorithms and basic methods. Navigation and creative aspects are handled by the classes introduced below. Models of sequence implemented so far: Factor Oracle Automaton (:class:`~Model.FactorOracle`).

.. inheritance-diagram:: Navigator.Navigator
   :parts: 1
   :caption: The class :class:`~Navigator.Navigator` implements parameters and methods that are used to navigate through a model of sequence. These parameters and methods are **model-independent**. This class defines in particular the naive versions of the methods :meth:`~Navigator.Navigator.simply_guided_generation` and :meth:`~Navigator.Navigator.free_generation` handling the navigation through a sequence when it is respectively guided by target labels and free. These methods are overloaded by model-dependant versions (and other model-dependent parameters or methods can be added) when creating a **model navigator** class (cf. below).

.. inheritance-diagram:: MetaModelNavigator.MetaModelNavigator
   :parts: 1 
   :caption: :class:`~MetaModelNavigator.MetaModelNavigator` is a **metaclass**. A new class created using this metaclass is a **model navigator** and inherits from: **1)** a class inheriting from :class:`~Model.Model`, **2)** a class inheriting from :class:`~Navigator.Navigator`. A **model navigator** implements the different algorithms, strategies, and heuristics to navigate through a given model of sequence for analysis or creative applications, for example **generating new sequences using concatenative synthesis of events learned in the model**. The class :class:`~ModelNavigator.FactorOracleNavigator` introduced below is an example of model navigator created using this metaclass.

.. inheritance-diagram:: ModelNavigator.FactorOracleNavigator Model.FactorOracle
   :parts: 1 
   :caption: The class :class:`~ModelNavigator.FactorOracleNavigator` implements different algorithms, strategies, and heuristics to navigate through a Factor Oracle Automaton for creative applications. The creation of the class :class:`~ModelNavigator.FactorOracleNavigator` in the file :file:`ModelNavigator.py` gives an example of easy definition of a new class of model navigator using the metaclass :class:`~MetaModelNavigator.MetaModelNavigator`: 1) chose two bases (here, model = :class:`~Model.FactorOracle`, navigator = :class:`~Navigator.Navigator`), 2) define the methods to overload :meth:`~Navigator.Navigator.simply_guided_generation` and :meth:`~Navigator.Navigator.free_generation` (here :meth:`ModelNavigator.FactorOracleNavigator.simply_guided_navigation` and :meth:`ModelNavigator.FactorOracleNavigator.free_navigation`)
   
.. TODO    
.. .. inheritance-diagram:: Query.Query 
..    :parts: 1    
.. inheritance-diagram:: Generator.GenerationHandler 
   :parts: 1
   :caption: The class :class:`~Generator.Generator` embeds a **model navigator** (cf. metaclass :class:`~MetaModelNavigator.MetaModelNavigator`) as "memory" and processes **queries** (class :class:`~Query.Query`) to generate new sequences. This class uses pattern matching techniques (cf. :mod:`PrefixIndexing`) to enrich the navigation and generation methods offered by the chosen model. The class :class:`~Generator.GenerationHandler` introduces time management and planning for interactive applications and adds a pool of query, concurrency (e.g. processing of concurrent queries), etc. to the class :class:`~Generator.Generator`. 


.. inheritance-diagram:: OSCAgent.OSCAgent
   :parts: 1 
   :caption: The class :class:`~OSCAgent.Server` defines an OSC (http://opensoundcontrol.org) server to communicate with external applications. The class :class:`~OSCAgent.OSCAgent` defines a process embedding an instance of :class:`~Generator.GenerationHandler` and its own OSC sender, receiver, settings, etc. to receive queries and control parameters and send generation outputs. Both classes can be used in particular in association with a Max interface handling audio or midi rendering.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


**Models and navigation**
==========================

.. automodule:: Model
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: Navigator
   :members:
   :undoc-members:
   :show-inheritance:  

.. automodule:: MetaModelNavigator
   :members:
   :show-inheritance:

.. BELOW: "autoclass" for all the classes defined using MetaModelNavigator

Factor Oracle Navigator
-----------------------

.. autoclass:: ModelNavigator.FactorOracleNavigator
   :members:
   :show-inheritance:

**Handle generation**
======================

.. automodule:: Query
   :members:
   :undoc-members:
   :show-inheritance: 

.. automodule:: Generator
   :members:
   :undoc-members:
   :show-inheritance:

**Pattern matching algorithms**
================================

.. automodule:: PrefixIndexing
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:

.. LA DOC N'EST PAS FAITE. JUSTE POUR QUE LE MODULE SOIT VISIBLE ET DONNE LE LIEN VERS LE TUTO
.. .. automodule:: Intervals
..    :members:
..    :undoc-members:
..    :inherited-members:
..    :show-inheritance:
.. automodule:: Intervals
   :show-inheritance:

/!\ ...documentation in progress... /!\

**Event, Label, Transformation**
================================

.. LA DOC N'EST PAS FAITE. JUSTE POUR QUE LE MODULE SOIT VISIBLE
.. .. automodule:: Label
..    :members:
..    :show-inheritance: 
.. automodule:: Label
   :show-inheritance: 

/!\ ...documentation in progress... /!\

.. LA DOC N'EST PAS FAITE. JUSTE POUR QUE LE MODULE SOIT VISIBLE
.. .. automodule:: Transforms
..    :members:
..    :show-inheritance:
.. automodule:: Transforms
   :show-inheritance:

/!\ ...documentation in progress... /!\


**OSC communication**
======================


.. LA DOC N'EST PAS FAITE. JUSTE POUR QUE LE MODULE SOIT VISIBLE
.. .. automodule:: OSCAgent
..    :members:
..    :undoc-members:
..    :show-inheritance:
.. automodule:: OSCAgent
   :show-inheritance:

/!\ ...documentation in progress... /!\

Memory and corpus
==================

.. automodule:: GeneratorBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: ParseAnnotationFiles
   :members:
   :show-inheritance:
..    :undoc-members:

/!\ ...documentation in progress... /!\

.. .. automodule:: CorpusBuilder
..    :members:
..    :undoc-members:
..    :show-inheritance:













