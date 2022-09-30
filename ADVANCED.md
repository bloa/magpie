# How To

## Magpie's Scenario Configuration

### Change the Stopping Condition

Under the header `[search]` you may specify three types of stopping conditions.

- `max_iter` is the maximal number of evaluation allowed
- `max_time` is the maximum wallclock time allowed (in seconds)
- `target_fitness` makes Magpie immediately stop when an equal or lower fitness value is found.

### Configure the Warmup Mechanism

Under the header `[warmup]` you may specify the number of warm up evaluations using `n` (default: 3).
In addition, you also also modify how the base fitness value is selected, using the key `strategy` (default: last); possible strategies include `last`, `min`, `max`, `mean`, and `median`.


### Configure the Cache Mechanism
### Change the Output Size Limit
### Change the Diff Format
### Change the Log File Names

## Advanced

### Change the Search Algorithm
### Change the Mutation Operators
### Change the Fitness Function
### Provide the Evaluation Script in Python
### Provide an Alternative Budget

## Hooks

### Warmup
### Start
### Main Loop
### Evaluation
### End
