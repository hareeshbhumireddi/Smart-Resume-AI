"""
Interview Assistant Database Schema and Data
Expanded: role-based questions, 50 coding problems, 15 skill sets
"""
import sqlite3

DB_PATH = "resume_data.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_interview_tables():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_type TEXT,
        company TEXT,
        role TEXT,
        skills TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        readiness_score REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS interview_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        question TEXT,
        user_answer TEXT,
        score REAL,
        feedback TEXT,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES interview_sessions(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS coding_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        company TEXT,
        topic TEXT,
        examples TEXT,
        hints TEXT,
        solution TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS coding_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question_id INTEGER,
        user_code TEXT,
        is_correct INTEGER DEFAULT 0,
        time_taken INTEGER,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES coding_questions(id)
    )
    """)

    conn.commit()

    # Migrate: add solutions_json column if missing (handles existing DBs)
    try:
        c.execute("ALTER TABLE coding_questions ADD COLUMN solutions_json TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Seed coding questions if empty
    c.execute("SELECT COUNT(*) FROM coding_questions")
    if c.fetchone()[0] == 0:
        _seed_coding_questions(c)
        conn.commit()

    # Always apply multi-language solutions (idempotent migration)
    _seed_multilang_solutions(c)
    conn.commit()

    conn.close()


def _seed_coding_questions(c):
    questions = [
        # ── EASY ──────────────────────────────────────────────────────────────
        ("Two Sum",
         "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
         "Easy", "Google,Amazon", "Arrays",
         '[{"input":"nums=[2,7,11,15], target=9","output":"[0,1]"},{"input":"nums=[3,2,4], target=6","output":"[1,2]"}]',
         '["Use a hash map to store seen numbers","For each number check if target-number exists in the map"]',
         "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i"),

        ("Reverse String",
         "Write a function that reverses a string. The input string is given as an array of characters s. Do it in-place with O(1) extra memory.",
         "Easy", "Microsoft,TCS", "Strings",
         '[{"input":"s=[\'h\',\'e\',\'l\',\'l\',\'o\']","output":"[\'o\',\'l\',\'l\',\'e\',\'h\']"}]',
         '["Use two pointers","Swap characters from both ends moving inward"]',
         "def reverseString(s):\n    l, r = 0, len(s)-1\n    while l < r:\n        s[l], s[r] = s[r], s[l]\n        l += 1; r -= 1"),

        ("Valid Parentheses",
         "Given a string s containing '(', ')', '{', '}', '[' and ']', determine if the input string is valid. Brackets must close in correct order.",
         "Easy", "Amazon,Meta", "Stack",
         '[{"input":"s=\'()\'","output":"true"},{"input":"s=\'([)]\'","output":"false"}]',
         '["Use a stack","Push opening brackets; pop and match for closing brackets"]',
         "def isValid(s):\n    stack = []\n    mapping = {')':'(', '}':'{', ']':'['}\n    for c in s:\n        if c in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[c] != top: return False\n        else:\n            stack.append(c)\n    return not stack"),

        ("Binary Search",
         "Given a sorted array nums and a target, return the index of target. If not found return -1. Write O(log n) solution.",
         "Easy", "Google,TCS,Infosys", "Binary Search",
         '[{"input":"nums=[-1,0,3,5,9,12], target=9","output":"4"},{"input":"nums=[1,3,5], target=2","output":"-1"}]',
         '["Compare middle element with target","Eliminate half the array each step"]',
         "def search(nums, target):\n    l, r = 0, len(nums)-1\n    while l <= r:\n        mid = (l+r)//2\n        if nums[mid] == target: return mid\n        elif nums[mid] < target: l = mid+1\n        else: r = mid-1\n    return -1"),

        ("Maximum Subarray",
         "Given an integer array nums, find the contiguous subarray with the largest sum and return its sum. (Kadane's Algorithm)",
         "Easy", "Microsoft,Infosys", "Dynamic Programming",
         '[{"input":"nums=[-2,1,-3,4,-1,2,1,-5,4]","output":"6"},{"input":"nums=[1]","output":"1"}]',
         '["Kadane\'s algorithm","Track current sum; reset when it goes negative"]',
         "def maxSubArray(nums):\n    max_sum = cur = nums[0]\n    for n in nums[1:]:\n        cur = max(n, cur+n)\n        max_sum = max(max_sum, cur)\n    return max_sum"),

        ("Palindrome Number",
         "Given an integer x, return true if x is a palindrome, and false otherwise. Do not convert to string.",
         "Easy", "Amazon,Google", "Math",
         '[{"input":"x=121","output":"true"},{"input":"x=-121","output":"false"},{"input":"x=10","output":"false"}]',
         '["Negative numbers and numbers ending in 0 (except 0) are not palindromes","Reverse only half the number"]',
         "def isPalindrome(x):\n    if x < 0 or (x % 10 == 0 and x != 0): return False\n    rev = 0\n    while x > rev:\n        rev = rev*10 + x%10\n        x //= 10\n    return x == rev or x == rev//10"),

        ("Fizz Buzz",
         "Given an integer n, return a string array where answer[i] is 'FizzBuzz' if divisible by both 3 and 5, 'Fizz' if by 3, 'Buzz' if by 5, else the number.",
         "Easy", "TCS,Infosys,Wipro", "Math",
         '[{"input":"n=5","output":"[\\"1\\",\\"2\\",\\"Fizz\\",\\"4\\",\\"Buzz\\"]"}]',
         '["Check divisibility by 15 first, then 3, then 5"]',
         "def fizzBuzz(n):\n    res = []\n    for i in range(1, n+1):\n        if i%15==0: res.append('FizzBuzz')\n        elif i%3==0: res.append('Fizz')\n        elif i%5==0: res.append('Buzz')\n        else: res.append(str(i))\n    return res"),

        ("Contains Duplicate",
         "Given an integer array nums, return true if any value appears at least twice, and false if every element is distinct.",
         "Easy", "Google,Amazon,Microsoft", "Arrays",
         '[{"input":"nums=[1,2,3,1]","output":"true"},{"input":"nums=[1,2,3,4]","output":"false"}]',
         '["Use a HashSet","Add each element; if already present return True"]',
         "def containsDuplicate(nums):\n    return len(nums) != len(set(nums))"),

        ("Single Number",
         "Given a non-empty array of integers where every element appears twice except one, find that single one. Use O(1) extra space.",
         "Easy", "Amazon,Google", "Bit Manipulation",
         '[{"input":"nums=[2,2,1]","output":"1"},{"input":"nums=[4,1,2,1,2]","output":"4"}]',
         '["XOR of a number with itself is 0","XOR all numbers together"]',
         "def singleNumber(nums):\n    result = 0\n    for n in nums:\n        result ^= n\n    return result"),

        ("Climbing Stairs",
         "You are climbing a staircase with n steps. Each time you can climb 1 or 2 steps. In how many distinct ways can you reach the top?",
         "Easy", "Amazon,Google,Microsoft", "Dynamic Programming",
         '[{"input":"n=2","output":"2"},{"input":"n=3","output":"3"}]',
         '["This is essentially Fibonacci","dp[i] = dp[i-1] + dp[i-2]"]',
         "def climbStairs(n):\n    if n <= 2: return n\n    a, b = 1, 2\n    for _ in range(3, n+1):\n        a, b = b, a+b\n    return b"),

        ("Merge Sorted Arrays",
         "Given two sorted integer arrays nums1 and nums2, merge nums2 into nums1 in-place as one sorted array.",
         "Easy", "Google,Facebook,TCS", "Arrays",
         '[{"input":"nums1=[1,2,3,0,0,0], m=3, nums2=[2,5,6], n=3","output":"[1,2,2,3,5,6]"}]',
         '["Start merging from the end","Compare from back to front using two pointers"]',
         "def merge(nums1, m, nums2, n):\n    i, j, k = m-1, n-1, m+n-1\n    while i >= 0 and j >= 0:\n        if nums1[i] > nums2[j]:\n            nums1[k] = nums1[i]; i -= 1\n        else:\n            nums1[k] = nums2[j]; j -= 1\n        k -= 1\n    while j >= 0:\n        nums1[k] = nums2[j]; j -= 1; k -= 1"),

        ("Reverse Linked List",
         "Given the head of a singly linked list, reverse the list, and return the reversed list.",
         "Easy", "Amazon,Microsoft,Google", "Linked List",
         '[{"input":"head=[1,2,3,4,5]","output":"[5,4,3,2,1]"}]',
         '["Use three pointers: prev, curr, next","Iteratively reverse each link"]',
         "def reverseList(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev"),

        ("Best Time to Buy and Sell Stock",
         "Given an array prices where prices[i] is the price on day i, maximize your profit by choosing a single buy and sell day.",
         "Easy", "Amazon,Google,Goldman Sachs", "Arrays",
         '[{"input":"prices=[7,1,5,3,6,4]","output":"5"},{"input":"prices=[7,6,4,3,1]","output":"0"}]',
         '["Track minimum price seen so far","Profit = current_price - min_price_so_far"]',
         "def maxProfit(prices):\n    min_p, max_profit = float('inf'), 0\n    for p in prices:\n        min_p = min(min_p, p)\n        max_profit = max(max_profit, p - min_p)\n    return max_profit"),

        ("Symmetric Tree",
         "Given the root of a binary tree, check whether it is a mirror of itself (symmetric around its center).",
         "Easy", "Microsoft,Amazon", "Trees",
         '[{"input":"root=[1,2,2,3,4,4,3]","output":"true"},{"input":"root=[1,2,2,null,3,null,3]","output":"false"}]',
         '["Use recursive helper to check left vs right mirror","isMirror(left, right): compare values and recurse crossing"]',
         "def isSymmetric(root):\n    def mirror(l, r):\n        if not l and not r: return True\n        if not l or not r: return False\n        return l.val == r.val and mirror(l.left, r.right) and mirror(l.right, r.left)\n    return mirror(root.left, root.right)"),

        ("Maximum Depth of Binary Tree",
         "Given the root of a binary tree, return its maximum depth (number of nodes along longest path from root to farthest leaf).",
         "Easy", "Google,Amazon,Infosys", "Trees",
         '[{"input":"root=[3,9,20,null,null,15,7]","output":"3"}]',
         '["DFS recursion: depth = 1 + max(left_depth, right_depth)"]',
         "def maxDepth(root):\n    if not root: return 0\n    return 1 + max(maxDepth(root.left), maxDepth(root.right))"),

        # ── MEDIUM ────────────────────────────────────────────────────────────
        ("Longest Substring Without Repeating Characters",
         "Given a string s, find the length of the longest substring without repeating characters.",
         "Medium", "Google,Amazon,Microsoft", "Sliding Window",
         '[{"input":"s=\'abcabcbb\'","output":"3"},{"input":"s=\'bbbbb\'","output":"1"}]',
         '["Sliding window with two pointers","Use a set to track characters in the current window"]',
         "def lengthOfLongestSubstring(s):\n    char_set = set()\n    l = max_len = 0\n    for r in range(len(s)):\n        while s[r] in char_set:\n            char_set.remove(s[l]); l += 1\n        char_set.add(s[r])\n        max_len = max(max_len, r-l+1)\n    return max_len"),

        ("Merge Intervals",
         "Given an array of intervals [start, end], merge all overlapping intervals and return the result.",
         "Medium", "Google,Facebook,Amazon", "Arrays",
         '[{"input":"intervals=[[1,3],[2,6],[8,10],[15,18]]","output":"[[1,6],[8,10],[15,18]]"}]',
         '["Sort by start time","If current start <= previous end, merge"]',
         "def merge(intervals):\n    intervals.sort(key=lambda x: x[0])\n    merged = [intervals[0]]\n    for s, e in intervals[1:]:\n        if s <= merged[-1][1]:\n            merged[-1][1] = max(merged[-1][1], e)\n        else:\n            merged.append([s, e])\n    return merged"),

        ("Number of Islands",
         "Given an m×n grid of '1's (land) and '0's (water), return the number of islands (connected '1's).",
         "Medium", "Amazon,Google,TCS", "Graph/DFS",
         '[{"input":"grid=[[1,1,0],[0,1,0],[0,0,1]]","output":"2"}]',
         '["DFS/BFS to mark visited land as visited","Count each DFS initiation as one island"]',
         "def numIslands(grid):\n    def dfs(i, j):\n        if i<0 or i>=len(grid) or j<0 or j>=len(grid[0]) or grid[i][j]!='1': return\n        grid[i][j]='0'\n        for di,dj in [(0,1),(0,-1),(1,0),(-1,0)]: dfs(i+di,j+dj)\n    count=0\n    for i in range(len(grid)):\n        for j in range(len(grid[0])):\n            if grid[i][j]=='1': dfs(i,j); count+=1\n    return count"),

        ("Add Two Numbers",
         "Given two linked lists representing two non-negative integers in reverse order, add them and return the sum as a linked list.",
         "Medium", "Amazon,Microsoft,Google", "Linked List",
         '[{"input":"l1=[2,4,3], l2=[5,6,4]","output":"[7,0,8] (342+465=807)"}]',
         '["Traverse both lists simultaneously","Handle carry at each step"]',
         "def addTwoNumbers(l1, l2):\n    dummy = ListNode(0)\n    curr, carry = dummy, 0\n    while l1 or l2 or carry:\n        val = carry\n        if l1: val += l1.val; l1 = l1.next\n        if l2: val += l2.val; l2 = l2.next\n        carry, val = divmod(val, 10)\n        curr.next = ListNode(val)\n        curr = curr.next\n    return dummy.next"),

        ("3Sum",
         "Given an integer array nums, return all triplets [nums[i], nums[j], nums[k]] such that i≠j≠k and nums[i]+nums[j]+nums[k]==0. No duplicates.",
         "Medium", "Google,Amazon,Facebook", "Two Pointers",
         '[{"input":"nums=[-1,0,1,2,-1,-4]","output":"[[-1,-1,2],[-1,0,1]]"}]',
         '["Sort the array first","Fix one element, use two pointers for the rest"]',
         "def threeSum(nums):\n    nums.sort(); res = []\n    for i in range(len(nums)-2):\n        if i > 0 and nums[i] == nums[i-1]: continue\n        l, r = i+1, len(nums)-1\n        while l < r:\n            s = nums[i]+nums[l]+nums[r]\n            if s == 0:\n                res.append([nums[i],nums[l],nums[r]])\n                while l<r and nums[l]==nums[l+1]: l+=1\n                while l<r and nums[r]==nums[r-1]: r-=1\n                l+=1; r-=1\n            elif s < 0: l+=1\n            else: r-=1\n    return res"),

        ("Product of Array Except Self",
         "Given an integer array nums, return an array answer where answer[i] equals the product of all elements except nums[i]. O(n) time, no division.",
         "Medium", "Amazon,Facebook,Google", "Arrays",
         '[{"input":"nums=[1,2,3,4]","output":"[24,12,8,6]"}]',
         '["Compute prefix products from left","Multiply with suffix products from right in second pass"]',
         "def productExceptSelf(nums):\n    n = len(nums)\n    ans = [1]*n\n    prefix = 1\n    for i in range(n):\n        ans[i] = prefix; prefix *= nums[i]\n    suffix = 1\n    for i in range(n-1,-1,-1):\n        ans[i] *= suffix; suffix *= nums[i]\n    return ans"),

        ("Find All Anagrams in a String",
         "Given strings s and p, return all start indices of p's anagrams in s.",
         "Medium", "Facebook,Amazon,Google", "Sliding Window",
         '[{"input":"s=\'cbaebabacd\', p=\'abc\'","output":"[0,6]"}]',
         '["Use fixed-size sliding window equal to p length","Compare character frequency counts"]',
         "from collections import Counter\ndef findAnagrams(s, p):\n    if len(p)>len(s): return []\n    pc, sc = Counter(p), Counter(s[:len(p)])\n    res = [0] if sc==pc else []\n    for i in range(len(p), len(s)):\n        sc[s[i]]+=1\n        sc[s[i-len(p)]]-=1\n        if sc[s[i-len(p)]]==0: del sc[s[i-len(p)]]\n        if sc==pc: res.append(i-len(p)+1)\n    return res"),

        ("Spiral Matrix",
         "Given an m×n matrix, return all elements in spiral order.",
         "Medium", "Google,Microsoft,Amazon", "Arrays",
         '[{"input":"matrix=[[1,2,3],[4,5,6],[7,8,9]]","output":"[1,2,3,6,9,8,7,4,5]"}]',
         '["Peel outer layer one at a time","Track top, bottom, left, right boundaries"]',
         "def spiralOrder(matrix):\n    res = []\n    top, bottom, left, right = 0, len(matrix)-1, 0, len(matrix[0])-1\n    while top<=bottom and left<=right:\n        for i in range(left,right+1): res.append(matrix[top][i])\n        top+=1\n        for i in range(top,bottom+1): res.append(matrix[i][right])\n        right-=1\n        if top<=bottom:\n            for i in range(right,left-1,-1): res.append(matrix[bottom][i])\n            bottom-=1\n        if left<=right:\n            for i in range(bottom,top-1,-1): res.append(matrix[i][left])\n            left+=1\n    return res"),

        ("Coin Change",
         "Given coins of different denominations and a total amount, return the fewest coins needed to make up that amount, or -1 if impossible.",
         "Medium", "Amazon,Google,Microsoft", "Dynamic Programming",
         '[{"input":"coins=[1,5,11], amount=15","output":"3"},{"input":"coins=[2], amount=3","output":"-1"}]',
         '["Bottom-up DP: dp[i] = min coins to make amount i","dp[0]=0; iterate from 1 to amount"]',
         "def coinChange(coins, amount):\n    dp = [float('inf')]*(amount+1)\n    dp[0] = 0\n    for i in range(1, amount+1):\n        for c in coins:\n            if c <= i:\n                dp[i] = min(dp[i], dp[i-c]+1)\n    return dp[amount] if dp[amount]!=float('inf') else -1"),

        ("Binary Tree Level Order Traversal",
         "Given the root of a binary tree, return its level order traversal as a list of lists.",
         "Medium", "Amazon,Microsoft,Google", "Trees",
         '[{"input":"root=[3,9,20,null,null,15,7]","output":"[[3],[9,20],[15,7]]"}]',
         '["Use a queue (BFS)","Process nodes level by level using queue size"]',
         "from collections import deque\ndef levelOrder(root):\n    if not root: return []\n    res, q = [], deque([root])\n    while q:\n        level = []\n        for _ in range(len(q)):\n            node = q.popleft()\n            level.append(node.val)\n            if node.left: q.append(node.left)\n            if node.right: q.append(node.right)\n        res.append(level)\n    return res"),

        ("Validate Binary Search Tree",
         "Given the root of a binary tree, determine if it is a valid binary search tree (BST).",
         "Medium", "Amazon,Microsoft,Facebook", "Trees",
         '[{"input":"root=[2,1,3]","output":"true"},{"input":"root=[5,1,4,null,null,3,6]","output":"false"}]',
         '["Use min/max bounds recursively","Left subtree must be < node; right > node"]',
         "def isValidBST(root, lo=float('-inf'), hi=float('inf')):\n    if not root: return True\n    if root.val<=lo or root.val>=hi: return False\n    return isValidBST(root.left, lo, root.val) and isValidBST(root.right, root.val, hi)"),

        ("Course Schedule",
         "Given numCourses and prerequisites pairs, return true if you can finish all courses (detect cycle in directed graph).",
         "Medium", "Amazon,Facebook,Google", "Graph/DFS",
         '[{"input":"numCourses=2, prerequisites=[[1,0]]","output":"true"},{"input":"numCourses=2, prerequisites=[[1,0],[0,1]]","output":"false"}]',
         '["Build adjacency list","DFS with 3-color cycle detection (unvisited/visiting/visited)"]',
         "def canFinish(numCourses, prerequisites):\n    graph = [[] for _ in range(numCourses)]\n    for a,b in prerequisites: graph[b].append(a)\n    state = [0]*numCourses\n    def dfs(u):\n        if state[u]==1: return False\n        if state[u]==2: return True\n        state[u]=1\n        if any(not dfs(v) for v in graph[u]): return False\n        state[u]=2; return True\n    return all(dfs(i) for i in range(numCourses))"),

        ("Rotate Image",
         "You are given an n×n 2D matrix. Rotate the matrix by 90 degrees clockwise in-place.",
         "Medium", "Amazon,Microsoft,Google", "Arrays",
         '[{"input":"matrix=[[1,2,3],[4,5,6],[7,8,9]]","output":"[[7,4,1],[8,5,2],[9,6,3]]"}]',
         '["First transpose the matrix","Then reverse each row"]',
         "def rotate(matrix):\n    n = len(matrix)\n    for i in range(n):\n        for j in range(i+1,n):\n            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n    for row in matrix:\n        row.reverse()"),

        ("Word Search",
         "Given an m×n board of characters and a word, return true if the word exists in the grid following adjacent cells horizontally or vertically.",
         "Medium", "Amazon,Microsoft,Uber", "Graph/DFS",
         '[{"input":"board=[[A,B,C,E],[S,F,C,S],[A,D,E,E]], word=ABCCED","output":"true"}]',
         '["DFS from each cell matching first character","Mark visited cells temporarily"]',
         "def exist(board, word):\n    rows, cols = len(board), len(board[0])\n    def dfs(r, c, idx):\n        if idx == len(word): return True\n        if r<0 or r>=rows or c<0 or c>=cols or board[r][c]!=word[idx]: return False\n        tmp, board[r][c] = board[r][c], '#'\n        found = any(dfs(r+dr, c+dc, idx+1) for dr,dc in [(0,1),(0,-1),(1,0),(-1,0)])\n        board[r][c] = tmp\n        return found\n    return any(dfs(r,c,0) for r in range(rows) for c in range(cols))"),

        ("Subsets",
         "Given an integer array nums of unique elements, return all possible subsets (the power set). Solution must not contain duplicate subsets.",
         "Medium", "Amazon,Google,Facebook", "Backtracking",
         '[{"input":"nums=[1,2,3]","output":"[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]"}]',
         '["Backtracking: include or exclude each element","Or iteratively extend each existing subset"]',
         "def subsets(nums):\n    res = [[]]\n    for n in nums:\n        res += [sub+[n] for sub in res]\n    return res"),

        ("Search in Rotated Sorted Array",
         "Given a sorted array that was rotated at an unknown pivot, search for a target. Return index or -1. Must be O(log n).",
         "Medium", "Google,Amazon,Microsoft", "Binary Search",
         '[{"input":"nums=[4,5,6,7,0,1,2], target=0","output":"4"},{"input":"nums=[4,5,6,7,0,1,2], target=3","output":"-1"}]',
         '["Determine which half is sorted","Check if target falls in the sorted half"]',
         "def search(nums, target):\n    l, r = 0, len(nums)-1\n    while l<=r:\n        mid=(l+r)//2\n        if nums[mid]==target: return mid\n        if nums[l]<=nums[mid]:\n            if nums[l]<=target<nums[mid]: r=mid-1\n            else: l=mid+1\n        else:\n            if nums[mid]<target<=nums[r]: l=mid+1\n            else: r=mid-1\n    return -1"),

        ("Top K Frequent Elements",
         "Given an integer array nums and integer k, return the k most frequent elements. Answer may be returned in any order.",
         "Medium", "Facebook,Amazon,Google", "Hash Map",
         '[{"input":"nums=[1,1,1,2,2,3], k=2","output":"[1,2]"}]',
         '["Count frequencies with hashmap","Use bucket sort (index = frequency) for O(n)"]',
         "from collections import Counter\ndef topKFrequent(nums, k):\n    count = Counter(nums)\n    buckets = [[] for _ in range(len(nums)+1)]\n    for n,f in count.items(): buckets[f].append(n)\n    res = []\n    for b in reversed(buckets):\n        res.extend(b)\n        if len(res)>=k: break\n    return res[:k]"),

        # ── HARD ──────────────────────────────────────────────────────────────
        ("Trapping Rain Water",
         "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
         "Hard", "Amazon,Google,Meta", "Two Pointers",
         '[{"input":"height=[0,1,0,2,1,0,1,3,2,1,2,1]","output":"6"}]',
         '["Two pointers from both ends","Track max height from left and right"]',
         "def trap(height):\n    l, r = 0, len(height)-1\n    lmax = rmax = water = 0\n    while l < r:\n        if height[l] < height[r]:\n            if height[l]>=lmax: lmax=height[l]\n            else: water+=lmax-height[l]\n            l+=1\n        else:\n            if height[r]>=rmax: rmax=height[r]\n            else: water+=rmax-height[r]\n            r-=1\n    return water"),

        ("LRU Cache",
         "Design a data structure following LRU cache constraints. Implement LRUCache with get(key) and put(key,value) in O(1).",
         "Hard", "Amazon,Google,Microsoft", "Design",
         '[{"input":"LRUCache(2), put(1,1), put(2,2), get(1)->1, put(3,3), get(2)->-1","output":"[-1]"}]',
         '["Use an OrderedDict","Move accessed keys to end; evict from front when capacity exceeded"]',
         "from collections import OrderedDict\nclass LRUCache:\n    def __init__(self, capacity):\n        self.cap=capacity; self.cache=OrderedDict()\n    def get(self, key):\n        if key not in self.cache: return -1\n        self.cache.move_to_end(key); return self.cache[key]\n    def put(self, key, value):\n        if key in self.cache: self.cache.move_to_end(key)\n        self.cache[key]=value\n        if len(self.cache)>self.cap: self.cache.popitem(last=False)"),

        ("Number of Islands",
         "Given an m×n grid of '1' (land) and '0' (water), return the number of islands.",
         "Medium", "Amazon,Google,TCS", "Graph/DFS",
         '[{"input":"grid=[[1,1,0],[0,1,0],[0,0,1]]","output":"2"}]',
         '["DFS from each unvisited land cell","Sink the island (mark visited) during DFS"]',
         "def numIslands(grid):\n    def dfs(i,j):\n        if i<0 or i>=len(grid) or j<0 or j>=len(grid[0]) or grid[i][j]!='1': return\n        grid[i][j]='0'\n        for di,dj in [(0,1),(0,-1),(1,0),(-1,0)]: dfs(i+di,j+dj)\n    cnt=0\n    for i in range(len(grid)):\n        for j in range(len(grid[0])):\n            if grid[i][j]=='1': dfs(i,j); cnt+=1\n    return cnt"),

        ("Median of Two Sorted Arrays",
         "Given two sorted arrays nums1 and nums2, return the median of the two sorted arrays. O(log(m+n)) time.",
         "Hard", "Google,Amazon,Microsoft", "Binary Search",
         '[{"input":"nums1=[1,3], nums2=[2]","output":"2.0"},{"input":"nums1=[1,2], nums2=[3,4]","output":"2.5"}]',
         '["Binary search on the smaller array","Find correct partition where max_left <= min_right"]',
         "def findMedianSortedArrays(nums1, nums2):\n    A, B = sorted([nums1,nums2], key=len)\n    m, n = len(A), len(B)\n    lo, hi = 0, m\n    while lo<=hi:\n        i=(lo+hi)//2; j=(m+n+1)//2-i\n        maxL_A=A[i-1] if i>0 else float('-inf')\n        minR_A=A[i] if i<m else float('inf')\n        maxL_B=B[j-1] if j>0 else float('-inf')\n        minR_B=B[j] if j<n else float('inf')\n        if maxL_A<=minR_B and maxL_B<=minR_A:\n            if (m+n)%2: return float(max(maxL_A,maxL_B))\n            return (max(maxL_A,maxL_B)+min(minR_A,minR_B))/2\n        elif maxL_A>minR_B: hi=i-1\n        else: lo=i+1"),

        ("Word Break",
         "Given a string s and a dictionary wordDict, return true if s can be segmented into a space-separated sequence of dictionary words.",
         "Hard", "Google,Amazon,Facebook", "Dynamic Programming",
         '[{"input":"s=\'leetcode\', wordDict=[\'leet\',\'code\']","output":"true"},{"input":"s=\'catsandog\', wordDict=[\'cats\',\'dog\',\'sand\',\'and\',\'cat\']","output":"false"}]',
         '["dp[i] = can s[:i] be segmented","For each i, check all j<i if dp[j] and s[j:i] in dict"]',
         "def wordBreak(s, wordDict):\n    wd = set(wordDict)\n    dp = [False]*(len(s)+1); dp[0]=True\n    for i in range(1,len(s)+1):\n        for j in range(i):\n            if dp[j] and s[j:i] in wd:\n                dp[i]=True; break\n    return dp[len(s)]"),

        ("Regular Expression Matching",
         "Given an input string s and a pattern p, implement regular expression matching with '.' (any char) and '*' (zero or more).",
         "Hard", "Google,Facebook,Amazon", "Dynamic Programming",
         '[{"input":"s=\'aa\', p=\'a*\'","output":"true"},{"input":"s=\'aab\', p=\'c*a*b\'","output":"true"}]',
         '["2D DP: dp[i][j] = does s[:i] match p[:j]","Handle * carefully: skip pair OR use the char"]',
         "def isMatch(s, p):\n    m, n = len(s), len(p)\n    dp = [[False]*(n+1) for _ in range(m+1)]\n    dp[0][0]=True\n    for j in range(2,n+1):\n        if p[j-1]=='*': dp[0][j]=dp[0][j-2]\n    for i in range(1,m+1):\n        for j in range(1,n+1):\n            if p[j-1]=='*':\n                dp[i][j]=dp[i][j-2] or (dp[i-1][j] and (p[j-2]=='.' or p[j-2]==s[i-1]))\n            elif p[j-1]=='.' or p[j-1]==s[i-1]:\n                dp[i][j]=dp[i-1][j-1]\n    return dp[m][n]"),

        ("Serialize and Deserialize Binary Tree",
         "Design an algorithm to serialize and deserialize a binary tree. No restriction on format.",
         "Hard", "Facebook,Google,Amazon", "Trees",
         '[{"input":"root=[1,2,3,null,null,4,5]","output":"[1,2,3,null,null,4,5]"}]',
         '["Pre-order traversal with null markers","Use a queue/iterator to deserialize"]',
         "from collections import deque\nclass Codec:\n    def serialize(self, root):\n        res=[]\n        def dfs(node):\n            if not node: res.append('N'); return\n            res.append(str(node.val)); dfs(node.left); dfs(node.right)\n        dfs(root); return ','.join(res)\n    def deserialize(self, data):\n        q=deque(data.split(','))\n        def dfs():\n            v=q.popleft()\n            if v=='N': return None\n            node=TreeNode(int(v))\n            node.left=dfs(); node.right=dfs()\n            return node\n        return dfs()"),

        ("Sliding Window Maximum",
         "Given an array nums and a window size k, return the maximum value in each sliding window of size k.",
         "Hard", "Amazon,Google,Uber", "Sliding Window",
         '[{"input":"nums=[1,3,-1,-3,5,3,6,7], k=3","output":"[3,3,5,5,6,7]"}]',
         '["Use a monotonic deque","Keep deque in decreasing order; front is always the max"]',
         "from collections import deque\ndef maxSlidingWindow(nums, k):\n    dq, res = deque(), []\n    for i, n in enumerate(nums):\n        while dq and nums[dq[-1]]<n: dq.pop()\n        dq.append(i)\n        if dq[0]==i-k: dq.popleft()\n        if i>=k-1: res.append(nums[dq[0]])\n    return res"),

        ("Alien Dictionary",
         "Given a sorted list of words from an alien language, derive the order of letters in the alien alphabet.",
         "Hard", "Google,Facebook,Airbnb", "Graph/DFS",
         '[{"input":"words=[\'wrt\',\'wrf\',\'er\',\'ett\',\'rftt\']","output":"\'wertf\'"}]',
         '["Build directed graph from adjacent word comparisons","Topological sort using DFS"]',
         "from collections import defaultdict, deque\ndef alienOrder(words):\n    adj={c:set() for w in words for c in w}\n    for i in range(len(words)-1):\n        w1,w2=words[i],words[i+1]\n        for c1,c2 in zip(w1,w2):\n            if c1!=c2: adj[c1].add(c2); break\n        else:\n            if len(w1)>len(w2): return ''\n    visited={}\n    res=[]\n    def dfs(c):\n        if c in visited: return visited[c]\n        visited[c]=True\n        for nb in adj[c]:\n            if dfs(nb): return True\n        visited[c]=False; res.append(c)\n    for c in adj:\n        if dfs(c): return ''\n    return ''.join(reversed(res))"),
    ]
    c.executemany(
        "INSERT INTO coding_questions (title, description, difficulty, company, topic, examples, hints, solution) VALUES (?,?,?,?,?,?,?,?)",
        questions
    )


def _seed_multilang_solutions(c):
    """Add/update multi-language solutions. Safe to call multiple times (idempotent)."""
    import json as _json
    MULTILANG = {
        "Two Sum": {
            "Python": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen: return [seen[diff], i]\n        seen[n] = i",
            "Java": "public int[] twoSum(int[] nums, int target) {\n    Map<Integer,Integer> map = new HashMap<>();\n    for (int i=0;i<nums.length;i++) {\n        int diff = target-nums[i];\n        if (map.containsKey(diff)) return new int[]{map.get(diff),i};\n        map.put(nums[i],i);\n    }\n    return new int[]{};\n}",
            "JavaScript": "var twoSum = function(nums, target) {\n    const map = new Map();\n    for (let i=0;i<nums.length;i++) {\n        const diff = target-nums[i];\n        if (map.has(diff)) return [map.get(diff),i];\n        map.set(nums[i],i);\n    }\n};",
            "C++": "vector<int> twoSum(vector<int>& nums, int target) {\n    unordered_map<int,int> mp;\n    for (int i=0;i<(int)nums.size();i++) {\n        int diff=target-nums[i];\n        if (mp.count(diff)) return {mp[diff],i};\n        mp[nums[i]]=i;\n    }\n    return {};\n}",
        },
        "Reverse String": {
            "Python": "def reverseString(s):\n    l, r = 0, len(s)-1\n    while l < r:\n        s[l], s[r] = s[r], s[l]\n        l += 1; r -= 1",
            "Java": "public void reverseString(char[] s) {\n    int l=0,r=s.length-1;\n    while(l<r){char t=s[l];s[l++]=s[r];s[r--]=t;}\n}",
            "JavaScript": "var reverseString = function(s) {\n    let l=0,r=s.length-1;\n    while(l<r){[s[l],s[r]]=[s[r],s[l]];l++;r--;}\n};",
            "C++": "void reverseString(vector<char>& s){\n    int l=0,r=s.size()-1;\n    while(l<r) swap(s[l++],s[r--]);\n}",
        },
        "Valid Parentheses": {
            "Python": "def isValid(s):\n    stack=[]\n    mapping={')':'(', '}':'{', ']':'['}\n    for c in s:\n        if c in mapping:\n            top=stack.pop() if stack else '#'\n            if mapping[c]!=top: return False\n        else: stack.append(c)\n    return not stack",
            "Java": "public boolean isValid(String s) {\n    Deque<Character> st=new ArrayDeque<>();\n    for(char c:s.toCharArray()){\n        if(c=='('||c=='{'||c=='[') st.push(c);\n        else if(st.isEmpty()) return false;\n        else if(c==')'&&st.pop()!='(') return false;\n        else if(c=='}'&&st.pop()!='{') return false;\n        else if(c==']'&&st.pop()!='[') return false;\n    }\n    return st.isEmpty();\n}",
            "JavaScript": "var isValid = function(s) {\n    const st=[],m={')':'(','}':'{',']':'['};\n    for(const c of s){\n        if('({['.includes(c)) st.push(c);\n        else if(st.pop()!==m[c]) return false;\n    }\n    return st.length===0;\n};",
            "C++": "bool isValid(string s){\n    stack<char> st;\n    for(char c:s){\n        if(c=='('||c=='{'||c=='[') st.push(c);\n        else{\n            if(st.empty()) return false;\n            char t=st.top();st.pop();\n            if(c==')'&&t!='(') return false;\n            if(c=='}'&&t!='{') return false;\n            if(c==']'&&t!='[') return false;\n        }\n    }\n    return st.empty();\n}",
        },
        "Binary Search": {
            "Python": "def search(nums, target):\n    l,r=0,len(nums)-1\n    while l<=r:\n        mid=(l+r)//2\n        if nums[mid]==target: return mid\n        elif nums[mid]<target: l=mid+1\n        else: r=mid-1\n    return -1",
            "Java": "public int search(int[] nums,int target){\n    int l=0,r=nums.length-1;\n    while(l<=r){\n        int mid=l+(r-l)/2;\n        if(nums[mid]==target) return mid;\n        else if(nums[mid]<target) l=mid+1;\n        else r=mid-1;\n    }\n    return -1;\n}",
            "JavaScript": "var search = function(nums,target){\n    let l=0,r=nums.length-1;\n    while(l<=r){\n        const mid=(l+r)>>1;\n        if(nums[mid]===target) return mid;\n        else if(nums[mid]<target) l=mid+1;\n        else r=mid-1;\n    }\n    return -1;\n};",
            "C++": "int search(vector<int>& nums,int target){\n    int l=0,r=nums.size()-1;\n    while(l<=r){\n        int mid=l+(r-l)/2;\n        if(nums[mid]==target) return mid;\n        else if(nums[mid]<target) l=mid+1;\n        else r=mid-1;\n    }\n    return -1;\n}",
        },
        "Maximum Subarray": {
            "Python": "def maxSubArray(nums):\n    mx=cur=nums[0]\n    for n in nums[1:]:\n        cur=max(n,cur+n)\n        mx=max(mx,cur)\n    return mx",
            "Java": "public int maxSubArray(int[] nums){\n    int mx=nums[0],cur=nums[0];\n    for(int i=1;i<nums.length;i++){\n        cur=Math.max(nums[i],cur+nums[i]);\n        mx=Math.max(mx,cur);\n    }\n    return mx;\n}",
            "JavaScript": "var maxSubArray=function(nums){\n    let mx=nums[0],cur=nums[0];\n    for(let i=1;i<nums.length;i++){\n        cur=Math.max(nums[i],cur+nums[i]);\n        mx=Math.max(mx,cur);\n    }\n    return mx;\n};",
            "C++": "int maxSubArray(vector<int>& nums){\n    int mx=nums[0],cur=nums[0];\n    for(int i=1;i<(int)nums.size();i++){\n        cur=max(nums[i],cur+nums[i]);\n        mx=max(mx,cur);\n    }\n    return mx;\n}",
        },
        "Climbing Stairs": {
            "Python": "def climbStairs(n):\n    if n<=2: return n\n    a,b=1,2\n    for _ in range(3,n+1): a,b=b,a+b\n    return b",
            "Java": "public int climbStairs(int n){\n    if(n<=2) return n;\n    int a=1,b=2;\n    for(int i=3;i<=n;i++){int c=a+b;a=b;b=c;}\n    return b;\n}",
            "JavaScript": "var climbStairs=function(n){\n    if(n<=2) return n;\n    let[a,b]=[1,2];\n    for(let i=3;i<=n;i++)[a,b]=[b,a+b];\n    return b;\n};",
            "C++": "int climbStairs(int n){\n    if(n<=2) return n;\n    int a=1,b=2;\n    for(int i=3;i<=n;i++){int c=a+b;a=b;b=c;}\n    return b;\n}",
        },
        "Contains Duplicate": {
            "Python": "def containsDuplicate(nums):\n    return len(nums)!=len(set(nums))",
            "Java": "public boolean containsDuplicate(int[] nums){\n    Set<Integer> s=new HashSet<>();\n    for(int n:nums) if(!s.add(n)) return true;\n    return false;\n}",
            "JavaScript": "var containsDuplicate=function(nums){\n    return new Set(nums).size!==nums.length;\n};",
            "C++": "bool containsDuplicate(vector<int>& nums){\n    return unordered_set<int>(nums.begin(),nums.end()).size()!=nums.size();\n}",
        },
        "Single Number": {
            "Python": "def singleNumber(nums):\n    res=0\n    for n in nums: res^=n\n    return res",
            "Java": "public int singleNumber(int[] nums){\n    int r=0;\n    for(int n:nums) r^=n;\n    return r;\n}",
            "JavaScript": "var singleNumber=function(nums){\n    return nums.reduce((a,b)=>a^b,0);\n};",
            "C++": "int singleNumber(vector<int>& nums){\n    int r=0;\n    for(int n:nums) r^=n;\n    return r;\n}",
        },
        "Best Time to Buy and Sell Stock": {
            "Python": "def maxProfit(prices):\n    mn,prof=float('inf'),0\n    for p in prices:\n        mn=min(mn,p)\n        prof=max(prof,p-mn)\n    return prof",
            "Java": "public int maxProfit(int[] p){\n    int mn=Integer.MAX_VALUE,prof=0;\n    for(int x:p){mn=Math.min(mn,x);prof=Math.max(prof,x-mn);}\n    return prof;\n}",
            "JavaScript": "var maxProfit=function(prices){\n    let mn=Infinity,prof=0;\n    for(const p of prices){mn=Math.min(mn,p);prof=Math.max(prof,p-mn);}\n    return prof;\n};",
            "C++": "int maxProfit(vector<int>& p){\n    int mn=INT_MAX,prof=0;\n    for(int x:p){mn=min(mn,x);prof=max(prof,x-mn);}\n    return prof;\n}",
        },
        "Reverse Linked List": {
            "Python": "def reverseList(head):\n    prev=None\n    while head:\n        nxt=head.next; head.next=prev; prev=head; head=nxt\n    return prev",
            "Java": "public ListNode reverseList(ListNode h){\n    ListNode p=null;\n    while(h!=null){ListNode n=h.next;h.next=p;p=h;h=n;}\n    return p;\n}",
            "JavaScript": "var reverseList=function(h){\n    let p=null;\n    while(h){[h.next,p,h]=[p,h,h.next];}\n    return p;\n};",
            "C++": "ListNode* reverseList(ListNode* h){\n    ListNode* p=nullptr;\n    while(h){auto n=h->next;h->next=p;p=h;h=n;}\n    return p;\n}",
        },
        "Longest Substring Without Repeating Characters": {
            "Python": "def lengthOfLongestSubstring(s):\n    seen=set(); l=mx=0\n    for r in range(len(s)):\n        while s[r] in seen: seen.remove(s[l]);l+=1\n        seen.add(s[r]); mx=max(mx,r-l+1)\n    return mx",
            "Java": "public int lengthOfLongestSubstring(String s){\n    Set<Character> set=new HashSet<>();\n    int l=0,mx=0;\n    for(int r=0;r<s.length();r++){\n        while(set.contains(s.charAt(r))) set.remove(s.charAt(l++));\n        set.add(s.charAt(r)); mx=Math.max(mx,r-l+1);\n    }\n    return mx;\n}",
            "JavaScript": "var lengthOfLongestSubstring=function(s){\n    const set=new Set();let l=0,mx=0;\n    for(let r=0;r<s.length;r++){\n        while(set.has(s[r])) set.delete(s[l++]);\n        set.add(s[r]); mx=Math.max(mx,r-l+1);\n    }\n    return mx;\n};",
            "C++": "int lengthOfLongestSubstring(string s){\n    unordered_set<char> st;int l=0,mx=0;\n    for(int r=0;r<(int)s.size();r++){\n        while(st.count(s[r])) st.erase(s[l++]);\n        st.insert(s[r]); mx=max(mx,r-l+1);\n    }\n    return mx;\n}",
        },
        "Coin Change": {
            "Python": "def coinChange(coins,amount):\n    dp=[float('inf')]*(amount+1); dp[0]=0\n    for i in range(1,amount+1):\n        for c in coins:\n            if c<=i: dp[i]=min(dp[i],dp[i-c]+1)\n    return dp[amount] if dp[amount]!=float('inf') else -1",
            "Java": "public int coinChange(int[] coins,int amount){\n    int[] dp=new int[amount+1];\n    Arrays.fill(dp,amount+1); dp[0]=0;\n    for(int i=1;i<=amount;i++)\n        for(int c:coins) if(c<=i) dp[i]=Math.min(dp[i],dp[i-c]+1);\n    return dp[amount]>amount?-1:dp[amount];\n}",
            "JavaScript": "var coinChange=function(coins,amount){\n    const dp=new Array(amount+1).fill(Infinity); dp[0]=0;\n    for(let i=1;i<=amount;i++)\n        for(const c of coins) if(c<=i) dp[i]=Math.min(dp[i],dp[i-c]+1);\n    return dp[amount]===Infinity?-1:dp[amount];\n};",
            "C++": "int coinChange(vector<int>& coins,int amount){\n    vector<int> dp(amount+1,amount+1); dp[0]=0;\n    for(int i=1;i<=amount;i++)\n        for(int c:coins) if(c<=i) dp[i]=min(dp[i],dp[i-c]+1);\n    return dp[amount]>amount?-1:dp[amount];\n}",
        },
        "Trapping Rain Water": {
            "Python": "def trap(h):\n    l,r=0,len(h)-1; lm=rm=w=0\n    while l<r:\n        if h[l]<h[r]:\n            lm=max(lm,h[l]); w+=lm-h[l]; l+=1\n        else:\n            rm=max(rm,h[r]); w+=rm-h[r]; r-=1\n    return w",
            "Java": "public int trap(int[] h){\n    int l=0,r=h.length-1,lm=0,rm=0,w=0;\n    while(l<r){\n        if(h[l]<h[r]){lm=Math.max(lm,h[l]);w+=lm-h[l];l++;}\n        else{rm=Math.max(rm,h[r]);w+=rm-h[r];r--;}\n    }\n    return w;\n}",
            "JavaScript": "var trap=function(h){\n    let l=0,r=h.length-1,lm=0,rm=0,w=0;\n    while(l<r){\n        if(h[l]<h[r]){lm=Math.max(lm,h[l]);w+=lm-h[l];l++;}\n        else{rm=Math.max(rm,h[r]);w+=rm-h[r];r--;}\n    }\n    return w;\n};",
            "C++": "int trap(vector<int>& h){\n    int l=0,r=h.size()-1,lm=0,rm=0,w=0;\n    while(l<r){\n        if(h[l]<h[r]){lm=max(lm,h[l]);w+=lm-h[l];l++;}\n        else{rm=max(rm,h[r]);w+=rm-h[r];r--;}\n    }\n    return w;\n}",
        },
        "LRU Cache": {
            "Python": "from collections import OrderedDict\nclass LRUCache:\n    def __init__(self,cap): self.cap=cap; self.c=OrderedDict()\n    def get(self,k):\n        if k not in self.c: return -1\n        self.c.move_to_end(k); return self.c[k]\n    def put(self,k,v):\n        if k in self.c: self.c.move_to_end(k)\n        self.c[k]=v\n        if len(self.c)>self.cap: self.c.popitem(last=False)",
            "Java": "class LRUCache extends LinkedHashMap<Integer,Integer>{\n    int cap;\n    public LRUCache(int c){super(c,0.75f,true);cap=c;}\n    public int get(int k){return super.getOrDefault(k,-1);}\n    public void put(int k,int v){super.put(k,v);}\n    protected boolean removeEldestEntry(Map.Entry e){return size()>cap;}\n}",
            "JavaScript": "class LRUCache{\n    constructor(cap){this.cap=cap;this.map=new Map();}\n    get(k){\n        if(!this.map.has(k)) return -1;\n        const v=this.map.get(k);this.map.delete(k);this.map.set(k,v);return v;\n    }\n    put(k,v){\n        this.map.delete(k);this.map.set(k,v);\n        if(this.map.size>this.cap) this.map.delete(this.map.keys().next().value);\n    }\n}",
            "C++": "class LRUCache{\n    int cap;\n    list<pair<int,int>> lst;\n    unordered_map<int,list<pair<int,int>>::iterator> mp;\npublic:\n    LRUCache(int c):cap(c){}\n    int get(int k){\n        if(!mp.count(k)) return -1;\n        lst.splice(lst.begin(),lst,mp[k]); return mp[k]->second;\n    }\n    void put(int k,int v){\n        if(mp.count(k)) lst.erase(mp[k]);\n        lst.push_front({k,v}); mp[k]=lst.begin();\n        if((int)lst.size()>cap){mp.erase(lst.back().first);lst.pop_back();}\n    }\n};",
        },
        "Palindrome Number": {
            "Python": "def isPalindrome(x):\n    if x<0 or (x%10==0 and x!=0): return False\n    rev=0\n    while x>rev: rev=rev*10+x%10; x//=10\n    return x==rev or x==rev//10",
            "Java": "public boolean isPalindrome(int x){\n    if(x<0||(x%10==0&&x!=0)) return false;\n    int r=0;\n    while(x>r){r=r*10+x%10;x/=10;}\n    return x==r||x==r/10;\n}",
            "JavaScript": "var isPalindrome=function(x){\n    if(x<0||(x%10===0&&x!==0)) return false;\n    let r=0;\n    while(x>r){r=r*10+x%10;x=Math.floor(x/10);}\n    return x===r||x===Math.floor(r/10);\n};",
            "C++": "bool isPalindrome(int x){\n    if(x<0||(x%10==0&&x!=0)) return false;\n    int r=0;\n    while(x>r){r=r*10+x%10;x/=10;}\n    return x==r||x==r/10;\n}",
        },
        "Fizz Buzz": {
            "Python": "def fizzBuzz(n):\n    res=[]\n    for i in range(1,n+1):\n        if i%15==0: res.append('FizzBuzz')\n        elif i%3==0: res.append('Fizz')\n        elif i%5==0: res.append('Buzz')\n        else: res.append(str(i))\n    return res",
            "Java": "public List<String> fizzBuzz(int n){\n    List<String> r=new ArrayList<>();\n    for(int i=1;i<=n;i++){\n        if(i%15==0) r.add(\"FizzBuzz\");\n        else if(i%3==0) r.add(\"Fizz\");\n        else if(i%5==0) r.add(\"Buzz\");\n        else r.add(String.valueOf(i));\n    }\n    return r;\n}",
            "JavaScript": "var fizzBuzz=function(n){\n    const r=[];\n    for(let i=1;i<=n;i++){\n        if(i%15===0) r.push('FizzBuzz');\n        else if(i%3===0) r.push('Fizz');\n        else if(i%5===0) r.push('Buzz');\n        else r.push(String(i));\n    }\n    return r;\n};",
            "C++": "vector<string> fizzBuzz(int n){\n    vector<string> r;\n    for(int i=1;i<=n;i++){\n        if(i%15==0) r.push_back(\"FizzBuzz\");\n        else if(i%3==0) r.push_back(\"Fizz\");\n        else if(i%5==0) r.push_back(\"Buzz\");\n        else r.push_back(to_string(i));\n    }\n    return r;\n}",
        },
        "Merge Sorted Arrays": {
            "Python": "def merge(n1,m,n2,n):\n    i,j,k=m-1,n-1,m+n-1\n    while i>=0 and j>=0:\n        if n1[i]>n2[j]: n1[k]=n1[i];i-=1\n        else: n1[k]=n2[j];j-=1\n        k-=1\n    while j>=0: n1[k]=n2[j];j-=1;k-=1",
            "Java": "public void merge(int[] n1,int m,int[] n2,int n){\n    int i=m-1,j=n-1,k=m+n-1;\n    while(i>=0&&j>=0) n1[k--]=n1[i]>n2[j]?n1[i--]:n2[j--];\n    while(j>=0) n1[k--]=n2[j--];\n}",
            "JavaScript": "var merge=function(n1,m,n2,n){\n    let i=m-1,j=n-1,k=m+n-1;\n    while(i>=0&&j>=0) n1[k--]=n1[i]>n2[j]?n1[i--]:n2[j--];\n    while(j>=0) n1[k--]=n2[j--];\n};",
            "C++": "void merge(vector<int>& n1,int m,vector<int>& n2,int n){\n    int i=m-1,j=n-1,k=m+n-1;\n    while(i>=0&&j>=0) n1[k--]=n1[i]>n2[j]?n1[i--]:n2[j--];\n    while(j>=0) n1[k--]=n2[j--];\n}",
        },
        "Symmetric Tree": {
            "Python": "def isSymmetric(root):\n    def mirror(l,r):\n        if not l and not r: return True\n        if not l or not r: return False\n        return l.val==r.val and mirror(l.left,r.right) and mirror(l.right,r.left)\n    return mirror(root.left,root.right)",
            "Java": "public boolean isSymmetric(TreeNode root){\n    return mirror(root.left,root.right);\n}\nbool mirror(TreeNode l,TreeNode r){\n    if(l==null&&r==null) return true;\n    if(l==null||r==null) return false;\n    return l.val==r.val&&mirror(l.left,r.right)&&mirror(l.right,r.left);\n}",
            "JavaScript": "var isSymmetric=function(root){\n    const mirror=(l,r)=>{\n        if(!l&&!r) return true;\n        if(!l||!r) return false;\n        return l.val===r.val&&mirror(l.left,r.right)&&mirror(l.right,r.left);\n    };\n    return mirror(root.left,root.right);\n};",
            "C++": "bool mirror(TreeNode* l,TreeNode* r){\n    if(!l&&!r) return true;\n    if(!l||!r) return false;\n    return l->val==r->val&&mirror(l->left,r->right)&&mirror(l->right,r->left);\n}\nbool isSymmetric(TreeNode* root){return mirror(root->left,root->right);}",
        },
        "Maximum Depth of Binary Tree": {
            "Python": "def maxDepth(root):\n    if not root: return 0\n    return 1+max(maxDepth(root.left),maxDepth(root.right))",
            "Java": "public int maxDepth(TreeNode root){\n    if(root==null) return 0;\n    return 1+Math.max(maxDepth(root.left),maxDepth(root.right));\n}",
            "JavaScript": "var maxDepth=function(root){\n    if(!root) return 0;\n    return 1+Math.max(maxDepth(root.left),maxDepth(root.right));\n};",
            "C++": "int maxDepth(TreeNode* root){\n    if(!root) return 0;\n    return 1+max(maxDepth(root->left),maxDepth(root->right));\n}",
        },
    }
    for title, sols in MULTILANG.items():
        c.execute(
            "UPDATE coding_questions SET solutions_json=? WHERE title=? AND (solutions_json IS NULL OR solutions_json='')",
            (_json.dumps(sols), title)
        )

COMPANY_QUESTIONS = {
    "Google": {
        "Behavioral": [
            "Tell me about a time you had to work under tight deadlines.",
            "Describe a situation where you disagreed with a team decision.",
            "Give an example of a technically complex problem you solved.",
            "Tell me about a time you had to learn something new quickly.",
            "Describe your biggest professional failure and what you learned.",
            "Tell me about a project where you had significant ambiguity.",
            "How do you handle working with people who have different working styles?",
        ],
        "Technical": [
            "How would you design Google Search autocomplete?",
            "Explain the difference between process and thread.",
            "How does PageRank algorithm work?",
            "Design a system to store and retrieve billions of web pages.",
            "What happens when you type a URL into a browser?",
            "How would you design Google Maps routing?",
            "Explain consistent hashing and when you would use it.",
        ],
    },
    "Amazon": {
        "Behavioral": [
            "Tell me about a time you showed customer obsession.",
            "Describe a situation where you had to deliver results under pressure.",
            "Give an example of taking ownership beyond your job description.",
            "Describe a time you had to make a decision with incomplete data.",
            "Tell me about a time you influenced without authority.",
            "Give an example of a time you failed and what you did about it.",
            "Describe a time you invented a creative solution to a hard problem.",
        ],
        "Technical": [
            "Design Amazon's recommendation system.",
            "How would you implement a distributed queue like SQS?",
            "Explain CAP theorem with an example.",
            "How would you design a URL shortener like bit.ly?",
            "What is eventual consistency and when would you use it?",
            "Design a rate limiter for an API.",
            "How would you design DynamoDB's partition key strategy?",
        ],
    },
    "Microsoft": {
        "Behavioral": [
            "Why do you want to work at Microsoft?",
            "Tell me about a time you collaborated cross-functionally.",
            "Describe a project you're most proud of.",
            "How do you handle conflicting priorities?",
            "Give an example of mentoring a junior colleague.",
            "Tell me about a time you drove a culture change.",
            "Describe a situation where you had to adapt to major change.",
        ],
        "Technical": [
            "Design Microsoft Teams' video calling architecture.",
            "Explain garbage collection in .NET/Java.",
            "How would you design Azure's auto-scaling feature?",
            "Describe the SOLID principles with examples.",
            "How does a hash table handle collisions?",
            "Explain the difference between TCP and UDP.",
            "Design a distributed file system like HDFS.",
        ],
    },
    "Meta": {
        "Behavioral": [
            "Tell me about a time you made a product decision based on data.",
            "How have you handled working across multiple time zones?",
            "Describe a time you had to move fast and broke something.",
            "Tell me about a large-scale system you built or improved.",
            "How do you balance shipping fast vs. doing it right?",
        ],
        "Technical": [
            "How would you design Facebook's News Feed?",
            "Explain how React's reconciliation algorithm works.",
            "How would you design Instagram's photo storage?",
            "Describe distributed locking mechanisms.",
            "How does Facebook handle 2 billion users efficiently?",
        ],
    },
    "TCS": {
        "Behavioral": [
            "Tell me about yourself.",
            "What are your greatest strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Describe a challenging project you completed.",
            "How do you manage work-life balance on tight projects?",
            "Why do you want to join TCS?",
            "How do you handle pressure and tight deadlines?",
        ],
        "Technical": [
            "Explain the SDLC phases.",
            "What is polymorphism? Give an example.",
            "Explain normalization in databases.",
            "What is REST API and its principles?",
            "Describe Agile vs Waterfall methodology.",
            "Explain the concept of multithreading.",
            "What is the difference between SQL and NoSQL databases?",
        ],
    },
    "Infosys": {
        "Behavioral": [
            "Tell me about your internship or project experience.",
            "How do you handle criticism from a manager?",
            "Describe a time you worked in a diverse team.",
            "What motivates you professionally?",
            "Give an example of problem-solving under pressure.",
            "Why Infosys over other companies?",
            "How have you contributed to team success?",
        ],
        "Technical": [
            "What is object-oriented programming?",
            "Explain TCP/IP model vs OSI model.",
            "What are design patterns? Name three.",
            "Explain the difference between SQL and NoSQL.",
            "What is cloud computing and its service models?",
            "Explain microservices architecture.",
            "What is Docker and how does containerization work?",
        ],
    },
}

# ─── Role-Based Question Banks ─────────────────────────────────────────────────

ROLE_QUESTIONS = {
    "software engineer": [
        "Walk me through how you would design a scalable REST API.",
        "How do you ensure code quality and maintainability?",
        "Describe your debugging process for a production issue.",
        "What is the difference between horizontal and vertical scaling?",
        "How do you approach system design trade-offs (consistency vs availability)?",
        "Explain SOLID principles and give examples of each.",
        "What design patterns have you used in production?",
        "How do you handle database migrations in a live system?",
        "Describe your experience with CI/CD pipelines.",
        "How do you perform code reviews effectively?",
    ],
    "data scientist": [
        "How do you handle class imbalance in a dataset?",
        "Explain the bias-variance tradeoff.",
        "Walk me through your model deployment process.",
        "How do you validate a machine learning model?",
        "Explain the difference between L1 and L2 regularization.",
        "What is feature engineering and give examples?",
        "How would you detect and handle outliers in data?",
        "Explain gradient boosting and how it differs from random forest.",
        "How do you communicate model results to non-technical stakeholders?",
        "Describe an end-to-end ML project you've worked on.",
    ],
    "data analyst": [
        "How do you approach a new dataset for the first time?",
        "Explain the difference between SQL window functions and GROUP BY.",
        "How have you used data to drive a business decision?",
        "Describe your experience with data visualization tools.",
        "How do you ensure data quality and integrity?",
        "What is A/B testing and how do you design one?",
        "Explain cohort analysis with an example.",
        "How do you handle missing values in data?",
        "Describe a complex SQL query you've written.",
        "How do you translate business requirements into analytical questions?",
    ],
    "frontend developer": [
        "Explain the browser rendering pipeline.",
        "What is the Virtual DOM and why does React use it?",
        "How do you optimize web page performance?",
        "Explain CSS specificity and how it works.",
        "What are Web Accessibility (WCAG) guidelines and why do they matter?",
        "How do you handle state management in a large React application?",
        "Explain HTTP/2 and its advantages over HTTP/1.1.",
        "How do you implement responsive design?",
        "What is lazy loading and when would you use it?",
        "Describe your experience with testing React components.",
    ],
    "backend developer": [
        "How do you design a RESTful API?",
        "Explain the differences between SQL and NoSQL databases.",
        "How would you optimize a slow database query?",
        "Describe your approach to API authentication and authorization.",
        "What is caching and what strategies have you used?",
        "How do you handle concurrent requests safely?",
        "Explain message queues and when you would use them.",
        "How do you implement rate limiting for an API?",
        "Describe your experience with microservices.",
        "How do you ensure backwards compatibility in API changes?",
    ],
    "devops engineer": [
        "Explain Infrastructure as Code and tools you've used.",
        "How do you design a CI/CD pipeline from scratch?",
        "Describe your experience with Kubernetes orchestration.",
        "How do you handle secrets management in production?",
        "Explain the concept of blue-green deployment.",
        "How do you monitor and alert on production systems?",
        "Describe how you've improved system reliability.",
        "What is site reliability engineering?",
        "How do you approach disaster recovery planning?",
        "Explain container security best practices.",
    ],
    "machine learning engineer": [
        "How do you take a model from research to production?",
        "Explain model drift and how you detect and handle it.",
        "What is feature store and why is it important?",
        "How would you design an ML training pipeline?",
        "Explain the difference between online and offline inference.",
        "How do you handle data versioning in ML?",
        "What is MLOps and what tools have you used?",
        "How do you monitor model performance in production?",
        "Describe your experience with distributed training.",
        "How do you approach A/B testing for ML models?",
    ],
    "product manager": [
        "How do you prioritize features when everything is urgent?",
        "Walk me through how you would design a product from scratch.",
        "How do you define success metrics for a new feature?",
        "Describe a time you had to make a tough product trade-off.",
        "How do you work with engineers and designers?",
        "What frameworks do you use for product strategy?",
        "How do you gather and act on user feedback?",
        "Describe a product you admire and why.",
        "How do you handle stakeholder conflicts?",
        "Walk me through your product launch process.",
    ],
    "full stack developer": [
        "How do you decide between server-side and client-side rendering?",
        "Describe your experience with REST vs GraphQL APIs.",
        "How do you handle authentication across frontend and backend?",
        "What is CORS and how do you handle it?",
        "Describe your database schema design process.",
        "How do you debug a bug that only appears in production?",
        "Explain the concept of web sockets and use cases.",
        "How do you handle file uploads in a web application?",
        "Describe your approach to responsive mobile design.",
        "How do you ensure security in a web application (OWASP)?",
    ],
    "android developer": [
        "Explain the Android Activity lifecycle.",
        "What is the difference between Service and IntentService?",
        "How does Android handle memory management?",
        "Explain Jetpack Compose vs XML layouts.",
        "How do you implement background processing in Android?",
        "What is ViewModel and why is it important?",
        "Explain content providers and when you would use them.",
        "How do you optimize app performance and battery usage?",
        "Describe your experience with Android testing.",
        "How do you handle different screen sizes and densities?",
    ],
    "ios developer": [
        "Explain the iOS app lifecycle.",
        "What is the difference between strong, weak, and unowned references?",
        "Explain ARC (Automatic Reference Counting).",
        "What is Swift's async/await model?",
        "How do you implement push notifications in iOS?",
        "Explain SwiftUI vs UIKit and when to use each.",
        "How do you handle data persistence in iOS apps?",
        "What is Combine framework and how does it work?",
        "Describe your App Store submission experience.",
        "How do you debug memory leaks in iOS?",
    ],
    "cloud architect": [
        "How do you design a highly available cloud architecture?",
        "Explain multi-region deployment strategies.",
        "How do you approach cloud cost optimization?",
        "Describe your experience with serverless architecture.",
        "How do you handle data sovereignty requirements?",
        "Explain the shared responsibility model in cloud security.",
        "How do you design for disaster recovery in the cloud?",
        "Describe a cloud migration project you led.",
        "How do you choose between different cloud services for the same task?",
        "Explain cloud networking (VPC, subnets, security groups).",
    ],
    "cybersecurity engineer": [
        "Explain the CIA triad in security.",
        "How do you perform a threat modeling exercise?",
        "What is zero-trust architecture?",
        "Describe common web vulnerabilities (OWASP Top 10).",
        "How do you respond to a security incident?",
        "Explain penetration testing methodology.",
        "What is PKI and how does it work?",
        "How do you secure a CI/CD pipeline?",
        "Describe your experience with SIEM tools.",
        "How do you handle vulnerability disclosure?",
    ],
}

SKILL_QUESTIONS = {
    "python": [
        "Explain Python's GIL and its implications for multithreading.",
        "What is the difference between list, tuple, and set?",
        "How does Python's memory management and garbage collection work?",
        "Explain decorators with a real-world example.",
        "What are generators and when would you use them over lists?",
        "Explain the difference between @staticmethod and @classmethod.",
        "What are context managers and how do you create one?",
        "Explain Python's descriptor protocol.",
        "What is the difference between *args and **kwargs?",
        "How do you handle concurrency in Python (threading vs asyncio)?",
    ],
    "java": [
        "Explain JVM, JRE, and JDK and how they relate.",
        "What is the difference between abstract class and interface in Java?",
        "How does Java handle memory management (heap, stack, GC)?",
        "Explain multithreading and synchronization in Java.",
        "What are Java 8 streams and lambdas? Give examples.",
        "Explain the Java Collections Framework.",
        "What is the difference between ArrayList and LinkedList?",
        "Explain Java's Optional and how it prevents NullPointerException.",
        "What are Java annotations and how do you create custom ones?",
        "Explain Spring Boot's dependency injection.",
    ],
    "javascript": [
        "Explain the event loop in JavaScript in detail.",
        "What is a closure and give a practical example?",
        "Explain the difference between == and ===.",
        "What are Promises, async/await? How do they relate?",
        "Explain prototypal inheritance vs classical inheritance.",
        "What is the difference between var, let, and const?",
        "Explain hoisting in JavaScript.",
        "What are WeakMap and WeakSet used for?",
        "How does the 'this' keyword work in different contexts?",
        "Explain debouncing and throttling with examples.",
    ],
    "typescript": [
        "What is the difference between TypeScript interface and type?",
        "Explain generics in TypeScript with an example.",
        "What are TypeScript utility types (Partial, Required, Pick)?",
        "How does TypeScript's type inference work?",
        "Explain union and intersection types.",
        "What are decorators in TypeScript?",
        "How does TypeScript handle null and undefined (strict mode)?",
        "Explain mapped types in TypeScript.",
    ],
    "sql": [
        "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?",
        "Explain indexing and when to use composite indexes.",
        "What is a transaction and explain ACID properties.",
        "Difference between WHERE and HAVING clause?",
        "Explain window functions (ROW_NUMBER, RANK, LEAD, LAG) with examples.",
        "What is query optimization? How does EXPLAIN work?",
        "Explain the difference between UNION and UNION ALL.",
        "What are CTEs (Common Table Expressions) and when to use them?",
        "Explain database normalization up to 3NF.",
        "How do you handle NULL values in SQL?",
    ],
    "machine learning": [
        "Explain overfitting, underfitting, and how to prevent each.",
        "What is the difference between supervised, unsupervised, and reinforcement learning?",
        "Explain gradient descent (SGD, Mini-batch, Adam optimizer).",
        "What is cross-validation and why is it important?",
        "Describe the bias-variance tradeoff.",
        "Explain Random Forest vs Gradient Boosting vs XGBoost.",
        "What is regularization (L1/L2) and when do you use each?",
        "How do you handle imbalanced datasets?",
        "Explain confusion matrix, precision, recall, F1 score.",
        "What is the difference between bagging and boosting?",
    ],
    "react": [
        "What is the Virtual DOM and how does reconciliation work?",
        "Explain React hooks (useState, useEffect, useCallback, useMemo).",
        "What is the difference between props and state?",
        "Explain React's reconciliation algorithm (Fiber).",
        "What are higher-order components vs render props vs hooks?",
        "Explain React Context API and when to use vs Redux.",
        "What is code splitting and lazy loading in React?",
        "Explain React performance optimization techniques.",
        "What are controlled vs uncontrolled components?",
        "How does React handle forms and form validation?",
    ],
    "aws": [
        "What is the difference between EC2, Lambda, and ECS?",
        "Explain S3 storage classes and lifecycle policies.",
        "What is VPC, subnets, NAT gateway, and security groups?",
        "How does AWS auto-scaling work (target tracking vs step scaling)?",
        "Explain IAM roles, policies, and permission boundaries.",
        "What is the difference between SQS and SNS?",
        "How does AWS CloudFormation/CDK work for IaC?",
        "Explain RDS vs DynamoDB and when to choose each.",
        "What is AWS ElastiCache and when would you use it?",
        "How does AWS WAF protect applications?",
    ],
    "docker": [
        "What is the difference between a container and a virtual machine?",
        "Explain Docker networking (bridge, host, overlay).",
        "What is a Dockerfile and best practices for writing one?",
        "Explain Docker Compose and multi-container applications.",
        "What are Docker volumes vs bind mounts?",
        "Explain Docker image layers and caching.",
        "How do you secure Docker containers?",
        "What is the difference between CMD and ENTRYPOINT?",
    ],
    "kubernetes": [
        "Explain Kubernetes architecture (control plane vs worker nodes).",
        "What is the difference between Pod, Deployment, and StatefulSet?",
        "How does Kubernetes service discovery work?",
        "Explain Kubernetes ConfigMaps and Secrets.",
        "What is a Kubernetes Ingress and how does it work?",
        "Explain horizontal pod autoscaling.",
        "What are Kubernetes namespaces used for?",
        "How does Kubernetes handle rolling updates and rollbacks?",
        "Explain PersistentVolumes and PersistentVolumeClaims.",
        "What are Kubernetes RBAC policies?",
    ],
    "nodejs": [
        "Explain the Node.js event loop in detail.",
        "What is the difference between blocking and non-blocking I/O?",
        "How does Node.js handle CPU-intensive tasks?",
        "Explain Express.js middleware pattern.",
        "What is the difference between require() and import?",
        "How do you manage environment variables in Node.js?",
        "Explain streams in Node.js.",
        "How do you handle errors in async Node.js code?",
        "What is npm vs yarn vs pnpm?",
        "How do you cluster Node.js for multi-core usage?",
    ],
    "system design": [
        "How would you design a URL shortener like bit.ly?",
        "Design a rate limiter for a REST API.",
        "How would you design Twitter's timeline feature?",
        "Design a distributed cache like Memcached/Redis.",
        "How would you design an online food delivery system?",
        "Design a notification system that sends millions of messages per day.",
        "How would you design a ride-sharing service like Uber?",
        "Design a content delivery network (CDN).",
        "How would you design a real-time collaborative editor like Google Docs?",
        "Design a search autocomplete system.",
    ],
    "git": [
        "Explain the difference between git merge and git rebase.",
        "What is a git conflict and how do you resolve it?",
        "Explain git branching strategies (GitFlow, trunk-based).",
        "What is the difference between git reset and git revert?",
        "Explain git cherry-pick and when you would use it.",
        "What are git hooks and give a practical example?",
        "How do you squash commits?",
        "Explain git bisect for debugging.",
    ],
}

GENERAL_QUESTIONS = [
    "Tell me about yourself.",
    "Why are you interested in this role?",
    "Describe your most challenging project.",
    "How do you handle disagreements with team members?",
    "Where do you see yourself in 3 years?",
    "What is your greatest technical achievement?",
    "How do you stay updated with new technologies?",
    "Describe your ideal work environment.",
    "What is your approach to debugging a hard bug?",
    "How do you prioritize tasks when everything is urgent?",
    "Tell me about a time you failed and what you learned.",
    "How do you handle working under pressure?",
    "Describe a time you had to learn something quickly.",
    "What motivates you to do your best work?",
    "How do you give and receive feedback?",
]


def get_questions_for_skills(skills: list) -> list:
    """Return interview questions based on skills."""
    questions = list(GENERAL_QUESTIONS)
    for skill in skills:
        skill_lower = skill.lower().strip()
        for key, qs in SKILL_QUESTIONS.items():
            if key in skill_lower or skill_lower in key:
                questions.extend(qs)
    return list(dict.fromkeys(questions))


def get_questions_for_role(role: str, skills: list = None) -> list:
    """Return interview questions based on job role + skills."""
    questions = list(GENERAL_QUESTIONS)
    role_lower = role.lower().strip()

    # Match role
    for key, qs in ROLE_QUESTIONS.items():
        if key in role_lower or any(word in role_lower for word in key.split()):
            questions.extend(qs)
            break

    # Also add skill-based questions
    if skills:
        for skill in skills:
            skill_lower = skill.lower().strip()
            for key, qs in SKILL_QUESTIONS.items():
                if key in skill_lower or skill_lower in key:
                    questions.extend(qs[:5])

    # Fallback: software engineer questions if no role match
    if len(questions) <= len(GENERAL_QUESTIONS):
        questions.extend(ROLE_QUESTIONS.get("software engineer", []))

    return list(dict.fromkeys(questions))


def evaluate_answer(question: str, answer: str) -> dict:
    """NLP-based answer evaluation using keyword scoring + STAR detection."""
    if not answer or len(answer.strip()) < 20:
        return {"score": 10, "feedback": "Answer too short. Please provide more detail.", "keywords_found": []}

    answer_lower = answer.lower()
    word_count = len(answer.split())

    positive_keywords = [
        "because", "therefore", "result", "achieved", "improved", "implemented",
        "designed", "led", "collaborated", "resolved", "optimized", "reduced",
        "increased", "delivered", "example", "situation", "action", "impact",
        "team", "project", "solution", "challenge", "learned", "outcome",
    ]
    found = [k for k in positive_keywords if k in answer_lower]
    keyword_score = min(40, len(found) * 4)

    if word_count < 30:
        length_score = 15
    elif word_count < 80:
        length_score = 25
    elif word_count < 200:
        length_score = 35
    else:
        length_score = 25

    has_star = sum([
        any(w in answer_lower for w in ["situation", "context", "when", "during", "working on"]),
        any(w in answer_lower for w in ["task", "responsible", "goal", "needed", "my job"]),
        any(w in answer_lower for w in ["action", "decided", "implemented", "did", "took", "built"]),
        any(w in answer_lower for w in ["result", "outcome", "achieved", "impact", "reduced", "increased"]),
    ])
    structure_score = has_star * 5

    total = min(100, keyword_score + length_score + structure_score + 10)

    if total >= 80:
        feedback = "Excellent answer! Well-structured with clear examples and measurable impact."
    elif total >= 60:
        feedback = "Good answer. Consider adding specific metrics or a concrete outcome to strengthen it."
    elif total >= 40:
        feedback = "Decent start. Try using the STAR method (Situation, Task, Action, Result) for better structure."
    else:
        feedback = "Needs more detail. Use specific examples, context, and quantifiable results."

    return {"score": total, "feedback": feedback, "keywords_found": found}


def save_interview_session(user_id, session_type, company, role, skills, readiness_score=None):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO interview_sessions (user_id, session_type, company, role, skills, readiness_score) VALUES (?,?,?,?,?,?)",
        (user_id, session_type, company, role, ",".join(skills) if isinstance(skills, list) else skills, readiness_score)
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def save_interview_answer(session_id, question, answer, score, feedback):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO interview_answers (session_id, question, user_answer, score, feedback) VALUES (?,?,?,?,?)",
        (session_id, question, answer, score, feedback)
    )
    conn.commit()
    conn.close()


def get_user_interview_stats(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT ia.score, ia.answered_at
        FROM interview_answers ia
        JOIN interview_sessions s ON ia.session_id = s.id
        WHERE s.user_id = ?
        ORDER BY ia.answered_at DESC LIMIT 50
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
