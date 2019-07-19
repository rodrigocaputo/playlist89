import urllib, xmltodict, json, time, threading, os, csv
from datetime import date, datetime

def crawler89Json():
	agora = int(time.time())
	url = 'https://players.gc2.com.br/cron/89fm/results2.json?_=' + str(agora)
	response = urllib.request.urlopen(url)
	data = json.loads(response.read())
	data['musicas']['tocando']['onair'] = True
	if data['musicas']['tocando']['singer'] != '89FM A Rádio Rock':
		agora = datetime.now()
		data['musicas']['tocando']['hour'] = str(agora.hour).zfill(2) + ':' + str(agora.minute).zfill(2) + ':' + str(agora.second).zfill(2)
		data['musicas']['tocando']['ISRC'] = None
		return data

	raise 'Falha no crawler89Json'

def crawler89():

	url = 'https://players.gc2.com.br/pulsar/rockpulsar.xml'
	try:
		response = urllib.request.urlopen(url)
		data = response.read()
		response.close()
		data = xmltodict.parse(data)
	except:
		try:
			data = crawler89Json()
		except:
			threading.Timer(60.0, crawler89).start()
			return

	registros = []
	for itens in data['musicas']:
		itens = data['musicas'][itens]
		registro = {}
		for item in itens:
			if type(item) == str:
				if item == 'ISRC':
					registros.append(registro)
					registro = {}
				else:
					registro[item] = itens[item]
					#print(item, itens[item])
			else:
				for chave, valor in item.items():
					if chave == 'ISRC':
						registros.append(registro)
						registro = {}
					else:
						registro[chave] = valor
						#print(chave, valor)

	#for registro in registros:
		#print(registro['hour'], registro)

	hoje = date.today()

	root = '.'
	ano = os.path.join(root, str(hoje.year))
	if not os.path.exists(ano):
		os.makedirs(ano)

	root = ano
	mes = os.path.join(root, str(hoje.month).zfill(2))
	if not os.path.exists(mes):
		os.makedirs(mes)

	root = mes
	dia = os.path.join(root, str(hoje.day).zfill(2))
	if not os.path.exists(dia):
		os.makedirs(dia)

	root = dia
	nome_csv = '89_' + str(hoje.year) + '-' \
					 + str(hoje.month).zfill(2) + '-' \
					 + str(hoje.day).zfill(2) + '.csv'
	colunas = ['ARTISTA', 'MUSICA', 'REPRODUCAO', 'TEMPO', \
				'ID_ARTISTA', 'ID_MUSICA', 'ID_ALBUM', 'TIPO']
	arquivo = os.path.join(root, nome_csv)
	if not os.path.exists(arquivo):
		with open(arquivo, 'w') as saida:
			writer = csv.DictWriter(saida, fieldnames=colunas, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writeheader()
			print('Arquivo', nome_csv, 'criado')

	musicas = []
	with open(arquivo, 'r+') as saida:
		reader = csv.DictReader(saida, fieldnames=colunas, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		contador = 0
		for linha in reader:
			if contador > 0:
				musicas.append(linha)
			
			contador += 1

	#print(musicas)
	ultimas = musicas[-7:]
	#print(ultimas)

	tags = {'ARTISTA': 'singer', \
			'MUSICA': 'song', \
			'REPRODUCAO': 'hour', \
			'TEMPO': 'length', \
			'ID_ARTISTA': 'singer_id', \
			'ID_MUSICA': 'song_id', \
			'ID_ALBUM': 'album_id', \
			'TIPO': 'media_type'}

	def verificaTag(registro, tag):
		if tag in registro:
			return registro[tag]

		return None

	with open(arquivo, 'a') as saida:
		writer = csv.DictWriter(saida, fieldnames=colunas, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for registro in sorted(registros, key=lambda x: x['hour']):
			inserir = True
			if 'onair' in registro and registro['onair'] == 'False' \
				or tags['TIPO'] in registro and registro[tags['TIPO']] == 'STOPPED':
				inserir = False

			if inserir:
				for item in ultimas:
					if registro[tags['ARTISTA']] == item['ARTISTA'] \
						and registro[tags['MUSICA']] == item['MUSICA']:
						inserir = False

			if inserir:
				print(registro[tags['REPRODUCAO']], registro[tags['ARTISTA']], '-', registro[tags['MUSICA']])
				writer.writerow({ \
					'ARTISTA': verificaTag(registro, tags['ARTISTA']), \
					'MUSICA': verificaTag(registro, tags['MUSICA']), \
					'REPRODUCAO': verificaTag(registro, tags['REPRODUCAO']), \
					'TEMPO': verificaTag(registro, tags['TEMPO']), \
					'ID_ARTISTA': verificaTag(registro, tags['ID_ARTISTA']), \
					'ID_MUSICA': verificaTag(registro, tags['ID_MUSICA']), \
					'ID_ALBUM': verificaTag(registro, tags['ID_ALBUM']), \
					'TIPO': verificaTag(registro, tags['TIPO'])})

	threading.Timer(60.0, crawler89).start()

crawler89()
