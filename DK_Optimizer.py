import pandas as pd
from ortools.sat.python import cp_model


def process_dk_csv(csv_file, locked_golfers=None, total_golfers=10):
    # Load the data
    data = pd.read_csv(csv_file)
    data.columns = data.columns.str.strip()
    print(data['OWGR'].iloc[11])

    # Sort locked_golfers by index in descending order
    locked_golfers_sorted = sorted(locked_golfers,
                                   key=lambda golfer: data.index[data['Golfer'].str.strip() == golfer.strip()].tolist()[
                                       0],
                                   reverse=True)

    # Handle locked golfers
    locked_owgr = 0
    locked_dk_value = 0
    num_locked = 0
    if locked_golfers:
        for golfer in locked_golfers_sorted:
            golfer_indices = data.index[data['Golfer'].str.strip() == golfer.strip()].tolist()
            if golfer_indices:
                golfer_index = golfer_indices[0]
                locked_owgr += int(round(float(data['OWGR'].iloc[golfer_index]) * 100))
                print(locked_owgr)
                locked_dk_value += int(data['DK'].iloc[golfer_index])
                num_locked += 1
                data.drop(golfer_index, inplace=True)  # Remove locked golfer from data
            else:
                print(f"Warning: Golfer '{golfer}' not found in the CSV file.")
        data.reset_index(drop=True, inplace=True)  # Reset the index after dropping rows

    free_picks = total_golfers - num_locked
    free_owgr = 3000 - locked_owgr

    values = data['DK'].tolist()
    owgr_values = [int(float(value) * 100) for value in data['OWGR'].tolist()]

    # Debugging information
    print("Locked OWGR:", locked_owgr)
    print("Free OWGR:", free_owgr)
    print("Locked DK value:", locked_dk_value)
    print("Free picks:", free_picks)

    # Create the model
    model = cp_model.CpModel()

    # Create a variable for each golfer
    x = [model.NewBoolVar(golfer) for golfer in data['Golfer']]

    # Constraint: Total OWGR <= (3000 - locked_owgr)
    model.Add(sum(x[i] * owgr_values[i] for i in range(len(x))) <= free_owgr)

    # Constraint: Select up to (10 - num_locked) golfers
    model.Add(sum(x) <= free_picks)

    # Objective: Maximize DK value (including locked golfers)
    model.Maximize(sum(x[i] * values[i] for i in range(len(x))) + locked_dk_value)

    # Create the solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print(f"Results for file: {csv_file}")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Total value =', solver.ObjectiveValue())
        print('Locked golfers:')
        for i in range(len(locked_golfers)):
            print(locked_golfers[i])

        print('Selected golfers:')
        selected_owgr = 0
        for i in range(len(x)):
            if solver.Value(x[i]) == 1:
                print(data['Golfer'].iloc[i], data['OWGR'].iloc[i])
                selected_owgr += int(float(data['OWGR'].iloc[i]) * 100)
        print("Total OWGR (including locked):", selected_owgr + locked_owgr)
    else:
        print('No solution found!')
    print("\n" + "=" * 50 + "\n")


# Add the names of the golfers you want  to lock
locked_golfers = ['Tyrrell Hatton', 'Sam Burns', 'Jon Rahm', 'Sepp Straka', 'Wyndham Clark']

csv_files = ['DK_prices.csv']

for file_path in csv_files:
    process_dk_csv(file_path, locked_golfers, 10)
