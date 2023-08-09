import pandas as pd


def process_csv(file_path):
    # Load the data
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()

    values = [float(value.replace(',', '').replace('$', '')) if isinstance(value, str) else float(value) for value in
              data['$/Event'].tolist()]
    owgr_values = [int(float(value)) for value in data['OWGR'].tolist()]

    from ortools.sat.python import cp_model

    # Create the model
    model = cp_model.CpModel()

    # Create a variable for each golfer
    x = [model.NewBoolVar(golfer) for golfer in data['Golfer']]

    # Constraint: Total OWGR <= 30
    model.Add(sum(x[i] * owgr_values[i] for i in range(len(x))) <= 30)

    # Constraint: Select up to 10 golfers
    model.Add(sum(x) <= 10)

    # Objective: Maximize $/Event
    model.Maximize(sum(x[i] * values[i] for i in range(len(x))))

    # Create the solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print(f"Results for file: {file_path}")
    if status == cp_model.OPTIMAL:
        print('Total value =', solver.ObjectiveValue())
        print('Selected golfers:')
        for i in range(len(x)):
            if solver.Value(x[i]) == 1:
                print(data['Golfer'].iloc[i])
    else:
        print('No solution found!')
    print("\n" + "=" * 50 + "\n")

csv_files = [
    'Last10All-StJude.csv',
    'Last10Str.csv',
    'Last25All.csv',
    'Majors23.csv'
]

for file_path in csv_files:
    process_csv(file_path)

