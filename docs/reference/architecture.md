# Simplified Architecture

```mermaid
classDiagram
    class AbstractAlgorithm {
        +software : AbstractSoftware
        +stop : dict~str, any~
        -create_edit()
        -evaluate_variant()
        +run()
    }

    class AbstractEdit {
        +data : list~any~
        +target : tuple~str, str, any~
        +apply()
        +auto_create()$
    }

    class AbstractFitness {
        +process_compile_exec()
        +process_init_exec()
        +process_run_exec()
        +process_setup_exec()
        +process_test_exec()
    }

    class AbstractModel {
        -contents : dict~str, dict~str, any~~
        +filename : str
        +locations : dict~str, dict~str, list~any~~~
        +readonly : bool
        +random_target()
        +write_to_file()
    }

    class AbstractSoftware {
        -fitness_objectives : list~AbstractFitness~
        +ingredient_files : list~str~
        +path : Path
        +noop_variant : AbstractVariant
        +target_files : list~str~
        -work_dir : Path
        +evaluate_variant()
        +exec_cmd()
        -sync_folder()
        -write_variant()
    }

    class AbstractVariant {
        +diff : str
        +models : Dict~str, AbstractModel~
        +patch : Patch
        +random_model()
    }

    class ExecResult {
        +cmd : str
        +return_code : int
        +stdout : bstr
        +stderr :bstr
    }

    class Patch {
        +edits : list~AbstractEdit~
        +apply()
    }

    class RunResult {
        +variant : AbstractVariant
        +fitness : list~double~
        +cache : dict~str, ExecResult~
    }

    class SearchProtocol {
        +search : AbstractAlgorithm
        +software : AbstractSoftware
        +cleanup()
        +report()
        +run()
        +setup()
    }

    %% compositions
    AbstractSoftware *-- AbstractFitness : fitness_objectives
    AbstractSoftware *-- AbstractVariant : noop_variant
    AbstractVariant *-- AbstractModel : models
    RunResult *-- ExecResult : cache

    %% aggregations
    Patch o-- AbstractEdit : edits

    %% associations
    AbstractAlgorithm --> AbstractSoftware : software
    AbstractVariant --> Patch : patch
    RunResult --> AbstractVariant : variant
    SearchProtocol --> AbstractAlgorithm : search
    SearchProtocol --> AbstractSoftware : software

    %% links

    %% dependencies
    AbstractAlgorithm ..> AbstractEdit : create_edit()
    AbstractAlgorithm ..> AbstractVariant : run()
    AbstractAlgorithm ..> Patch : run()
    AbstractFitness ..> ExecResult : process_()
    AbstractSoftware ..> AbstractVariant : evaluate_variant()
    AbstractSoftware ..> RunResult : exec_cmd()
```

# Search Evaluation Pipeline

```mermaid
flowchart
  Algorithm -->|investigates| Patch
  Algorithm -->|creates| Edit["Edit(s)"]
  Edit -->|collected into| Patch
  Patch -->|realised into| Variant
  Edit -.->|modifies| Model["Model(s)"]
  Model -.->|collected into| Variant
  Variant -->|evaluated into| RunResult
  Variant -.->|evaluated by| Software
  Software -.->|to obtain| ExecResult["ExecResult(s)"]
  ExecResult -.->|interpreted by| Fitness["Fitness(s)"]
  Fitness -.->|stored into| RunResult
  RunResult -->|consumed by| Algorithm
```