import sys
from build_data import get_data


def execute_operations(data, operations_file):
    """Execute operations specified in the operations file on the dataset."""
    try:
        with open(operations_file, 'r') as file:
            operations = file.readlines()
    except FileNotFoundError:
        print(f"Error: Operations file '{operations_file}' not found.")
        sys.exit(1)

    for idx, line in enumerate(operations):
        line = line.strip()
        if not line:
            continue  # Skip blank lines

        try:
            # Parse operation
            parts = line.split(":")
            op = parts[0]

            # Handle each operation
            if op == "display":
                display(data)
            elif op == "filter-state":
                state = parts[1]
                data = filter_state(data, state)
            elif op == "filter-gt":
                field, value = parts[1], float(parts[2])
                data = filter_gt(data, field, value)
            elif op == "filter-lt":
                field, value = parts[1], float(parts[2])
                data = filter_lt(data, field, value)
            elif op == "population-total":
                population_total(data)
            elif op.startswith("population"):
                field = parts[1]
                population_field(data, field)
            elif op.startswith("percent"):
                field = parts[1]
                percent_field(data, field)
            else:
                raise ValueError("Unknown operation")

        except (ValueError, IndexError):
            print(f"Error: Malformed line {idx + 1}: {line}")
            continue

def display(data):
    """Print information about all counties in a readable format."""
    for entry in data:
        # Print county and state
        print(f"{entry.county}, {entry.state}")

        # Print Population
        print(f"        Population: {repr(entry.population.get('2014 Population', 'N/A'))}")

        # Print Age breakdown
        print("        Age:")
        print(f"               < 5: {repr(entry.age.get('< 5', 'N/A'))}%")
        print(f"               < 18: {repr(entry.age.get('< 18', 'N/A'))}%")
        print(f"               > 65: {repr(entry.age.get('> 65', 'N/A'))}%")

        # Print Education statistics
        print("        Education")
        print(f"                >= High School: {repr(entry.education.get('High School or Higher', 'N/A'))}%")
        print(f"                >= Bachelor's: {repr(entry.education.get('Bachelor\'s Degree or Higher', 'N/A'))}%")

        # Print Ethnicities breakdown
        print("        Ethnicity Percentages")
        print(f"                American Indian and Alaska Native: {repr(entry.ethnicities.get('American Indian and Alaska Native Alone', 'N/A'))}%")
        print(f"                Asian Alone: {repr(entry.ethnicities.get('Asian Alone', 'N/A'))}%")
        print(f"                Black Alone: {repr(entry.ethnicities.get('Black Alone', 'N/A'))}%")
        print(f"                Hispanic or Latino: {repr(entry.ethnicities.get('Hispanic or Latino', 'N/A'))}%")
        print(f"                Native Hawaiian and Other Pacific Islander Alone: {repr(entry.ethnicities.get('Native Hawaiian and Other Pacific Islander Alone', 'N/A'))}%")
        print(f"                Two or More Races: {repr(entry.ethnicities.get('Two or More Races', 'N/A'))}%")
        print(f"                White Alone: {repr(entry.ethnicities.get('White Alone', 'N/A'))}%")
        print(f"                White Alone, not Hispanic or Latino: {repr(entry.ethnicities.get('White Alone, not Hispanic or Latino', 'N/A'))}%")

        # Print Income statistics
        print("        Income")
        print(f"                Median Household: {repr(entry.income.get('Median Household Income', 'N/A'))}")
        print(f"                Per Capita: {repr(entry.income.get('Per Capita Income', 'N/A'))}")
        print(f"                Below Poverty Level: {repr(entry.income.get('Persons Below Poverty Level', 'N/A'))}%")

        print()



def filter_state(data, state):
    """Filter counties by state abbreviation."""
    filtered = [entry for entry in data if entry.state == state]
    print(f"Filter: state == {state} ({len(filtered)} entries)")
    return filtered


def filter_gt(data, field, value):
    """Filter counties where a field value is greater than the specified value."""
    filtered = [entry for entry in data if get_field_value(entry, field) > value]
    print(f"Filter: {field} gt {value} ({len(filtered)} entries)")
    return filtered


def filter_lt(data, field, value):
    """Filter counties where a field value is less than the specified value."""
    filtered = [entry for entry in data if get_field_value(entry, field) < value]
    print(f"Filter: {field} lt {value} ({len(filtered)} entries)")
    return filtered


def population_total(data):
    """Compute and print the total 2014 population across all counties."""
    total_population = sum(entry.population.get("2014 Population", 0) for entry in data)
    print(f"2014 population: {total_population}")


def population_field(data, field):
    """Compute and print the total sub-population for the specified field."""
    try:
        total_population = sum(entry.population.get("2014 Population", 0) for entry in data)
        sub_population = sum(
            entry.population.get("2014 Population", 0) * (get_field_value(entry, field) / 100)
            for entry in data
        )

        # Convert the sub_population to a string with the required precision, then strip trailing zeros
        sub_population_str = f"{sub_population:.15f}".rstrip('0').rstrip('.')
        print(f"2014 {field} population: {sub_population_str}")
    except ValueError as e:
        print(f"Error: {e}")


def percent_field(data, field):
    """Compute and print the percentage of the total population for a specified field."""
    try:
        total_population = sum(entry.population.get("2014 Population", 0) for entry in data)
        sub_population = sum(
            entry.population.get("2014 Population", 0) * (get_field_value(entry, field) / 100)
            for entry in data
        )
        if total_population > 0:
            percentage = (sub_population / total_population) * 100
            # Print percentage with full precision using repr()
            print(f"2014 {field} percentage: {repr(percentage)}")
        else:
            print(f"2014 {field} percentage: 0.000000")
    except ValueError as e:
        print(f"Error: {e}")


def get_field_value(entry, field):
    """Retrieve the value of a nested field from a CountyDemographics object."""
    parts = field.split(".")
    prefix = parts[0]  # The dictionary name (e.g., "Education")
    key = ".".join(parts[1:])  # The specific key within the dictionary (e.g., "Bachelor's Degree or Higher")

    # Map prefixes to attributes in the CountyDemographics object
    if prefix == "Education":
        return entry.education[key]
    elif prefix == "Ethnicities":
        return entry.ethnicities[key]
    elif prefix == "Income":
        return entry.income[key]
    elif prefix == "Population":
        return entry.population[key]
    else:
        raise ValueError(f"Field '{field}' not found in entry.")


def main():
    """Main function to load data and execute operations."""
    if len(sys.argv) < 2:
        print("Usage: python3 hw4.py <operations_file>")
        sys.exit(1)

    operations_file = sys.argv[1]

    # Load data from county demographics
    data = get_data()
    print(f"{len(data)} records loaded")  # No commas in the loaded records count

    # Execute operations
    execute_operations(data, operations_file)


if __name__ == "__main__":
    main()
