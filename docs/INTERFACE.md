# Core classes

## Algorithm
```
software # Prococol
report   # Protocol
reset()  #
run()    # Protocol
```

## Edit
```
target        # Patch
data          # Patch
auto_create() # Algorithm
apply()       # Patch
```

## EvalCache
```
config   #
reset()  # Algorithm
setup()  # Algorithm
get()    # Algorithm
update() # Algorithm
```

## Model
```
filename           # bin
renamed_filename   # Fitness, Variant
locations          # bin
locations_names    # bin
cached_dump        # Software
readonly           # Variant
init_contents()    # Variant
init_other()       # Variant
dump()             # Software, Variant
write_to_file()    # Software
random_target()    # Edit
update_cli()       # Variant
show_location()    # bin
```

## Protocol
```
config    # bin
setup()   # bin
run()     # bin
report()  # bin
cleanup() # bin
```

## Software
```
config             # Model
logger             # Algorithm, Protocol
path               # Variant
target_files       # Variant
ingredient_files   # Variant
noop_variant       # Algorithm, Variant
model_config       # Model
model_rules        # Variant
run_label          # Protocol
evaluate_variant() # Algorithm
write_variant()    # bin
add_to_env()       # Algorithm
clean_work_dir()   # Protocol, bin
```

## Variant
```
models         # Edit, Fitness, Software, bin
patch          # Algorithm
diff           # Algorithm, Protocol, bin
cli()          # Software
random_model() # Edit
```
