import anytree
from anytree import NodeMixin, RenderTree
from anytree.exporter import DotExporter

# class which stocks the data of the robot arm
class Arm :
    def __init__(self, empty=True, holding=None):
        self.empty = empty # know if the arm is holding something
        self.holding = holding # containing the current box which is hold by the arm

    # function to know if the robot is holding a specific box
    def isHolding(self, box):
        if(self.empty == False and self.holding == box):
            return True
        return False

    # function to grab a specific box and update the status of the arm
    def grab(self, box):
        if(self.empty): # the robot must not hold anything
            # we need to update the box
            box.getGrabbed()
            # then we update the arm state
            self.empty = False
            self.holding = box        
        else:
            print("the arm has already a box, it can't take another")

    # function to drop a specific box and update the status of the arm
    def drop(self, onThisBox):
        if(not self.empty):
            self.empty = True # the arm can now grab something else
            if(onThisBox == None): # we didn't give a box to drop on, so we drop it on the table
                self.holding.putOnTable()
            else: # we drop it on the specified box
                self.holding.putOnBox(onThisBox)
            self.holding = None # the arm don't have a box anymore
        else:
            print("the arm doesn't have a box, it can't drop anything")

    # print the content of the arm
    def show(self):
        print("   - Arm :")
        print("     - empty :", bool(self.empty))   
        if(self.holding == None):
            print("     - holding : Nothing")
        else:
            print("     - holding :", self.holding.name)

    # function to compare this Arm with another one
    def isEqual(self, arm):
        if(self.empty == arm.empty):
            if(self.holding == None and arm.holding == None):
                return True
            elif(self.holding != None and arm.holding != None):
                if(self.holding.isEqual(arm.holding)):
                    return True
        return False

    # function to copy the Arm instance
    def __copy__(self):
        if(self.holding == None):
            return Arm(self.empty, None)
        else:
            return Arm(self.empty, self.holding.__copy__())


# class which stocks the data to create a box
class Box :
    def __init__(self, name, free=True, onTable=True, onBox=None):
        self.name = name
        self.free = free # know if we can grab the box
        self.onTable = onTable # know if the box is on the table
        self.onBox = onBox # containing the box which this box in on

    # function to know if this box is on a specific box
    def isOn(self, box):
        if(self.onBox == None or box == None):
            return False
        if(self.onBox.name == box.name):
            return True
        return False

    # function update the status of the box when grabbed
    def getGrabbed(self):
        self.free = False
        self.onTable = False
        self.onBox = None

    # function update the status of the box when dropped on the table
    def putOnTable(self):
        self.free = True
        self.onTable = True
        self.onBox = None

    # function update the status of the box when dropped on a specific box
    def putOnBox(self, box):
        if(box.free):
            box.free = False
            self.free = True
            self.onBox = box
        else:
            print("the box is not free, we can't put this box on it")

    # print the content of the box
    def show(self):
        print("   - Box :")
        print("     - name :", self.name)
        print("     - free :", bool(self.free))
        print("     - onTable :", bool(self.onTable))
        if(self.onBox == None):
            print("     - onBox : No")
        else:
            print("     - onBox :", self.onBox.name)

    # function to compare this Box with another one
    def isEqual(self, box):
        if(self.name == box.name and self.free == box.free and self.onTable == box.onTable):
            if(self.onBox == None and box.onBox == None):
                return True
            elif(self.onBox != None and box.onBox != None):
                if(self.onBox.name == box.onBox.name):
                    return True
        return False

    # function to copy the Box instance
    def __copy__(self):
        if(self.onBox == None):
            return Box(self.name, self.free, self.onTable, None)
        else:
            return Box(self.name, self.free, self.onTable, self.onBox.__copy__())
    

# class which stocks all the current positions of the robot and boxes
class State :
    # for the copy
    def __init__(self, arm=None, boxA=None, boxB=None, boxC=None):
        if(arm == None):
            self.arm = Arm()
        else:
            self.arm = arm

        if(boxA == None):
            self.boxA = Box("A")
        else:
            self.boxA = boxA

        if(boxB == None):
            self.boxB = Box("B")
        else:
            self.boxB = boxB

        if(boxC == None):
            self.boxC = Box("C")
        else:
            self.boxC = boxC

    # print the content of the state
    def show(self):
        self.arm.show()
        print()
        self.boxA.show()
        print()
        self.boxB.show()
        print()
        self.boxC.show()

    # function to compare this State with another one
    def isEqual(self, state):
        if(self.arm.isEqual(state.arm) and self.boxA.isEqual(state.boxA) and self.boxB.isEqual(state.boxB) and self.boxC.isEqual(state.boxC)):
            return True
        return False

    # function to copy the State instance
    def __copy__(self):
        copy = State(self.arm.__copy__(), self.boxA.__copy__(), self.boxB.__copy__(), self.boxC.__copy__())
        # update the arm pointer if it's holding a box
        if(copy.arm.holding != None):
            if(copy.arm.holding.name == copy.boxA.name):
                copy.arm.holding = copy.boxA
            elif(copy.arm.holding.name == copy.boxB.name):
                copy.arm.holding = copy.boxB
            elif(copy.arm.holding.name == copy.boxC.name):
                copy.arm.holding = copy.boxC         
        return copy

     
# our node which will be used in the MyNode class of anytree
class MyBaseNode :
    def __init__(self, state, depth, rule, choice=1):
        self.state = state
        self.rule = rule
        self.choice = choice

        self.h_value = 0
        if(choice == 1):
            self.h_value = 6
            if(state.boxA.isOn(state.boxB)): # if A is on B
                self.h_value -= 1
            else:
                self.h_value += 1
            if(state.boxB.isOn(state.boxC)): # if B is on C
                self.h_value -= 2
            else:
                self.h_value += 2
            if(state.boxC.onTable): # if C is on the table
                self.h_value -= 3
            else:
                self.h_value += 3
        elif(choice == 2):
            self.h_value = 3
            if(state.boxA.isOn(state.boxB)): # if A is on B
                self.h_value -= 1
            else:
                self.h_value += 1
            if(state.boxB.isOn(state.boxC)): # if B is on C
                self.h_value -= 1
            else:
                self.h_value += 1
            if(state.boxC.onTable): # if C is on the table
                self.h_value -= 1
            else:
                self.h_value += 1
            
        self.g_value = depth
        
        self.f = self.h_value + self.g_value

    # print the content of the node
    def show(self):
        print(" - Node :")
        self.state.show()
        print()
        print("   - rule : %d" % self.rule)
        print("   - choice : %d" % self.choice)
        print("   - h_value : %d" % self.h_value)
        print("   - g_value : %d" % self.g_value)
        print("   - f : %d" % self.f)


# overload of the anytree MyNode class, to implement our nodes
class MyNode(MyBaseNode, NodeMixin) :
    def __init__(self, state, depth, rule, choice, name, length, width, parent=None, children=None):
        MyBaseNode.__init__(self, state, depth, rule, choice)
        self.name = name
        self.length = length
        self.width = width
        self.parent = parent
        if children:
            self.children = children

    # function to compare this MyNode with another one
    def isEqual(self, node):
        if(self.state.isEqual(node.state)):
            return True
        return False


# rule which grab a box on the table if possible
def r1(state, box) : 
    if(state.arm.empty and box.free and box.onTable):
        state.arm.grab(box) # we grab the given box
        return True
    return False

        
# rule which grab a box on another box if possible
def r2(state, box) : 
    if(state.arm.empty and box.free):
        boxes = [state.boxA, state.boxB, state.boxC]
        for b in boxes:          
            if(box.isOn(b)):
                state.arm.grab(box) # we grab the given box
                b.free = True
                return True     
    return False


# rule which drop the box hold by the arm on the table if possible
def r3(state) : 
    if(not state.arm.empty):
        state.arm.drop(None) # we drop the box on the table
        return True
    return False


# rule which drop the box hold by the arm on another box if possible
def r4(state, box) : 
    if(not state.arm.empty and box.free):
        state.arm.drop(box) # we drop the box of the arm on the box given
        return True
    return False


# generate all the children of a node with the help of rules (r1, r2,...)
def generate_children(node) :
    children = []

    for i in range(3): # for all boxes
        tmp_state = node.state.__copy__() # copy of the node to not have the same pointers in the tree
        boxes = [tmp_state.boxA, tmp_state.boxB, tmp_state.boxC] # same thing with the boxes     
        if(r1(tmp_state, boxes[i])): # the rule 1 can be applied on the node for this box
            children.append(create_child(node, tmp_state.__copy__(), "r1"))
                    
        tmp_state = node.state.__copy__()
        boxes = [tmp_state.boxA, tmp_state.boxB, tmp_state.boxC]
        if(r2(tmp_state, boxes[i])): # the rule 2 can be applied on the node for this box
            children.append(create_child(node, tmp_state.__copy__(), "r2"))
                
        tmp_state = node.state.__copy__()
        boxes = [tmp_state.boxA, tmp_state.boxB, tmp_state.boxC]
        if(r4(tmp_state, boxes[i])): # the rule 4 can be applied on the node for this box
            children.append(create_child(node, tmp_state.__copy__(), "r4"))

    # we don't need to check for all boxes for this one because we put it on the table
    tmp_state = node.state.__copy__()
    if(r3(tmp_state)): # the rule 3 can be applied on the node
        children.append(create_child(node, tmp_state.__copy__(), "r3"))

    return children


# function used by generate_children to add the new node in the tree
def create_child(node, state, rule) :
    depth = node.length + 1
    name = "child_%d_" % (depth)
    new_child = MyNode(state, depth, rule, node.choice, name, depth, node.width, node) # add the child to the node
    return new_child


# insert a node in a list of MyNode, the list is sorted by the h_value
def insert(list, node) :
    index = len(list)
    
    for i in range(len(list)):
        if(list[i].h_value > node.h_value):
            index = i
            break

    if index == len(list):
      list = list[:index] + [node]
    else:
      list = list[:index] + [node] + list[index:]
    return list


# search a node in a list of MyNode for a duplicate, and return it if founded
def find(list, node) :
    for n in list:
        if(node.state.isEqual(n.state)): 
            return n # we found a duplicate of the node
    return None


# A* algorithm which take a root node and 
def a_star(start_node) :      
    open_list = [] # a list which stocks all the opened nodes during the algorithm
    close_list = [] # a list which stocks all the closed nodes during the algorithm
    open_list.append(start_node)

    while(len(open_list) > 0):
        node = open_list.pop(0) # get and remove the first node in the open list
        close_list = insert(close_list, node) # add the current node in the list of closed nodes
        
        children = generate_children(node) # we create all the children of the current node
        
        for child in children: # we search for the goal node in the newly created children
            if(child.h_value == 0):
                return True # we found the goal node, the algorithm stops
            
            found_in_open = find(open_list, child) # search the new node in the list of already opened nodes
            found_in_close = find(close_list, child) # search the new node in the list of already closed nodes

            # the node has never been created before
            if(found_in_open == None and found_in_close == None): 
                open_list = insert(open_list, child)

            # if we founded the new node in the list of closed nodes and the h value is more valuable, we remove it    
            elif(found_in_close != None and child.h_value < found_in_close.h_value): 
                close_list.remove(found_in_close)
                open_list = insert(open_list, child)

            # if we founded the new node in the list of opeed nodes and the h value is more valuable, we exchange it    
            elif(found_in_open != None and child.h_value < found_in_open.h_value):
                open_list.remove(found_in_open)
                open_list = insert(open_list, child)

            # else the new node already existed in the lists and we have better values with the old ones, so we don't keep it
                
    return False # the algorithm ends and we still didn't found the goal node

            
# creation of the root state with the configuration of our choice
root_state = State()
root_state.arm.empty = True
root_state.boxA.putOnTable()
root_state.boxB.putOnTable()
root_state.boxC.onTable = False
root_state.boxC.putOnBox(root_state.boxA)

# creation of the root node with anytree and our state
root_node = MyNode(root_state, 0, "r", 1, "root_", 0, 0)
#                                      ^-choice of the h value


# functions for the .dot tree
def nodenamefunc(node):
    return '%s\nh=%d\nf=%d' % (node.name, node.h_value, node.f)

def nodeattrfunc(node):
    if(node.h_value == 0):
        return 'shape=box color=red'
    return 'shape=box color=black'

def edgeattrfunc(node, child):
    if(child.h_value == 0):
        return 'label="%s" color=red' % (child.rule)
    return 'label="%s"' % (child.rule)

def edgetypefunc(node, child):
    return '--'


print("Start of the A* algorithm :")

if(a_star(root_node)): # the algorithm found the goal node
    # naming the nodes of the tree with a unique name to generate a correct .dot file
    number = 0 
    for pre, _, node in RenderTree(root_node): 
        node.name += "%d" % number
        number += 1

    #create the .dot file with the tree in it
    DotExporter(root_node, graph="graph", nodenamefunc=nodenamefunc,nodeattrfunc=nodeattrfunc,
                edgeattrfunc=edgeattrfunc, edgetypefunc=edgetypefunc).to_dotfile("tree.dot")
    # to compile it on linux : $ dot tree.dot -T png -o tree.png

    #create the .png image with the graphical tree in it
    DotExporter(root_node, graph="graph", nodenamefunc=nodenamefunc,nodeattrfunc=nodeattrfunc,
                edgeattrfunc=edgeattrfunc, edgetypefunc=edgetypefunc).to_picture("tree.png")
    
else:
    print("Failure: goal node not found")






    
    
