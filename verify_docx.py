import re
import sys
import zipfile

path = sys.argv[1] if len(sys.argv) > 1 else '_tmp-doc.docx'
z = zipfile.ZipFile(path)
doc = z.read('word/document.xml').decode('utf-8')
sty = z.read('word/styles.xml').decode('utf-8')
foot = z.read('word/footer1.xml').decode('utf-8')

print('file:', path)
print('runs            :', doc.count('<w:r>') + doc.count('<w:r '))
print('noProof (body)  :', doc.count('<w:noProof/>'))
print('proofErr (body) :', doc.count('proofErr'))
print('lang zh-CN runs :', len(re.findall(r'<w:lang w:val="zh-CN"', doc)))
print('docDefaults lang zh-CN:', 'zh-CN' in sty)
print('footer noProof  :', foot.count('<w:noProof/>'), '/ runs', foot.count('<w:r>'))

m = re.search(r'<w:r>(?:(?!</w:r>).)*?DeepSeek Harness(?:(?!</w:r>).)*?</w:r>', doc, re.S)
if m:
    rpr = re.search(r'<w:rPr>.*?</w:rPr>', m.group(0), re.S)
    print('sample rPr      :', rpr.group(0) if rpr else 'none')
