import csv
import json

# TODO: Run simulations, and pick cases based on the following
# 1. Whether I would lose a supply centre
# 2. Whether the attacker would lose a supply centre in that same turn
# 3. Whether I would gain a supply centre, without losing one.

# Need to limit Armies and Fleets
# Possibly the hardest parts of this will be support and convoy.


positions = []
current = {}
pieces = []
convoys = []
aconvoys = []
supports = []
movements = []
holds = []
n = 1

class piece:
    def __init__(self, unit_type, country, position):
        global n
        self.unit_type = unit_type
        self.country = country
        self.position = position
        self.nodes = []
        self.id = n
        n += 1
        self.possible_moves()

    def possible_moves(self):
        utype = self.unit_type
        position = self.position
        with open("nodes.csv", 'r') as f:
            reader = csv.DictReader(f)
            for line in reader:
                if line["code"] == position:
                    nodes = line.values()
                    break
        nodes = list(nodes)
        nodes.pop(0)
        nodes = [i for i in nodes if i is not None]
        match utype:
            case "A":
                remover = "S"
            case "F":
                remover = "L"
        self.nodes = [i for i in nodes if i[len(i) - 1] != remover]
        return


def main():
    check_position()
    load_pieces()
    check_convoys()
    check_support()
    check_movements()
    gather_sim()
    return

# Get last position
def check_position():
    global positions
    global current
    with open('position.json', 'r') as f:
        positions = json.load(f)
        if len(positions) == 0:
            init_position()
        else:
            current = positions[len(positions)-1]
    return

def load_pieces():
    global current
    for p in current["positions"]:
        pieces.append(piece(p["Type"], p["Country"], p["Position"]))
    return

def check_convoys():
    global convoys
    global pieces
    global aconvoys
    fleetlist = [i for i in pieces if i.unit_type == "F"]
    convoylist = [i for i in fleetlist if i.position[len(i.position) - 1] == "S"]
    armylist = [i for i in pieces if i.unit_type == "A"]
    for fleet in convoylist:
        for army in armylist:
            test = [i for i in fleet.nodes if i == army.position]
            if len(test) != 0:
                origin = army.position
                convoyer = fleet.position
                destinations = [i for i in fleet.nodes if i != origin]
                convoy = ("CONVOY", convoyer, origin, destinations, fleet.id)
                aconvoy = ("ARMYCONVOY", origin, destinations, army.id)
                aconvoys.append(aconvoy)
                convoys.append(convoy)

# For this section, I'm going to assume that supporting an army, and that army moving is one move.
# For this reason, an available support will add n permutations
# n is the number of moves Army 2 can move while being supported by Army 1
def check_support():
    global pieces
    global supports
    # TODO #1: Find two armies that share a node
    # TODO #2: Find two armies next to each other
    for p in pieces:
        for q in pieces:
            if q.position == p.position:
                continue
            testlist = [i for i in q.nodes if i == p.position]
            testlist2 = [i for i in q.nodes if i in p.nodes]
            testlist3 = [i for i in pieces if i.position in testlist2]
            if len(testlist2) != 0 and len(testlist3) == 0:
                tup = ("SUPPORT", p.position, q.position, testlist2, p.id)
                supports.append(tup)
            # For this next one, I'm assuming no one attacks their own square
            # THIS CODE IS UNTESTED, I'M WORKING ON A TEST
            elif len(testlist2) != 0 and len(testlist3) != 0:
                badlist = [i.position for i in testlist3 if i.country == p.country or i.country == q.country]
                for item in badlist:
                    testlist2.remove(item)
                if len(testlist2) != 0:
                    tup = ("SUPPORT", p.position, q.position, testlist2, p.id)
                    supports.append(tup)
            if len(testlist) != 0:
                supports.append(("SUPPORT", p.position,q.position, p.id))
    return

def check_movements():
    global pieces
    global movements
    global holds
    for p in pieces:
        holds.append(("HOLD", p.position, p.id))
        options = [i for i in p.nodes]
        tup = ("MOVEMENT", p.position, options, p.id)
        movements.append(tup)
    return

def gather_sim():
    global movements
    global convoys
    global aconvoys
    holders = []
    n = 0
    for hold in holds:
        hold = list(hold)
        hold.append(n)
        holders.append(hold)
        n += 1
    master = holders
    movers = []
    supporters = []
    convoyers = []
    aconvoyers = []
    for movement in movements:
        for item in movement[2]:
            it = ["MOVEMENT", movement[1], item, movement[3], n]
            movers.append(it)
            n += 1
    master.extend(movers)
    for support in supports:
        if len(support) == 5:
            for item in support[3]:
                it = ["SUPPORT", support[1], support[2], item, support[4], n]
                supporters.append(it)
                n += 1
        else:
            support = list(support)
            support.append(n)
            supporters.append(support)
            n += 1
    master.extend(supporters)
    for convoy in convoys:
        for item in convoy[3]:
            it = ["CONVOY", convoy[1], convoy[2], item, convoy[4], n]
            convoyers.append(it)
            n += 1
    for aconvoy in aconvoys:
        for item in aconvoy[2]:
            it = ["ARMYCONVOY", aconvoy[1], item, aconvoy[3], n]
            aconvoyers.append(it)
            n += 1
    master.extend(aconvoyers)
    master.extend(convoyers)
    with open('actions.json', 'w') as f:
        json.dump(master, f)
    print(len(master))
    del master
    return

def run_sim():
    with open('actions.json', 'r') as f:
        d = json.read(f)
    # TODO: Run down the tree of possiblities. Start by doing a Hold/Move model only. Then bring in the support possiblities, then finally convoys.
    return

def init_position():
    global positions
    global current
    positions = []
    with open('initial.csv', 'r') as f:
        for line in csv.DictReader(f):
            position = {"Country": line["country"], "Type" : line["type"], "Position" : line["position"]}
            positions.append(position)
    info = [{"year": 1901, "period": 1, "positions": positions}]
    with open('position.json', 'a') as g:
        t = json.dump(info, g)
    return
    

if __name__ == "__main__":
    main()