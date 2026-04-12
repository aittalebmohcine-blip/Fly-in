# To Do
- [ ] docstrings
- [ ] documentation
- [ ] understand the algorithm
- [x] flake8
- [x] mypy
- [x] parsing

- file permission

# Extracting

- colors provided => visual feedback (p10-colors)
  - what do they mean by visual feedback?
    - (p11-pathfinding) Visual Representation: Your implementation must provide visual feedback of the simulation, either through:
      - Colored terminal output showing drone movements and zone states
      - A graphical interface displaying the network and drone positions
      - Both options for enhanced user experience

      - what do they mean by deadlocks (p11-pathfinding)



# Fly-in Parser Testing Checklist

## 1. Initialization & File Structure
- [x] Reject empty files.
- [x] Reject files missing `nb_drones:` entirely.
- [x] Verify `nb_drones:` is strictly the first valid line (before any zone/connection).
- [x] Reject files with unknown prefixes or unrecognized line formats.
- [x] Verify handling of files with no connections or no intermediate hubs.

## 2. `nb_drones` Validation
- [x] Reject non-integer values (e.g., floats, strings, empty).
- [x] Reject zero or negative integers.
- [x] Reject missing value after colon (`nb_drones:`).
- [ ] Reject whitespace between key, colon, and value (`nb_drones : 5` or `nb_drones:  5` if strict).
- [x] Accept valid positive integers.

## 3. Zone Definition Syntax
- [x] Reject lines missing type prefix (`start_hub:`, `end_hub:`, `hub:`).
- [x] Reject misspelled or case-mismatched prefixes.
- [x] Reject zones missing name, X, or Y coordinate.
- [x] Reject coordinates that are not integers (floats, letters, symbols).
- [x] Reject zones with trailing metadata missing opening/closing brackets.
- [x] Reject lines with multiple metadata blocks or malformed bracket syntax.

## 4. Zone Names & Coordinates
- [x] Reject zone names containing dashes (`-`).
- [x] Reject zone names containing spaces.
- [x] Reject duplicate zone names across the entire file.
- [x] Verify coordinates are stored/parsed as exact integers.
- [x] Verify exactly one `start_hub:` exists in the file.
- [x] Verify exactly one `end_hub:` exists in the file.
- [x] Reject files with zero `start_hub:` or zero `end_hub:`.
- [x] Reject files with multiple `start_hub:` or `end_hub:`.

## 5. Zone Metadata Parsing
- [x] Accept missing metadata block and apply defaults (`zone=normal`, `max_drones=1`, `color` unspecified).
- [x] Accept metadata tags in any order inside brackets.
- [x] Reject invalid `zone=` values (must be strictly `normal`, `blocked`, `restricted`, or `priority`).
- [x] Reject `max_drones=` values that are not positive integers (`0`, negative, floats, strings).
- [ ] Reject `color=` values containing spaces or multiple words.
- [x] Reject unknown keys inside zone metadata brackets.
- [x] Reject malformed key-value pairs (missing `=`, missing value, missing spaces between tags).

## 6. Connection Syntax & References
- [x] Reject connections missing the `connection:` prefix.
- [x] Reject connections missing one or both zone names.
- [x] Reject connections referencing zones that were not previously defined.
- [x] Reject connections where a zone name contains a dash (subject explicitly forbids this).
- [x] Reject self-referencing connections (`connection: zone1-zone1`).
- [x] Reject duplicate connections (`a-b` followed by `a-b`).
- [x] Reject duplicate bidirectional connections (`a-b` followed by `b-a`).
- [x] Verify connections are parsed as bidirectional.

## 7. Connection Metadata & Integrity
- [x] Accept missing connection metadata and apply default (`max_link_capacity=1`).
- [x] Reject `max_link_capacity=` values that are not positive integers (`0`, negative, floats, strings).
- [x] Reject malformed connection metadata brackets.
- [x] Reject unknown keys inside connection metadata brackets.
- [ ] Verify metadata is correctly associated with the specific connection.

## 8. Comments & Whitespace Handling
- [x] Ignore lines starting with `#`.
- [x] Ignore completely empty lines anywhere in the file.
- [x] Verify correct parsing with leading/trailing whitespace on valid lines.
- [x] Verify correct parsing with multiple spaces between tokens.
- [x] Reject inline comments if not explicitly supported (subject states "Comments start with '#'").

## 9. Error Handling & Output Compliance
- [ ] Verify program terminates immediately on the first parsing error.
- [x] Verify error output is written to stderr (or clear console output) without a Python traceback/crash.
- [x] Verify every error message explicitly states the exact line number.
- [x] Verify every error message explicitly states the exact cause of failure.
- [x] Verify no partial state is processed or simulated after an error.

## 10. Valid Baseline Verification
- [x] Parse the provided example map successfully without warnings.
- [x] Verify all zone attributes (name, type, coords, metadata) match expected defaults/overrides.
- [x] Verify all connections are correctly linked and bidirectional.
- [x] Verify parsed graph structure matches logical expectation for downstream simulation.
