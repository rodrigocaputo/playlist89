import urllib, json, time, threading

def crawler89():
	with open('playlist89.txt', 'r') as f:
		lines = f.read().splitlines()
		ultimas = lines[-4:]

	agora = int(time.time())
	print time.ctime(agora)
	#url = 'https://players.gc2.com.br/pulsar/rockpulsar.xml'
	url = 'https://players.gc2.com.br/cron/89fm/results2.json?_=' + str(agora)
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	print data
	for item in reversed(data['musicas']['jatocou']):
		musica = item['song'] + ' - ' + item['singer']
		if musica not in ultimas:
			with open('playlist89.txt', 'a') as f:
				f.write('\n' + musica)

	threading.Timer(15.0, crawler89).start()

threading.Timer(15.0, crawler89).start()