class TreeNode(object):
    def __init__(self,x):
        self.val=x
        self.left=None
        self.right=None

class Tree(object):
    def __init__(self):
        self.root=TreeNode(None)
        self.t=[]
    def add(self,val):
        treenode=TreeNode(val)
        if self.root.val==None:
            self.root=treenode
            self.t.append(self.root)
            return
        else: 
            tree_exist_node=self.t[0]
            print(self.t[0].val)
            if tree_exist_node.left==None:
                tree_exist_node.left=treenode
                self.t.append(tree_exist_node.left)
                return
            else: 
                tree_exist_node.right=treenode
                self.t.append(tree_exist_node.right)
                self.t.pop(0)

t1=[2,1,3,None,4,None,7]
t=Tree()
for i in t1:
    print("-----------",i)
    t.add(i)
