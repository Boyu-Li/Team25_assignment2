
word_index_path = './dataset/word_index.csv'
model_file_path = './keras_model/model.h5'

# consumer_key, consumer_secret, access_token, access_secret
twitter_credential = [
	[
		'IOIOw6xvqofsRv0IPfVXenjdx',
		'SB7hctfAE5ahJODVmDfu5L7DlLjBwRCpbYvpGtaB0tdm770UTO',
		'2827916142-AnmNWbyNOoHpKyIDf81tbsbU0MpHzwGWmIkq1nD',
		'sF0xiUjhzqkSCznntgGcFWhDBXug24516vArdiIX5yCZS'
	],
	[
		'pEyWDAkywaps25FwcevKsHfVP',
		'Pcjpt01eq0CJurEvkOfKdiRfjzmUy3mTccEBqRImdLcs0cKIGW',
		'1073317984834383874-vXefDmuS7qv1P1gzMVEXwlOc0ReC3h',
		'er6TuvBoyY9nIbRdF86HDHRw3WcabdWUTzMGro98PRb1N'

	],
	[
		'bBAyCzuDVTwZ4a5cEdXZsCBtD',
		'ULRqMIeXV4g5UZRsUYAutQLoA9KGc2LBgtzUm11J4DApoxIi1v',
		'988328066442117121-ttz85CDp8aGRzs2AzmoeWAFJ1HQrFmq',
		'ApDqhTbpsAOGoYnhQQqbLjlosHPUBzVKlxm1wS2PBG8Q7'
	],
	[
		'd62pUkVPmCn3Z7xqNMQMxWXMZ',
		'XaxYpFE8Tg996xObHCEuinJSMzsOlgw6aURg0Q2pVPmVTCxJny',
		'929822293026410496-IEgodiHH2bp8811JQgVrYLf0YfIJD7j',
		'LaExHPHyKbeOQ2uKECjryNOL1oi0IwiN0YS66BLGFRpwO'
	],
	[
		'Kpyssg6TFroQBUFnOXypEfe42',
		'Tc4yDwFuLsgmbLzpZLwlMEIUiUDG5N1onXOJAEQiTxXbG670iL',
		'1404414595-tAxzSebx6HLTGj59RBlJISAh5VqOx6BZWv7pCk0',
		'z0VO09ArtRqRi1G0eEwOJWKPwHdThbJ6Py60x033cNpQr'
	],
	[
		'KgOsEeVIl3tYoumlldYJMCB4w',
		'jJTt7k6SMX8I9lEp4o3pxXtk7FV5oi3vuTbXVjqKDMt2iaagQZ',
		'1126354979969613825-VFJQGZuuv8gYI3JIo1dMSNMbOxTheo'
		'JrGwQkoEEr7AGh4Pst29CsTRiMRExFIi0KUGz0N3EUjoW'
	],
	[
		'jOLT42joLaYvCiKwj80THjZKv',
		'rpfm0BVZpQsE72ydp59mlE9miA5w52wUgt0NDoh2E9TjJB6Pkm',
		'1126292737530011648-WxoyvAvIw6Vj6cdSNPFIZEpYmbj2Sh',
		'pW3p4JZbzldZijGnCLeCsGolxYQaoEVPr2g7YEgDaZBlN'

	],
	[
		'qYf1RiCNwdnNt2DVkptvMuQIa',
		'SXCG0Yd3aI1xr3srBhwfI7rKvFCAJYkwQZKnxKF8c25BYIvaip',
		'3317109732-9itC8SnbbGAJYbNhM7OQGczUGbcNMK1U2t6piSy',
		'0lXPWtpgGei2PBBqBlODlKZpbkmIn8VvBR0UcY70NwRrM'

	]
]

city_list = [
	'Sydney',
	'Melbourne',
	'Brisbane',
	'Canberra',
	'Perth',
	'Adelaide',
	'Hobart',
	'Darwin'
]

twitter_count = [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000]


# def get_locaton_geo(city_index):
#
# 	if city_index == 0:
# 		return 'Sydney', [150.92, -34.19, 151.49, -33.53]
# 	elif city_index == 1:
# 		return 'Melbourne', [144.67, -38.16, 145.39, -37.58]
# 	elif city_index == 2:
# 		return ('Brisbane', [152.65, -27.75, 153.44, -27.05])
# 	elif city_index == 3:
# 		return ('Canberra', [149.10, -35.30, 149.16, -35.25])
# 	elif city_index == 4:
# 		return ('Perth', [115.80, -31.94, 115.86, -31.90])
# 	elif city_index == 5:
# 		return ('Adelaide', [138.58, -34.94, 138.62, -34.90])
# 	elif city_index == 6:
# 		return ('Hobart', [147.30, -42.90, 147.32, -42.86])
# 	elif city_index == 7:
# 		return ('Darwin', [130.82, -12.48, 130.86, -12.44])
# 	elif city_index == 8:
# 		return ('AU', [115.86, -34.74, 152.51, -14.35])
# 	else:
# 		return None
