"""
Coding Interview Practice Module
Features: Problem browser, difficulty filter, company filter,
          code editor area, hints, solution reveal, analytics
"""
import json
import sqlite3
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from interview.interview_data import init_interview_tables

DB_PATH = "resume_data.db"


# ── Per-language reference solutions ──────────────────────────────────────────
PROBLEM_SOLUTIONS = {
    "Two Sum": {
        "Python": (
            "def twoSum(nums, target):\n"
            "    seen = {}\n"
            "    for i, n in enumerate(nums):\n"
            "        diff = target - n\n"
            "        if diff in seen:\n"
            "            return [seen[diff], i]\n"
            "        seen[n] = i\n"
        ),
        "Java": (
            "import java.util.HashMap;\n"
            "public class Solution {\n"
            "    public int[] twoSum(int[] nums, int target) {\n"
            "        HashMap<Integer,Integer> map = new HashMap<>();\n"
            "        for (int i = 0; i < nums.length; i++) {\n"
            "            int diff = target - nums[i];\n"
            "            if (map.containsKey(diff)) return new int[]{map.get(diff), i};\n"
            "            map.put(nums[i], i);\n"
            "        }\n"
            "        return new int[]{};\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function twoSum(nums, target) {\n"
            "    const map = {};\n"
            "    for (let i = 0; i < nums.length; i++) {\n"
            "        const diff = target - nums[i];\n"
            "        if (map[diff] !== undefined) return [map[diff], i];\n"
            "        map[nums[i]] = i;\n"
            "    }\n"
            "}"
        ),
        "C++": (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n"
            "vector<int> twoSum(vector<int>& nums, int target) {\n"
            "    unordered_map<int,int> mp;\n"
            "    for (int i = 0; i < (int)nums.size(); i++) {\n"
            "        int diff = target - nums[i];\n"
            "        if (mp.count(diff)) return {mp[diff], i};\n"
            "        mp[nums[i]] = i;\n"
            "    }\n"
            "    return {};\n"
            "}"
        ),
    },
    "Contains Duplicate": {
        "Python": (
            "def containsDuplicate(nums):\n"
            "    return len(nums) != len(set(nums))\n"
        ),
        "Java": (
            "import java.util.HashSet;\n"
            "public class Solution {\n"
            "    public boolean containsDuplicate(int[] nums) {\n"
            "        HashSet<Integer> set = new HashSet<>();\n"
            "        for (int n : nums) {\n"
            "            if (!set.add(n)) return true;\n"
            "        }\n"
            "        return false;\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function containsDuplicate(nums) {\n"
            "    return new Set(nums).size !== nums.length;\n"
            "}"
        ),
        "C++": (
            "bool containsDuplicate(vector<int>& nums) {\n"
            "    unordered_set<int> s(nums.begin(), nums.end());\n"
            "    return s.size() != nums.size();\n"
            "}"
        ),
    },
    "Merge Sorted Arrays": {
        "Python": (
            "def merge(nums1, m, nums2, n):\n"
            "    i, j, k = m-1, n-1, m+n-1\n"
            "    while i >= 0 and j >= 0:\n"
            "        if nums1[i] > nums2[j]:\n"
            "            nums1[k] = nums1[i]; i -= 1\n"
            "        else:\n"
            "            nums1[k] = nums2[j]; j -= 1\n"
            "        k -= 1\n"
            "    while j >= 0:\n"
            "        nums1[k] = nums2[j]; j -= 1; k -= 1\n"
        ),
        "Java": (
            "public class Solution {\n"
            "    public void merge(int[] nums1, int m, int[] nums2, int n) {\n"
            "        int i = m-1, j = n-1, k = m+n-1;\n"
            "        while (i >= 0 && j >= 0)\n"
            "            nums1[k--] = nums1[i] > nums2[j] ? nums1[i--] : nums2[j--];\n"
            "        while (j >= 0) nums1[k--] = nums2[j--];\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function merge(nums1, m, nums2, n) {\n"
            "    let i = m-1, j = n-1, k = m+n-1;\n"
            "    while (i >= 0 && j >= 0)\n"
            "        nums1[k--] = nums1[i] > nums2[j] ? nums1[i--] : nums2[j--];\n"
            "    while (j >= 0) nums1[k--] = nums2[j--];\n"
            "}"
        ),
        "C++": (
            "void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {\n"
            "    int i=m-1, j=n-1, k=m+n-1;\n"
            "    while(i>=0 && j>=0)\n"
            "        nums1[k--] = nums1[i]>nums2[j] ? nums1[i--] : nums2[j--];\n"
            "    while(j>=0) nums1[k--]=nums2[j--];\n"
            "}"
        ),
    },
    "Climbing Stairs": {
        "Python": (
            "def climbStairs(n):\n"
            "    a, b = 1, 1\n"
            "    for _ in range(n-1):\n"
            "        a, b = b, a+b\n"
            "    return b\n"
        ),
        "Java": (
            "public class Solution {\n"
            "    public int climbStairs(int n) {\n"
            "        int a = 1, b = 1;\n"
            "        for (int i = 1; i < n; i++) {\n"
            "            int tmp = b; b = a+b; a = tmp;\n"
            "        }\n"
            "        return b;\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function climbStairs(n) {\n"
            "    let [a, b] = [1, 1];\n"
            "    for (let i = 1; i < n; i++) [a, b] = [b, a+b];\n"
            "    return b;\n"
            "}"
        ),
        "C++": (
            "int climbStairs(int n) {\n"
            "    int a=1, b=1;\n"
            "    for(int i=1;i<n;i++){int t=b;b=a+b;a=t;}\n"
            "    return b;\n"
            "}"
        ),
    },
    "Reverse Linked List": {
        "Python": (
            "def reverseList(head):\n"
            "    prev = None\n"
            "    while head:\n"
            "        nxt = head.next\n"
            "        head.next = prev\n"
            "        prev = head\n"
            "        head = nxt\n"
            "    return prev\n"
        ),
        "Java": (
            "public class Solution {\n"
            "    public ListNode reverseList(ListNode head) {\n"
            "        ListNode prev = null;\n"
            "        while (head != null) {\n"
            "            ListNode next = head.next;\n"
            "            head.next = prev;\n"
            "            prev = head;\n"
            "            head = next;\n"
            "        }\n"
            "        return prev;\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function reverseList(head) {\n"
            "    let prev = null;\n"
            "    while (head) {\n"
            "        let next = head.next;\n"
            "        head.next = prev;\n"
            "        prev = head;\n"
            "        head = next;\n"
            "    }\n"
            "    return prev;\n"
            "}"
        ),
        "C++": (
            "ListNode* reverseList(ListNode* head) {\n"
            "    ListNode* prev = nullptr;\n"
            "    while (head) {\n"
            "        auto* nxt = head->next;\n"
            "        head->next = prev;\n"
            "        prev = head;\n"
            "        head = nxt;\n"
            "    }\n"
            "    return prev;\n"
            "}"
        ),
    },
    "Best Time to Buy and Sell Stock": {
        "Python": (
            "def maxProfit(prices):\n"
            "    min_p, max_p = float('inf'), 0\n"
            "    for p in prices:\n"
            "        min_p = min(min_p, p)\n"
            "        max_p = max(max_p, p - min_p)\n"
            "    return max_p\n"
        ),
        "Java": (
            "public class Solution {\n"
            "    public int maxProfit(int[] prices) {\n"
            "        int minP = Integer.MAX_VALUE, maxP = 0;\n"
            "        for (int p : prices) {\n"
            "            minP = Math.min(minP, p);\n"
            "            maxP = Math.max(maxP, p - minP);\n"
            "        }\n"
            "        return maxP;\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function maxProfit(prices) {\n"
            "    let min = Infinity, max = 0;\n"
            "    for (const p of prices) {\n"
            "        min = Math.min(min, p);\n"
            "        max = Math.max(max, p - min);\n"
            "    }\n"
            "    return max;\n"
            "}"
        ),
        "C++": (
            "int maxProfit(vector<int>& prices) {\n"
            "    int mn = INT_MAX, mx = 0;\n"
            "    for (int p : prices) { mn = min(mn,p); mx = max(mx,p-mn); }\n"
            "    return mx;\n"
            "}"
        ),
    },
    "Fizz Buzz": {
        "Python": (
            "def fizzBuzz(n):\n"
            "    res = []\n"
            "    for i in range(1, n+1):\n"
            "        if i % 15 == 0: res.append('FizzBuzz')\n"
            "        elif i % 3 == 0: res.append('Fizz')\n"
            "        elif i % 5 == 0: res.append('Buzz')\n"
            "        else: res.append(str(i))\n"
            "    return res\n"
        ),
        "Java": (
            "import java.util.*;\n"
            "public class Solution {\n"
            "    public List<String> fizzBuzz(int n) {\n"
            "        List<String> res = new ArrayList<>();\n"
            "        for (int i=1;i<=n;i++)\n"
            "            res.add(i%15==0?\"FizzBuzz\":i%3==0?\"Fizz\":i%5==0?\"Buzz\":\"\"+i);\n"
            "        return res;\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function fizzBuzz(n) {\n"
            "    const res = [];\n"
            "    for (let i=1;i<=n;i++)\n"
            "        res.push(i%15===0?'FizzBuzz':i%3===0?'Fizz':i%5===0?'Buzz':''+i);\n"
            "    return res;\n"
            "}"
        ),
        "C++": (
            "vector<string> fizzBuzz(int n) {\n"
            "    vector<string> r;\n"
            "    for(int i=1;i<=n;i++)\n"
            "        r.push_back(i%15==0?\"FizzBuzz\":i%3==0?\"Fizz\":i%5==0?\"Buzz\":to_string(i));\n"
            "    return r;\n"
            "}"
        ),
    },
    "Single Number": {
        "Python": (
            "def singleNumber(nums):\n"
            "    res = 0\n"
            "    for n in nums:\n"
            "        res ^= n\n"
            "    return res\n"
        ),
        "Java": (
            "public class Solution {\n"
            "    public int singleNumber(int[] nums) {\n"
            "        int res = 0;\n"
            "        for (int n : nums) res ^= n;\n"
            "        return res;\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function singleNumber(nums) {\n"
            "    return nums.reduce((a, b) => a ^ b, 0);\n"
            "}"
        ),
        "C++": (
            "int singleNumber(vector<int>& nums) {\n"
            "    int r = 0;\n"
            "    for (int n : nums) r ^= n;\n"
            "    return r;\n"
            "}"
        ),
    },
    "Alien Dictionary": {
        "Python": (
            "from collections import defaultdict, deque\n"
            "def alienOrder(words):\n"
            "    adj={c:set() for w in words for c in w}\n"
            "    for i in range(len(words)-1):\n"
            "        w1,w2=words[i],words[i+1]\n"
            "        for c1,c2 in zip(w1,w2):\n"
            "            if c1!=c2: adj[c1].add(c2); break\n"
            "        else:\n"
            "            if len(w1)>len(w2): return ''\n"
            "    visited={}\n"
            "    res=[]\n"
            "    def dfs(c):\n"
            "        if c in visited: return visited[c]\n"
            "        visited[c]=True\n"
            "        for nb in adj[c]:\n"
            "            if dfs(nb): return True\n"
            "        visited[c]=False; res.append(c)\n"
            "    for c in adj:\n"
            "        if dfs(c): return ''\n"
            "    return ''.join(reversed(res))\n"
        ),
        "Java": (
            "import java.util.*;\n"
            "public class Solution {\n"
            "    public String alienOrder(String[] words) {\n"
            "        Map<Character,Set<Character>> adj = new HashMap<>();\n"
            "        Map<Character,Integer> inDeg = new HashMap<>();\n"
            "        for (String w : words) for (char c : w.toCharArray()) {\n"
            "            adj.putIfAbsent(c, new HashSet<>());\n"
            "            inDeg.putIfAbsent(c, 0);\n"
            "        }\n"
            "        for (int i=0;i<words.length-1;i++) {\n"
            "            String w1=words[i],w2=words[i+1];\n"
            "            int len=Math.min(w1.length(),w2.length());\n"
            "            if(w1.length()>w2.length()&&w1.startsWith(w2)) return \"\";\n"
            "            for(int j=0;j<len;j++) {\n"
            "                char c1=w1.charAt(j),c2=w2.charAt(j);\n"
            "                if(c1!=c2){\n"
            "                    if(!adj.get(c1).contains(c2)){\n"
            "                        adj.get(c1).add(c2);\n"
            "                        inDeg.merge(c2,1,Integer::sum);\n"
            "                    }\n"
            "                    break;\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "        Queue<Character> q=new LinkedList<>();\n"
            "        for(char c:inDeg.keySet()) if(inDeg.get(c)==0) q.add(c);\n"
            "        StringBuilder sb=new StringBuilder();\n"
            "        while(!q.isEmpty()){\n"
            "            char c=q.poll(); sb.append(c);\n"
            "            for(char nb:adj.get(c)){\n"
            "                inDeg.merge(nb,-1,Integer::sum);\n"
            "                if(inDeg.get(nb)==0) q.add(nb);\n"
            "            }\n"
            "        }\n"
            "        return sb.length()==inDeg.size()?sb.toString():\"\";\n"
            "    }\n"
            "}\n"
        ),
        "JavaScript": (
            "var alienOrder = function(words) {\n"
            "    const adj=new Map(), inDeg=new Map();\n"
            "    for(const w of words) for(const c of w){\n"
            "        if(!adj.has(c)) adj.set(c,new Set());\n"
            "        if(!inDeg.has(c)) inDeg.set(c,0);\n"
            "    }\n"
            "    for(let i=0;i<words.length-1;i++){\n"
            "        const w1=words[i],w2=words[i+1];\n"
            "        if(w1.length>w2.length&&w1.startsWith(w2)) return '';\n"
            "        for(let j=0;j<Math.min(w1.length,w2.length);j++){\n"
            "            if(w1[j]!==w2[j]){\n"
            "                if(!adj.get(w1[j]).has(w2[j])){\n"
            "                    adj.get(w1[j]).add(w2[j]);\n"
            "                    inDeg.set(w2[j],(inDeg.get(w2[j])||0)+1);\n"
            "                }\n"
            "                break;\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    const q=[...inDeg.keys()].filter(c=>inDeg.get(c)===0);\n"
            "    let res='';\n"
            "    while(q.length){\n"
            "        const c=q.shift(); res+=c;\n"
            "        for(const nb of adj.get(c)){\n"
            "            inDeg.set(nb,inDeg.get(nb)-1);\n"
            "            if(inDeg.get(nb)===0) q.push(nb);\n"
            "        }\n"
            "    }\n"
            "    return res.length===inDeg.size?res:'';\n"
            "};\n"
        ),
        "C++": (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n"
            "string alienOrder(vector<string>& words) {\n"
            "    map<char,set<char>> adj;\n"
            "    map<char,int> inDeg;\n"
            "    for(auto& w:words) for(char c:w){adj[c];inDeg[c];}\n"
            "    for(int i=0;i<(int)words.size()-1;i++){\n"
            "        auto& w1=words[i]; auto& w2=words[i+1];\n"
            "        if(w1.size()>w2.size()&&w1.substr(0,w2.size())==w2) return \"\";\n"
            "        for(int j=0;j<(int)min(w1.size(),w2.size());j++){\n"
            "            if(w1[j]!=w2[j]){\n"
            "                if(!adj[w1[j]].count(w2[j])){adj[w1[j]].insert(w2[j]);inDeg[w2[j]]++;}\n"
            "                break;\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    queue<char> q;\n"
            "    for(auto&[c,d]:inDeg) if(d==0) q.push(c);\n"
            "    string res;\n"
            "    while(!q.empty()){\n"
            "        char c=q.front();q.pop();res+=c;\n"
            "        for(char nb:adj[c]) if(--inDeg[nb]==0) q.push(nb);\n"
            "    }\n"
            "    return res.size()==inDeg.size()?res:\"\";\n"
            "}\n"
        ),
    },
    "Number of Islands": {
        "Python": (
            "def numIslands(grid):\n"
            "    def dfs(i,j):\n"
            "        if i<0 or i>=len(grid) or j<0 or j>=len(grid[0]) or grid[i][j]!='1': return\n"
            "        grid[i][j]='0'\n"
            "        for di,dj in [(0,1),(0,-1),(1,0),(-1,0)]: dfs(i+di,j+dj)\n"
            "    cnt=0\n"
            "    for i in range(len(grid)):\n"
            "        for j in range(len(grid[0])):\n"
            "            if grid[i][j]=='1': dfs(i,j); cnt+=1\n"
            "    return cnt\n"
        ),
        "Java": (
            "public int numIslands(char[][] grid) {\n"
            "    int cnt=0;\n"
            "    for(int i=0;i<grid.length;i++)\n"
            "        for(int j=0;j<grid[0].length;j++)\n"
            "            if(grid[i][j]=='1'){dfs(grid,i,j);cnt++;}\n"
            "    return cnt;\n"
            "}\n"
            "void dfs(char[][] g,int i,int j){\n"
            "    if(i<0||i>=g.length||j<0||j>=g[0].length||g[i][j]!='1') return;\n"
            "    g[i][j]='0';\n"
            "    dfs(g,i+1,j);dfs(g,i-1,j);dfs(g,i,j+1);dfs(g,i,j-1);\n"
            "}\n"
        ),
        "JavaScript": (
            "var numIslands = function(grid) {\n"
            "    const dfs=(i,j)=>{\n"
            "        if(i<0||i>=grid.length||j<0||j>=grid[0].length||grid[i][j]!=='1') return;\n"
            "        grid[i][j]='0';\n"
            "        dfs(i+1,j);dfs(i-1,j);dfs(i,j+1);dfs(i,j-1);\n"
            "    };\n"
            "    let cnt=0;\n"
            "    for(let i=0;i<grid.length;i++)\n"
            "        for(let j=0;j<grid[0].length;j++)\n"
            "            if(grid[i][j]==='1'){dfs(i,j);cnt++;}\n"
            "    return cnt;\n"
            "};\n"
        ),
        "C++": (
            "void dfs(vector<vector<char>>& g,int i,int j){\n"
            "    if(i<0||i>=(int)g.size()||j<0||j>=(int)g[0].size()||g[i][j]!='1') return;\n"
            "    g[i][j]='0';\n"
            "    dfs(g,i+1,j);dfs(g,i-1,j);dfs(g,i,j+1);dfs(g,i,j-1);\n"
            "}\n"
            "int numIslands(vector<vector<char>>& grid){\n"
            "    int cnt=0;\n"
            "    for(int i=0;i<(int)grid.size();i++)\n"
            "        for(int j=0;j<(int)grid[0].size();j++)\n"
            "            if(grid[i][j]=='1'){dfs(grid,i,j);cnt++;}\n"
            "    return cnt;\n"
            "}\n"
        ),
    },
    "Coin Change": {
        "Python": (
            "def coinChange(coins, amount):\n"
            "    dp=[float('inf')]*(amount+1); dp[0]=0\n"
            "    for i in range(1,amount+1):\n"
            "        for c in coins:\n"
            "            if c<=i: dp[i]=min(dp[i],dp[i-c]+1)\n"
            "    return dp[amount] if dp[amount]!=float('inf') else -1\n"
        ),
        "Java": (
            "public int coinChange(int[] coins, int amount) {\n"
            "    int[] dp=new int[amount+1];\n"
            "    Arrays.fill(dp,amount+1); dp[0]=0;\n"
            "    for(int i=1;i<=amount;i++)\n"
            "        for(int c:coins) if(c<=i) dp[i]=Math.min(dp[i],dp[i-c]+1);\n"
            "    return dp[amount]>amount?-1:dp[amount];\n"
            "}\n"
        ),
        "JavaScript": (
            "var coinChange = function(coins, amount) {\n"
            "    const dp=new Array(amount+1).fill(Infinity); dp[0]=0;\n"
            "    for(let i=1;i<=amount;i++)\n"
            "        for(const c of coins) if(c<=i) dp[i]=Math.min(dp[i],dp[i-c]+1);\n"
            "    return dp[amount]===Infinity?-1:dp[amount];\n"
            "};\n"
        ),
        "C++": (
            "int coinChange(vector<int>& coins, int amount) {\n"
            "    vector<int> dp(amount+1,amount+1); dp[0]=0;\n"
            "    for(int i=1;i<=amount;i++)\n"
            "        for(int c:coins) if(c<=i) dp[i]=min(dp[i],dp[i-c]+1);\n"
            "    return dp[amount]>amount?-1:dp[amount];\n"
            "}\n"
        ),
    },
    "Rotate Image": {
        "Python": (
            "def rotate(matrix):\n"
            "    n = len(matrix)\n"
            "    for i in range(n):\n"
            "        for j in range(i+1, n):\n"
            "            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n"
            "    for row in matrix:\n"
            "        row.reverse()\n"
        ),
        "Java": (
            "public class Solution {\n"
            "    public void rotate(int[][] matrix) {\n"
            "        int n = matrix.length;\n"
            "        for(int i=0;i<n;i++)\n"
            "            for(int j=i+1;j<n;j++) {\n"
            "                int t = matrix[i][j];\n"
            "                matrix[i][j] = matrix[j][i];\n"
            "                matrix[j][i] = t;\n"
            "            }\n"
            "        for(int[] row : matrix) {\n"
            "            int l=0, r=n-1;\n"
            "            while(l<r) { int t=row[l]; row[l++]=row[r]; row[r--]=t; }\n"
            "        }\n"
            "    }\n"
            "}"
        ),
        "JavaScript": (
            "function rotate(matrix) {\n"
            "    const n = matrix.length;\n"
            "    for(let i=0;i<n;i++)\n"
            "        for(let j=i+1;j<n;j++)\n"
            "            [matrix[i][j], matrix[j][i]] = [matrix[j][i], matrix[i][j]];\n"
            "    for(const row of matrix) row.reverse();\n"
            "}"
        ),
        "C++": (
            "void rotate(vector<vector<int>>& m) {\n"
            "    int n = m.size();\n"
            "    for(int i=0;i<n;i++)\n"
            "        for(int j=i+1;j<n;j++) swap(m[i][j], m[j][i]);\n"
            "    for(auto& r : m) reverse(r.begin(), r.end());\n"
            "}"
        ),
    },
}


def get_solution_for_lang(title, lang, python_fallback, db_solutions_json="{}"):
    """Return (code, language_string) for st.code().
    Priority: 1) DB solutions_json  2) PROBLEM_SOLUTIONS dict  3) python_fallback
    """
    import json as _j
    lang_map = {"Python": "python", "JavaScript": "javascript", "Java": "java", "C++": "cpp"}

    # 1. Try DB stored multi-lang solutions first
    try:
        db_sols = _j.loads(db_solutions_json) if db_solutions_json else {}
        if lang in db_sols:
            return db_sols[lang], lang_map[lang]
    except Exception:
        db_sols = {}

    # 2. Try in-memory PROBLEM_SOLUTIONS dict
    mem_sols = PROBLEM_SOLUTIONS.get(title, {})
    if lang in mem_sols:
        return mem_sols[lang], lang_map[lang]

    # 3. Try Python from either source
    py_code = db_sols.get("Python") or mem_sols.get("Python") or python_fallback
    return py_code, "python"

def get_db():
    return sqlite3.connect(DB_PATH)


def get_all_questions(difficulty=None, company=None, topic=None):
    init_interview_tables()
    conn = get_db()
    c = conn.cursor()
    query = "SELECT id, title, description, difficulty, company, topic, examples, hints, solution, COALESCE(solutions_json,'{}') FROM coding_questions WHERE 1=1"
    params = []
    if difficulty and difficulty != "All":
        query += " AND difficulty = ?"
        params.append(difficulty)
    if company and company != "All":
        query += " AND company LIKE ?"
        params.append(f"%{company}%")
    if topic and topic != "All":
        query += " AND topic LIKE ?"
        params.append(f"%{topic}%")
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows


def save_coding_result(user_id, question_id, code, is_correct, time_taken):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO coding_results (user_id, question_id, user_code, is_correct, time_taken) VALUES (?,?,?,?,?)",
        (user_id, question_id, code, int(is_correct), time_taken)
    )
    conn.commit()
    conn.close()


def get_user_coding_stats(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT cq.difficulty, cr.is_correct, cq.topic
        FROM coding_results cr
        JOIN coding_questions cq ON cr.question_id = cq.id
        WHERE cr.user_id = ?
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def _card(html):
    st.markdown(
        f"<div style='background:#1e1e1e;border-radius:12px;padding:1rem 1.2rem;"
        f"margin:0.5rem 0;border:1px solid rgba(76,175,80,0.2);'>{html}</div>",
        unsafe_allow_html=True,
    )


def _difficulty_badge(diff):
    colors = {"Easy": "#4CAF50", "Medium": "#FFA500", "Hard": "#FF4444"}
    c = colors.get(diff, "#888")
    return f"<span style='background:{c};color:white;border-radius:5px;padding:2px 8px;font-size:0.8rem;font-weight:bold;'>{diff}</span>"


def render_coding_practice():
    """Main entry for Coding Practice page."""
    init_interview_tables()

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a237e,#283593);padding:1.5rem 2rem;
    border-radius:14px;margin-bottom:1.5rem;'>
    <h1 style='color:white;margin:0;'>💻 Coding Interview Practice</h1>
    <p style='color:#c5cae9;margin:0.4rem 0 0;'>Practice coding problems by difficulty, company, and topic</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🗂️ Problem Browser", "✏️ Practice Problem", "📊 My Progress"])

    # Determine which tab to show based on session state
    active_tab = st.session_state.get("coding_tab", "browser")
    
    with tabs[0]:
        if active_tab == "browser":
            _render_problem_browser()
        else:
            _render_problem_browser()
    with tabs[1]:
        _render_practice_editor()
    with tabs[2]:
        _render_coding_analytics()
    
    # Auto-scroll to practice tab if set
    if active_tab == "practice":
        st.session_state.coding_tab = "browser"  # reset for next time
        st.markdown("""
        <script>
        setTimeout(function(){
            var tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
            if(tabs && tabs[1]) { tabs[1].click(); }
        }, 200);
        </script>
        """, unsafe_allow_html=True)


# ── Problem Browser ────────────────────────────────────────────────────────────

def _render_problem_browser():
    st.subheader("Browse Problems")

    col1, col2, col3 = st.columns(3)
    with col1:
        diff_filter = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="pb_diff")
    with col2:
        company_filter = st.selectbox("Company", ["All", "Google", "Amazon", "Microsoft", "Meta", "TCS", "Infosys"], key="pb_company")
    with col3:
        topic_filter = st.selectbox("Topic", ["All", "Arrays", "Strings", "Stack", "Binary Search",
                                               "Sliding Window", "Dynamic Programming", "Graph/DFS", "Design", "Two Pointers"], key="pb_topic")

    questions = get_all_questions(diff_filter, company_filter, topic_filter)

    if not questions:
        st.info("No questions match your filters.")
        return

    st.success(f"Found **{len(questions)}** problems")

    for q in questions:
        qid, title, desc, diff, company, topic, examples, hints, solution, solutions_json = q
        diff_emoji = {"Easy": "🟢", "Medium": "🟠", "Hard": "🔴"}.get(diff, "⚪")
        with st.expander(f"{diff_emoji} {diff} · {title} — {topic}", expanded=False):
            st.markdown(f"{_difficulty_badge(diff)} **{title}** &nbsp; `{topic}`", unsafe_allow_html=True)
            st.markdown(desc)

            # Examples
            try:
                examples_list = json.loads(examples) if examples else []
            except Exception:
                examples_list = []
            if examples_list:
                st.markdown("**Examples:**")
                for ex in examples_list:
                    st.code(f"Input:  {ex.get('input', '')}\nOutput: {ex.get('output', '')}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Practice This →", key=f"practice_{qid}"):
                    st.session_state.practice_qid = qid
                    st.session_state.practice_q = q
                    st.session_state.coding_tab = "practice"
                    st.rerun()
            with col2:
                company_list = company.split(",") if company else []
                if company_list:
                    badges = " ".join(
                        f"<span style='background:#263238;color:#80deea;border-radius:4px;padding:1px 6px;font-size:0.75rem;margin:1px;'>{c.strip()}</span>"
                        for c in company_list
                    )
                    st.markdown(f"Companies: {badges}", unsafe_allow_html=True)


# ── Practice Editor ────────────────────────────────────────────────────────────

def _render_practice_editor():
    if "practice_q" not in st.session_state:
        st.info("👈 Select a problem from the Problem Browser tab to practice it here.")
        # Show quick select
        questions = get_all_questions()
        if questions:
            titles = {f"{q[1]} ({q[3]})": q for q in questions}
            selected_title = st.selectbox("Or pick a problem directly:", list(titles.keys()), key="quick_pick")
            if st.button("Load Problem", type="primary", key="load_quick"):
                q = titles[selected_title]
                st.session_state.practice_q = q
                st.session_state.practice_qid = q[0]
                st.rerun()
        return

    q = st.session_state.practice_q
    qid, title, desc, diff, company, topic, examples, hints, solution, solutions_json = q

    # Problem header
    st.markdown(
        f"<div style='background:#1e1e1e;border-radius:12px;padding:1.2rem;margin-bottom:1rem;'>"
        f"<h2 style='color:white;margin:0;'>{title} {_difficulty_badge(diff)}</h2>"
        f"<p style='color:#aaa;margin:0.3rem 0 0;'>Topic: {topic}</p></div>",
        unsafe_allow_html=True,
    )

    # Description and examples in a left panel
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("**Problem:**")
        _card(f"<p style='color:#e0e0e0;line-height:1.7;margin:0;'>{desc}</p>")

        try:
            examples_list = json.loads(examples) if examples else []
        except Exception:
            examples_list = []
        if examples_list:
            st.markdown("**Examples:**")
            for ex in examples_list:
                st.code(f"Input:  {ex.get('input', '')}\nOutput: {ex.get('output', '')}", language="text")

        # Hints
        if hints:
            with st.expander("💡 Show Hints"):
                try:
                    hints_list = json.loads(hints)
                    for i, h in enumerate(hints_list, 1):
                        st.markdown(f"**Hint {i}:** {h}")
                except Exception:
                    st.markdown(hints)

    with col_right:
        st.markdown("**Your Solution:**")

        # Language selector - track previous language to detect changes
        prev_lang = st.session_state.get(f"prev_lang_{qid}", "Python")
        lang = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++"], key="code_lang")
        lang_map = {"Python": "python", "JavaScript": "javascript", "Java": "java", "C++": "cpp"}

        # Starter code templates
        starters = {
            "Python": f"# Solve: {title}\ndef solution():\n    # Your code here\n    pass\n",
            "JavaScript": f"// Solve: {title}\nfunction solution() {{\n    // Your code here\n}}\n",
            "Java": f"// Solve: {title}\npublic class Solution {{\n    public void solve() {{\n        // Your code here\n    }}\n}}\n",
            "C++": f"// Solve: {title}\n#include <bits/stdc++.h>\nusing namespace std;\nvoid solution() {{\n    // Your code here\n}}\n",
        }

        # Use per-language key so switching language resets to that language's starter
        code_key = f"code_{qid}_{lang}"
        if lang != prev_lang:
            # Language changed - clear old code key so starter code loads
            st.session_state.pop(code_key, None)
            st.session_state[f"prev_lang_{qid}"] = lang

        default_code = st.session_state.get(code_key, starters[lang])
        user_code = st.text_area(
            "Code Editor",
            value=default_code,
            height=300,
            key=f"editor_{qid}_{lang}",
        )
        st.session_state[code_key] = user_code

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Submit Solution", type="primary", key=f"submit_code_{qid}"):
                is_attempt = len(user_code.strip()) > 50 and "pass" not in user_code and "Your code here" not in user_code
                user_id = st.session_state.get("user_id", 0)
                save_coding_result(user_id, qid, user_code, is_attempt, 0)
                if is_attempt:
                    st.success("✅ Solution submitted! Great effort!")
                else:
                    st.warning("⚠️ Please write a more complete solution before submitting.")

        with col2:
            # Use a distinct state key (prefixed) to avoid widget key conflict
            if st.button("🔍 Show Solution", key=f"btn_sol_{qid}"):
                st.session_state[f"reveal_sol_{qid}"] = True

        with col3:
            if st.button("🔄 Reset Code", key=f"reset_{qid}"):
                st.session_state.pop(f"code_{qid}_{lang}", None)
                st.session_state.pop(f"reveal_sol_{qid}", None)
                st.rerun()

        if st.session_state.get(f"reveal_sol_{qid}"):
            st.markdown("**Reference Solution:**")
            # Pass solutions_json from DB so all stored languages are available
            sol_code, sol_lang = get_solution_for_lang(title, lang, solution, solutions_json)
            if sol_lang == "python" and lang != "Python":
                st.caption(f"ℹ️ No {lang} solution stored yet — showing Python")
            st.code(sol_code, language=sol_lang)

    # Next / Previous problem
    all_qs = get_all_questions()
    ids = [q[0] for q in all_qs]
    if qid in ids:
        curr_idx = ids.index(qid)
        c1, c2 = st.columns(2)
        with c1:
            if curr_idx > 0 and st.button("← Previous Problem", key="prev_prob"):
                st.session_state.practice_q = all_qs[curr_idx - 1]
                st.session_state.practice_qid = all_qs[curr_idx - 1][0]
                st.rerun()
        with c2:
            if curr_idx < len(all_qs) - 1 and st.button("Next Problem →", key="next_prob"):
                st.session_state.practice_q = all_qs[curr_idx + 1]
                st.session_state.practice_qid = all_qs[curr_idx + 1][0]
                st.rerun()


# ── Coding Analytics ────────────────────────────────────────────────────────────

def _render_coding_analytics():
    st.subheader("My Coding Progress")

    user_id = st.session_state.get("user_id", 0)
    stats = get_user_coding_stats(user_id)
    all_q = get_all_questions()
    total_problems = len(all_q)

    if stats:
        solved = sum(1 for s in stats if s[1] == 1)
        attempted = len(stats)
        accuracy = (solved / attempted * 100) if attempted else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Problems Attempted", attempted)
        col2.metric("Solved", solved)
        col3.metric("Accuracy", f"{accuracy:.1f}%")
        col4.metric("Total Available", total_problems)

        # Difficulty breakdown
        diff_data = {}
        for s in stats:
            diff = s[0]
            diff_data.setdefault(diff, {"attempted": 0, "solved": 0})
            diff_data[diff]["attempted"] += 1
            if s[1]:
                diff_data[diff]["solved"] += 1

        if diff_data:
            df = pd.DataFrame([
                {"Difficulty": k, "Attempted": v["attempted"], "Solved": v["solved"]}
                for k, v in diff_data.items()
            ])
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Attempted", x=df["Difficulty"], y=df["Attempted"],
                                 marker_color="#FFA500"))
            fig.add_trace(go.Bar(name="Solved", x=df["Difficulty"], y=df["Solved"],
                                 marker_color="#4CAF50"))
            fig.update_layout(barmode="group", title="Problems by Difficulty",
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="white")
            st.plotly_chart(fig, width='stretch')

        # Skill progress radar
        topics = list({s[2] for s in stats if s[2]})[:6]
        if topics:
            topic_scores = []
            for t in topics:
                t_stats = [s for s in stats if s[2] == t]
                score = (sum(1 for s in t_stats if s[1]) / len(t_stats) * 100) if t_stats else 0
                topic_scores.append(score)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatterpolar(
                r=topic_scores + [topic_scores[0]], theta=topics + [topics[0]],
                fill="toself", line_color="#7C4DFF", name="Skill Level"
            ))
            fig2.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])),
                showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=350, title="Skill Proficiency by Topic"
            )
            st.plotly_chart(fig2, width='stretch')

    else:
        _card("""
        <div style='text-align:center;padding:2rem;'>
        <p style='font-size:3rem;'>💻</p>
        <p style='color:#aaa;font-size:1.1rem;'>No coding attempts yet.</p>
        <p style='color:#888;'>Solve problems in the Practice tab to see your progress here.</p>
        </div>
        """)

    # Study plan suggestion
    st.markdown("### 📅 Suggested Study Plan")
    plan = [
        ("Week 1", "Easy", "Arrays, Strings — Focus on Two Sum, Reverse String, Valid Parentheses"),
        ("Week 2", "Easy-Medium", "Sliding Window, Binary Search — LongestSubstring, Search algorithms"),
        ("Week 3", "Medium", "Dynamic Programming, Graph DFS — Maximum Subarray, Number of Islands"),
        ("Week 4", "Hard", "System Design, Complex DS — LRU Cache, Trapping Rain Water"),
    ]
    for week, level, focus in plan:
        _card(
            f"<b style='color:#4CAF50;'>{week}</b> &nbsp;"
            f"<span style='background:#263238;color:#80cbc4;border-radius:4px;padding:1px 6px;font-size:0.8rem;'>{level}</span>"
            f"<p style='color:#ddd;margin:0.3rem 0 0;'>{focus}</p>"
        )