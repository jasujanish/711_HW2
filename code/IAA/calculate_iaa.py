from sklearn.metrics import cohen_kappa_score

with open('IAA/IAA_Nishchay.txt', "r") as f:
    a1 = [l.strip().lower() for l in f]
with open('IAA/IAA_Natan.txt', "r") as f:
    a2 = [l.strip().lower() for l in f]

kappa = cohen_kappa_score(a1, a2)
print(kappa)
