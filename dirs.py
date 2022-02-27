import os
from os.path import join, getsize

with open("icons_rcc.qrc", "w") as f:
	f.write("""<!DOCTYPE RCC><RCC version="1.0">\n""")
	f.write("<qresource>\n")

	for root, dirs, files in os.walk('icons'):
		print(root, "consumes", end=" ")
		print(round(sum([getsize(join(root, name)) for name in files])/1024/1024, 1), end=" ")
		print("megabytes in", len(files), "non-directory files")

		for file in files:
			ficheiro = root + "/" + file
			print(ficheiro)
			f.write("""\t<file alias="{}">{}</file>\n""".format(file, ficheiro))

	for root, dirs, files in os.walk('images'):
		print(root, "consumes", end=" ")
		print(round(sum([getsize(join(root, name)) for name in files])/1024/1024, 1), end=" ")
		print("megabytes in", len(files), "non-directory files")

		for file in files:
			ficheiro = root + "/" + file
			print(ficheiro)
			f.write("""\t<file alias="{}">{}</file>\n""".format(file, ficheiro))

	f.write("</qresource>\n")
	f.write("</RCC>\n")
	f.flush()
	f.close()