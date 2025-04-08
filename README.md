# Class Scheduler Script

This Python script helps generate valid schedules based on available classes, session timings, and location constraints. It allows you to create and visualize schedules while ensuring that they adhere to certain rules, such as avoiding overlaps and ensuring enough time between sessions held in different locations.

## Requirements

* Python 3.x
* `matplotlib` library (for generating visual schedules)

To install the necessary library:

```bash
pip install matplotlib
```

## CSV File Format

The script expects a CSV file formatted as follows:

| name         | date1           | date2           | location   | credits |
| ------------ | --------------- | --------------- | ---------- | ------- |
| Class Name 1 | MON 08:00-10:00 | WED 10:00-12:00 | Building A | 3       |
| Class Name 2 | TUE 09:00-11:00 |                 | Building B | 4       |
| Class Name 3 | THU 13:00-15:00 | FRI 09:00-11:00 | Building C | 2       |
| ...          | ...             | ...             | ...        | ...     |

* `name`: The name of the class.
* `date1`: The first session time in the format `DAY HH:MM-HH:MM`.
* `date2`: The second session time (optional). If not applicable, leave it blank.
* `location`: The location where the class takes place.
* `credits`: The number of credits the class offers.

## Usage

To use the script, run the following command in your terminal:

```bash
python scheduler.py <CSV_FILE> <NUM_CLASSES> [OPTIONS]
```

### Example:

```bash
python scheduler.py realData.csv 4 --block MON FRI --include "Quantum information theory"
```

### Arguments:

* **`<CSV_FILE>`** : Path to the CSV file containing class information (as described above).
* **`<NUM_CLASSES>`** : The number of classes to include in each generated schedule.

### Flags:

* **`--block`** : Specify which days of the week to block (e.g., MON TUE). Classes will not be scheduled on these days.
  Example:

```bash
  --block MON FRI
```

* **`--include`** : Force the inclusion of certain class names in all generated schedules.
  Example:

```bash
  --include "Quantum information theory"
```

* **`--help`** : Show the help message with all available options.
  Example:

```bash
  python scheduler.py --help
```

### Output:

The script will:

1. Generate all valid schedules (based on the number of classes, blocked days, and any included classes).
2. Print each valid schedule to the console, listing the classes, their locations, and times.
3. Generate visual representations of each valid schedule and save them as images in a folder named `schedules/`.

---

## Customization & Fine-Tuning

You can modify the script to suit your needs by adjusting the following variables and functions.

### 1. **Allowed Time Overlap** (`allowed_overlap`)

By default, the script allows a maximum time overlap of 30 minutes between sessions. You can adjust this by changing the `allowed_overlap` variable in the `is_valid_schedule` function.

```python
allowed_overlap = 30  # Increase or decrease as needed
```

### 2. **Minimum Travel Gap** (`min_travel_gap`)

The script ensures that there is at least a 30-minute gap between sessions in different locations. You can change this value in the `is_valid_schedule` function.

```python
min_travel_gap = 30  # Modify for shorter/longer gaps
```

### 3. **CSV Parsing** (`load_classes`)

If your CSV file structure changes, you may need to adjust the `load_classes` function. It currently expects columns in the following order: `name`, `date1`, `date2`, `location`, `credits`.

```python
def load_classes(csv_file):
    # Custom CSV parsing code
```

### 4. **Visual Output Settings** (`draw_schedule`)

If you want to modify the appearance of the generated visual schedules (e.g., colors, font sizes, or grid layout), you can adjust the `draw_schedule` function.

```python
def draw_schedule(schedule, index, output_folder="schedules"):
    # Modify matplotlib code here to adjust visual output
```

### 5. **Valid Schedule Logic** (`is_valid_schedule`)

You can adjust the validation logic (e.g., constraints for session overlaps, location checks, or blocked days) in the `is_valid_schedule` function. If you have additional constraints, you can add them here.

```python
def is_valid_schedule(schedule, blocked_days, allowed_overlap=30, min_travel_gap=30):
    # Modify logic for valid schedule generation
```

## Important Notes

* The script does not currently account for class conflicts where multiple sessions might span over weekends or across non-standard hours. If your scheduling needs involve such scenarios, additional logic may be required.
* If the number of valid schedules generated is too large, consider narrowing down the parameters (e.g., by increasing the minimum number of credits or blocking more days).

---

## Example CSV for Testing:

```csv
name,date1,date2,location,credits
Mathematics,MON 08:00-10:00,WED 10:00-12:00,Building A,4
Physics,TUE 09:00-11:00,,Building B,3
Computer Science,THU 13:00-15:00,FRI 09:00-11:00,Building C,3
Quantum Information Theory,MON 10:00-12:00,,Building A,4
```

 **Command** :

```bash
python scheduler.py classes.csv 3 --block MON --include "Quantum Information Theory"
```
