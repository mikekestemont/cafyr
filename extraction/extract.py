import argparse
from lxml import etree
namespaces = {'tei':'http://www.tei-c.org/ns/1.0'}

def main():
    argparser = argparse.ArgumentParser(description='Convert a plain text document to XML')
    argparser.add_argument('--infile', type=str, default='MillionsGA.xml',
                        help='Path to the input file (raw text, UTF8)')
    args = argparser.parse_args()
    print(args)

    book = etree.parse(args.infile)
    
    with open('child.txt', 'w') as f:
        for said in book.iterfind('.//tei:said', namespaces=namespaces):
            if 'direct' in said.attrib and said.attrib['direct'] == 'true':
                if 'agecat' in said.attrib and said.attrib['agecat'] not in ('adult', 'oldadult'):
                    t = ' '.join(said.itertext()).strip()
                    f.write(t + '\n')
    
    with open('adult.txt', 'w') as f:
        for said in book.iterfind('.//tei:said', namespaces=namespaces):
            if 'direct' in said.attrib and said.attrib['direct'] == 'true':
                if 'agecat' in said.attrib and said.attrib['agecat'] in ('adult', 'oldadult'):
                    t = ' '.join(said.itertext()).strip()
                    f.write(t + '\n')
    
    with open('mum.txt', 'w') as f:
        for seg in book.iterfind('.//tei:seg', namespaces=namespaces):
            if 'about' in seg.attrib and seg.attrib['about'].lower() == 'mum':
                t = ' '.join(seg.itertext()).strip()
                f.write(t + '\n')
    
    with open('dad.txt', 'w') as f:
        for seg in book.iterfind('.//tei:seg', namespaces=namespaces):
            if 'about' in seg.attrib and seg.attrib['about'].lower() == 'dad':
                t = ' '.join(seg.itertext()).strip()
                f.write(t + '\n')
    
    with open('dad_said.txt', 'w') as f:
        for said in book.iterfind('.//tei:said', namespaces=namespaces):
            if 'direct' in said.attrib and said.attrib['direct'] == 'true':
                if 'who' in said.attrib and said.attrib['who'].lower() == 'dad':
                    t = ' '.join(said.itertext()).strip()
                    f.write(t + '\n')


if __name__ == '__main__':
    main()


