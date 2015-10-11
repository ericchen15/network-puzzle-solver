import urllib.request
import urllib.parse
url = "https://www.brainbashers.com/shownetwork.asp"
data = urllib.request.Request(url, urllib.parse.urlencode({
    "date":"1006",
	"size":"6",
    "diff":"WRAP",
    "go.x":"25",
    "go.y":"4"}))
content = urllib.request.urlopen("https://www.brainbashers.com/shownetwork.asp?date=1009&size=6&diff=WRAP").read()
print(content)