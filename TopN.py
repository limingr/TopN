import sys, re, optparse
import json
import requests

#organization=Twitter and N=10

#https://github.com/twitter
#To get a user's repo:    https://api.github.com/users/limingr/repos
#To get a org's repo      https://api.github.com/orgs/twitter/repos

#
# Top-N repos by number of stars.
# Top-N repos by number of forks.
# Top-N repos by number of Pull Requests (PRs).
# Top-N repos by contribution percentage (PRs/forks).
#

if len(sys.argv) < 5:
   sys.exit("Please provide an org name,  N and a valid github user name and password such as: organization=Twitter N=5 user password")

org_para=sys.argv[1]
top_Npara=sys.argv[2]

if not org_para.startswith("organization="):
    sys.exit("The orgination parameter is not in correct format, the parameters should be similar to:   organization=Twitter N=5 user password ")

org_len=len("organization=");
organization=org_para[org_len:]

if not top_Npara.startswith("N="):
    sys.exit("The N parameter is not in correct format, the parameters should be similar to:   organization=Twitter N=5 user password")

try:
    top_NLen=len("N=")
    top_N=(int)(top_Npara[top_NLen:])
except ValueError:
    sys.exit("Please provide an org name and N such as:   organization=Twitter N=5 user password")


#print("organization="+organization)
#print("N="+str(top_N))

if  top_N<=0:
    sys.exit("The value of N={N} is invalid".format(N=top_N))

if len(organization) == 0:
   sys.exit("The value of organization={organization} is invalid".format(organization=organization))

username =  sys.argv[3]
password =  sys.argv[4]

if len(password)==0 or len(password)==0:
   sys.exit("Please provide a valid github user name and password, thanks.")

url="https://api.github.com/orgs/"+organization+"/repos"
#print("Requesting "+url)
contents = requests.get("https://api.github.com/orgs/"+organization+"/repos", auth=(username, password))
#print(contents)

if contents.status_code != 200: ## OK
   print("Http returns {sc}.".format(sc=contents.status_code));
   sys.exit("Please provide a github valid user name and password, thanks.")


repos = contents.json()
print("There are "+str(len(repos))+" repos");
repos=sorted(repos, key=lambda x:x["stargazers_count"], reverse=True)

#stars
print("Top-{N} repos by number of stars:".format(N=top_N))
for i in range(min(len(repos), top_N)):
    #print(str(i)+ "  "+ repos[i]["name"] +"  "+ str(repos[i]["stargazers_count"]))
    print("{index:5d}  {name:40s}  {stargazers_count:10d}".format(index=i, name=repos[i]["name"], stargazers_count=repos[i]["stargazers_count"]))


print("Top-{N} repos by number of forks:".format(N=top_N))
repos=sorted(repos, key=lambda x:x["forks_count"], reverse=True)
for i in range(min(len(repos), top_N)):
    #print(str(i)+ "  "+ repos[i]["name"] +"  "+ str(repos[i]["forks_count"]))
    print("{index:5d}  {name:40s}  {stargazers_count:10d}".format(index=i, name=repos[i]["name"], stargazers_count=repos[i]["forks_count"]))


#https://api.github.com/repos/twitter/twurl/pulls?state=all

#Pull Requests dictionary
pullrequests_dict={}  # name:pr_count
print("Retrieving pull request counts (may take a min.) ....");
for i in range(len(repos)):
    request_url="https://api.github.com/repos/{org}/{repo}/pulls?state=all".format(org=organization, repo=repos[i]["name"])
    pullrequests= requests.get(request_url)
    pullrequests=pullrequests.json();
    pullrequests_dict[repos[i]["name"]]=len(pullrequests)

#top PR
print("Top-{N} repos by number of pull requests:".format(N=top_N))
i=0
for k, v in sorted(pullrequests_dict.items(), key=lambda items: items[1],  reverse=True):
    print("{index:5d}  {name:40s}  {pullrequest_count:10d}".format(index=i, name=k, pullrequest_count=v))
    i=i+1
    if i>=top_N :
        break

#contribution percentage
contribution_dict={}
for x in range(len(repos)):
    name=repos[x]["name"]
    pullrequests_count=pullrequests_dict[name] if name in  pullrequests_dict  else 0
    forks_count=repos[x]["forks_count"]
    contribution_dict[name]=0.0 if forks_count==0 else (pullrequests_count/forks_count)

print("Top-{N} repos by number of contribution percentage (PRs/forks):".format(N=top_N))
i=0
for k, v in sorted(contribution_dict.items(), key=lambda items: items[1],  reverse=True):
    print("{index:5d}  {name:40s}  {contribution_count:10.4f}".format(index=i, name=k, contribution_count=v))
    i=i+1
    if i>=top_N :
        break