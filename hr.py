def areAlmostEquivalent(s,t):
    res=['NO']*len(s)
    for i in range(len(s)):
        if len(s[i])==len(t[i]):
            cnt=0
            for j in range(len(s[i])):
                if s[i][j]!=t[i][j]:
                    cnt+=1
                    if cnt>3:
                        break
            if cnt<=3:
                res[i]='YES'
    return res

print(areAlmostEquivalent(['aaabbb','ccaab'],['aacbbc','aabbc']))