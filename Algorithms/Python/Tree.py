# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

class Solution:
    def __init__(self):
        self.flag = True
        
    def isBalanced(self, root):
        def isb(root):
            root = TreeNode(root)
            if not root:
                return 0
            l = isb(root.left) + 1
            r =  isb(root.right) + 1
            if abs(l-r)>1:
                self.flag = False      
            return max(l,r)
        isb(root)
        return self.flag

solution = Solution()
list = [3,9,20,None,None,15,7]

for i in list:
    print(i)
    solution.isBalanced(i)