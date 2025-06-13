# from wasabi2d import Scene, run

# scene = Scene()

# # The rest of your code goes here.

# run()

contraintes = {2: 'b', 0: 'b'}
rev_contraintes = {}
for key, value in contraintes.items():
	if value in rev_contraintes :
		rev_contraintes[value].append(key)
	else :
		rev_contraintes[value] = [key]

print(rev_contraintes)
