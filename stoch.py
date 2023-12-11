import graphviz


# element definition
class Element:
    def __init__(self, number, parents, mean_time, variance, children):
        self.number = number
        self.parents = parents
        self.mean_time = mean_time
        self.variance = variance
        self.children = children
        self.cv = (variance ** 0.5) / mean_time
        self.cv2 = variance / (mean_time ** 2)


# station definition
class Station:
    def __init__(self, station_no, elements, station_time, idle_time, probability, mean, var):
        self.station_no = station_no
        self.elements = elements
        self.station_time = station_time
        self.idle_time = idle_time
        self.probability = probability
        self.mean = mean
        self.var = var


elements = []
stations = []
availList = []
edict = dict()


# to create precedence diagram
def create_element_graph(elements, file_name):
    dot = graphviz.Digraph(format='png')

    # Inside the create_element_graph function
    for element in elements:
        dot.node(str(element.number), f"Element {element.number}\nmean time: {element.mean_time:.2f}", shape='ellipse')

    for element in elements:
        for parent in element.parents:
            dot.edge(str(parent), str(element.number))  # Add 'constraint' here

    dot.render(file_name, view=True)


def create_new_station(k, cycle_time):
    station = Station(len(stations) + 1, [], 0, cycle_time, 0.0, 0.0, 0.0)

    # Sort availList with increasing cv
    availList.sort(key=lambda element: element.cv)

    for element in availList:
        element_time = new_time(element, station, k)
        # element_time = element.mean_time + station_time + (station_time ** 0.5) * (element.variance ** 0.5)

        if element_time <= cycle_time:
            station.mean = element.mean_time
            station.var = element.variance
            # Add the element to the station
            station.elements.append(element.number)
            station.station_time = element_time
            availList.remove(element)

            child = edict[element.number].children
            for c in child:
                try:
                    edict[c].parents.remove(element.number)
                except:
                    pass

                if not edict[c].parents:
                    availList.append(edict[c])
            break

    stations.append(station)


def add_element(k, cycle_time):
    is_added = False
    station = stations[-1]

    # Sort availList with increasing cv
    availList.sort(key=lambda element: element.cv)

    cv2_l = []

    for element in availList:
        r = station.mean / element.mean_time
        new_cv2 = element.cv**2
        st_cv2 = (1+2*r)*(station.var/(station.mean**2))
        if new_cv2 < st_cv2:
            cv2_l.append(element)
    if not cv2_l:
        for element in availList:
            element_time = new_time(element, station, k)
            # element_time = element.mean_time + station_time + (station_time ** 0.5) * (element.variance ** 0.5)

            if element_time <= cycle_time:
                is_added = True
                station.mean += element.mean_time
                station.var += element.variance
                # Add the element to the station
                station.elements.append(element.number)
                station.station_time = element_time
                availList.remove(element)

                child = edict[element.number].children
                for c in child:
                    try:
                        edict[c].parents.remove(element.number)
                    except:
                        pass

                    if not edict[c].parents:
                        availList.append(edict[c])
                break
    else:
        for element in cv2_l:
            element_time = new_time(element, station, k)
            # element_time = element.mean_time + station_time + (station_time ** 0.5) * (element.variance ** 0.5)

            if element_time <= cycle_time:
                is_added = True
                station.mean += element.mean_time
                station.var += element.variance
                # Add the element to the station
                station.elements.append(element.number)
                station.station_time = element_time
                availList.remove(element)

                child = edict[element.number].children
                for c in child:
                    try:
                        edict[c].parents.remove(element.number)
                    except:
                        pass

                    if not edict[c].parents:
                        availList.append(edict[c])
                break

    return is_added


def new_time(element, station, k):
    m = element.mean_time
    var = element.variance
    for el in station.elements:
        m += edict[el].mean_time
        var += edict[el].variance

    ts = m + k * (var ** 0.5)
    return ts


def main():
    # input_file = input("Enter the name of the input file (e.g., input_data.txt):")

    try:
        with open('input_data.txt', 'r') as file:
            for line in file:
                elements_data = line.strip().split()
                number = int(elements_data[0])
                parent_data = elements_data[1]
                if parent_data == '0':
                    parents = []
                else:
                    parents = [int(p) for p in parent_data.split(',')]

                child_data = elements_data[2]
                if child_data == '0':
                    children = []
                else:
                    children = [int(c) for c in child_data.split(',')]

                mean_time = float(elements_data[3])
                variance = float(elements_data[4])
                element = Element(number, parents, mean_time, variance, children)
                edict[number] = element
                elements.append(element)
                if not parents:  # If the element has no parents, add it to availList
                    availList.append(element)
    except FileNotFoundError:
        print("File not found.")
        return

    cycle_time = float(input("Enter cycle time (C): "))
    max_probability = float(input("Enter the maximum probability (Pc): "))
    max_probability = max_probability / 100

    # Create a graph to visualize element relationships
    create_element_graph(elements, "element_graph")

    k = 1 / ((2 * max_probability) ** 0.5)

    while availList:
        if not stations:
            create_new_station(k, cycle_time)
        is_added = add_element(k, cycle_time)
        if not is_added:
            create_new_station(k, cycle_time)

    for station in stations:
        station.idle_time -= station.station_time

    print("Station no.\telements\ttime\tidle time")
    for station in stations:
        print(f"{station.station_no}\t{station.elements}\t{station.station_time}\t{station.idle_time}")

if __name__ == "__main__":
    main()
