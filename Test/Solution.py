class Solution:
    def longestPalindrome(self, s: str) -> str:
        if len(s) ==1:
            return s
        poliStr = ""
        for i in range(len(s)):
            for j in range(i+1, len(s)+1):
                subStr = s[i:j]
                if self.checkPoly(subStr):
                    if len(subStr) > len(poliStr):
                        poliStr = subStr
        return poliStr
        

    def checkPoly(self, s: str) -> bool:
        if s ==  s[::-1]:
            return True
        return False
    
if __name__ =="__main__":
    print(Solution().longestPalindrome("bb"))
