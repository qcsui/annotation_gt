# gt_extract.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pdfextract  # 示例：导入需要的类或函数
import glob

def main():
	file_list = glob.glob("./pdfs/*.pdf")
	print(file_list)
	for filedir in file_list:
		pageno = 2
		figno = 1
		rehtml,rejson= pdfextract.pdf_main(filedir,pageno,figno)
		# return 'File uploaded successfully.' + filedir
		# os.remove(filedir) #delete file after preview
	#jsonify({'html': rehtml, 'json': rejson})
	#print(rehtml)
	# print(rejson)
		print(type(rehtml))
		print(type(rejson))
		filename = os.path.join("./data_extracted",os.path.basename(filedir[:-4]+f"_p{pageno}f{figno}.html"))
		with open(filename, "w") as html_file:
    			html_file.write(rehtml)
		
		filename = os.path.join("./data_extracted",os.path.basename(filedir[:-4]+f"_p{pageno}f{figno}.json"))
		with open(filename, "w") as json_file:
    			json_file.write(rejson)
if __name__ == "__main__":
	main()
