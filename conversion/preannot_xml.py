import argparse
import os
import re

from lxml import etree
import spacy

parser = etree.XMLParser()
namespaces = {'tei':'http://www.tei-c.org/ns/1.0'}

def main():
    argparser = argparse.ArgumentParser(description='Convert a plain text document to XML')
    argparser.add_argument('--infile', type=str, default='../xml/paradijs.xml',
                        help='Path to the xml input file')
    argparser.add_argument('--outfile', type=str, default='../xml/paradijs_preannot.xml',
                        help='Path to the output file (.xml)')
    argparser.add_argument('--language', type=str, default='nl',
                        help='Language of the files')
    args = argparser.parse_args()
    print(args)

    nlp = spacy.load(args.language)

    tree = etree.parse(args.infile)
    for said_node in tree.iterfind('.//tei:said', namespaces=namespaces):
        t = ' '.join(said_node.itertext()).strip()
        t = ' '.join(t.split()).strip()

        new_el = etree.Element('said')
        new_el.attrib['direct'] = said_node.attrib['direct']
        try:
            new_el.attrib['who'] = said_node.attrib['who']
        except KeyError:
            pass
        
        if args.language == 'en':
            ne = []
            for token in nlp(t):
                print(token, token.ent_type_, token.ent_iob_, token.tag_)
                if token.ent_type_ == 'PERSON':
                    if token.ent_iob_ in ('B', 'I'):
                        ne.append(token)
                else:
                    if ne and token.ent_iob_ == 'O':
                        ne_el = etree.Element('rs')
                        ne_el.attrib['ref'] = '#xxx'
                        ne_el.text = ''.join([w.text_with_ws for w in ne]).rstrip()
                        if ne[-1].whitespace_:
                            ne_el.tail = ne[-1].whitespace_
                        new_el.append(ne_el)
                        ne = []
                    if token.tag_.startswith('PRP'):
                        pos_el = etree.Element('rs')
                        pos_el.text = token.text
                        pos_el.attrib['ref'] = '#xxx'
                        if token.whitespace_:
                            pos_el.tail = token.whitespace_
                        new_el.append(pos_el)
                    else:
                        if not len(new_el):
                            if new_el.text:
                                new_el.text += token.text_with_ws
                            else:
                                new_el.text = token.text_with_ws
                        else:
                            if new_el[-1].tail:
                                new_el[-1].tail += token.text_with_ws
                            else:
                                new_el[-1].tail = token.text_with_ws
        elif args.language == 'nl':
            ne = []
            for token in nlp(t):
                print(token, token.ent_type_, token.ent_iob_, token.tag_)
                if token.ent_type_ == 'PER':
                    if token.ent_iob_ in ('B', 'I'):
                        ne.append(token)
                else:
                    if ne and token.ent_iob_ == 'O':
                        ne_el = etree.Element('rs')
                        ne_el.attrib['ref'] = '#xxx'
                        ne_el.text = ''.join([w.text_with_ws for w in ne]).rstrip()
                        if ne[-1].whitespace_:
                            ne_el.tail = ne[-1].whitespace_
                        new_el.append(ne_el)
                        ne = []
                    if token.tag_.startswith(('Pron|per|', 'Pron|bez|')):
                        pos_el = etree.Element('rs')
                        pos_el.text = token.text
                        pos_el.attrib['ref'] = '#xxx'
                        if token.whitespace_:
                            pos_el.tail = token.whitespace_
                        new_el.append(pos_el)
                    else:
                        if not len(new_el):
                            if new_el.text:
                                new_el.text += token.text_with_ws
                            else:
                                new_el.text = token.text_with_ws
                        else:
                            if new_el[-1].tail:
                                new_el[-1].tail += token.text_with_ws
                            else:
                                new_el[-1].tail = token.text_with_ws
        
        said_node.getparent().replace(said_node, new_el)   
        

    with open(args.outfile, 'w') as f:
        f.write(etree.tostring(tree, xml_declaration=True,
                                pretty_print=True, encoding='utf-8').decode())

if __name__ == '__main__':
    main()