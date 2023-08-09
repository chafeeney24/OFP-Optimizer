import pandas as pd
from ortools.sat.python import cp_model


def process_csv(csv_file, optimize_column=None, locked_golfers=None):
    # Load the data
    data = pd.read_csv(csv_file)
    data.columns = data.columns.str.strip()

    # Determine the values to optimize
    if optimize_column:
        values = [float(value) if isinstance(value, str) else float(value) for value in data[optimize_column].tolist()]
    else:
        values = [float(value.replace(',', '').replace('$', '')) if isinstance(value, str) else float(value) for value
                  in data['$/Event'].tolist()]

    owgr_values = [int(float(value)) for value in data['OWGR'].tolist()]

    # Create the model
    model = cp_model.CpModel()

    # Create a variable for each golfer
    x = [model.NewBoolVar(golfer) for golfer in data['Golfer']]

    # Constraint: Total OWGR <= 30
    model.Add(sum(x[i] * owgr_values[i] for i in range(len(x))) <= 30)

    # Constraint: Select up to 10 golfers
    model.Add(sum(x) <= 10)

    # Constraint: Select at least 1 golfer
    model.Add(sum(x) >= 8)

    # Constraint: Lock in specified golfers
    # Constraint: Lock in specified golfers
    if locked_golfers:
        golfer_list = [g.strip() for g in data['Golfer'].tolist()]  # Stripping whitespace
        for golfer in locked_golfers:
            if golfer in golfer_list:
                golfer_index = golfer_list.index(golfer)
                model.Add(x[golfer_index] == 1)
            else:
                print(f"Warning: Golfer '{golfer}' not found in the CSV file.")

    # Objective: Minimize the specified column if optimizing for odds, otherwise maximize
    if optimize_column:
        model.Minimize(sum(x[i] * values[i] for i in range(len(x))))
    else:
        model.Maximize(sum(x[i] * values[i] for i in range(len(x))))

    # Create the solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print(f"Results for file: {csv_file}")
    if status == cp_model.OPTIMAL:
        print('Total value =', solver.ObjectiveValue())
        print('Selected golfers:')
        for i in range(len(x)):
            if solver.Value(x[i]) == 1:
                print(data['Golfer'].iloc[i])
    else:
        print('No solution found!')
    print("\n" + "=" * 50 + "\n")


locked_golfers = ['Jon Rahm', 'Sepp Straka']
# Example usage
csv_files = [
    'Last10All-StJude.csv',
    'Last10Str.csv',
    'Last15All.csv',
    'Last25All.csv',
    'Majors23.csv'
]

for file_path in csv_files:
    process_csv(file_path, locked_golfers=locked_golfers)  # For the original CSV format

# For the new CSV format with odds
process_csv('DKOdds.csv', 'Winner', locked_golfers=locked_golfers)
process_csv('DKOdds.csv', 'Top 5', locked_golfers=locked_golfers)
process_csv('DKOdds.csv', 'Top 10', locked_golfers=locked_golfers)
