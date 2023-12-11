class Element:
    def __init__(self, number, parents, mean_time, variance, children):
        self.number = number
        self.parents = parents
        self.mean_time = mean_time
        self.variance = variance
        self.children = children
        self.cv = (variance ** 0.5) / mean_time
        self.cv2 = variance / (mean_time ** 2)

class Station:
    def __init__(self, station_no, elements, station_time, idle_time, probability):
        self.station_no = station_no
        self.elements = elements
        self.station_time = station_time
        self.idle_time = idle_time
        self.probability = probability

def create_station(availList, cycle_time):
    station_no = 1
    station_time = 0
    elements_in_station = []

    # Sort availList with increasing cv
    availList.sort(key=lambda element: element.cv)

    for element in availList:
        element_time = element.mean_time + station_time + (station_time ** 0.5) * (element.variance ** 0.5)

        if element_time <= cycle_time:
            # Add the element to the station
            elements_in_station.append(element)
            station_time += element_time
            availList.remove(element)

            # Add its children with no parents to availList
            for child_element in element.children:
                if all(parent_element not in elements_in_station for parent_element in child_element.parents):
                    availList.append(child_element)

    # Calculate idle time
    idle_time = cycle_time - station_time

    # Create a new station
    station = Station(station_no, elements_in_station, station_time, idle_time, 0.0)

    return station

def main():
    input_file = input("Enter the name of the input file (e.g., input_data.txt):")
    
    elements = []
    availList = []  # Create a new list for elements with no parents

    try:
        with open(input_file, 'r') as file:
            for line in file:
                elements_data = line.strip().split()
                number = int(elements_data[0])
                parent_data = elements_data[1]
                if parent_data == '0':
                    parents = []
                else:
                    parents = [int(p) for p in parent_data.split(',')]
                mean_time = float(elements_data[2])
                variance = float(elements_data[3])
                child_data = elements_data[4]
                if child_data == '0':
                    children = []
                else:
                    children = [int(c) for c in child_data.split(',')]
                element = Element(number, parents, mean_time, variance, children)
                elements.append(element)
                if not parents:  # If the element has no parents, add it to availList
                    availList.append(element)
    except FileNotFoundError:
        print(f"File '{input_file}' not found.")
        return

    cycle_time = float(input("Enter cycle time (C): "))
    max_probability = float(input("Enter the maximum probability (Pc): "))

    # Create a station
    station = create_station(availList, cycle_time)

    # Print the station details
    print("Station No:", station.station_no)
    print("Elements in Station:")
    for element in station.elements:
        print(f"- Element No: {element.number}, Parents: {element.parents}, Mean Time: {element.mean_time}, Variance: {element.variance}")
    print("Station Time:", station.station_time)
    print("Idle Time:", station.idle_time)
    print("Max Probability (Pc):", station.probability)

if __name__ == "__main__":
    main()
