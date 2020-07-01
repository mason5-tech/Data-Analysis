#Goal
#find longest lenght for two vocabuary
#"eceba": ece, 3
#"ccaabbb": aabbb,5


input1 = "eceba"
input2 = "ccaabbb"
input3 = "a"

class Solution():
    def __init__(self):
        self.hash = {}
        self.max_len = 2
        self.right = 0
        self.left = 0
    def process(self,val):
        hash = self.hash
        max_len = self.max_len
        right = self.right
        left = self.left

        if len(val) < 3:
            return len(val)

        while right < len(val):
            if len(hash) < 3:
                hash[val[right]] = right
                right += 1
            if len(hash) == 3:
                del_ind = min(hash.values())
                del hash[val[del_ind]]
                left = del_ind + 1
            max_len = max(max_len, right - left)
        return max_len

if __name__ == "__main__":
    print(Solution().process(input1))
    print(Solution().process(input2))
    print(Solution().process(input3))