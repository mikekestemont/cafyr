"""
python text2xml.py --infile=crummy.txt --outfile=crummy.xml --quote=uk
"""

import argparse
import os
import re

from lxml import etree
import spacy

parser = etree.XMLParser()

def make_header(title='unknown', author='unknown', publisher='unknown'):
    header = etree.XML(f"""<teiHeader>
     <fileDesc>
      <titleStmt>
       <title>{title}</title>
       <respStmt>
        <resp>authored by</resp>
        <name>{author}</name>
       </respStmt>
      </titleStmt>
      <publicationStmt>
       <distributor>{publisher}</distributor>
      </publicationStmt>
      <sourceDesc>
       <bibl>{title}</bibl>
      </sourceDesc>
     </fileDesc>
    </teiHeader>""", parser)
    return header

def make_text():
    text = etree.XML("""<text>
      <front>
    <!-- front matter of copy text, if any, goes here -->
      </front>
      <body>
    <!-- body of copy text goes here -->
      </body>
      <back>
    <!-- back matter of copy text, if any, goes here -->
      </back>
     </text>""", parser)
    return text


def main():
    argparser = argparse.ArgumentParser(description='Convert a plain text document to XML')
    argparser.add_argument('--infile', type=str, default='../txt/paradijs.txt',
                        help='Path to the input file (raw text, UTF8)')
    argparser.add_argument('--outfile', type=str, default='../xml/paradijs.xml',
                        help='Path to the output file (.xml)')
    argparser.add_argument('--quote', type=str, default='uk',
                        help='Path to the output file (.xml)')
    argparser.add_argument('--language', type=str, default='nl',
                        help='Path to the output file (.xml)')
    args = argparser.parse_args()
    print(args)

    if args.quote not in ('uk', 'us'):
        raise ValueError('--quote option must be uk or us')
    
    root = etree.Element('TEI')
    root.attrib['xmlns'] = 'http://www.tei-c.org/ns/1.0'
    root.append(make_header())
    
    text_node = make_text()

    with open(args.infile, 'r') as f:
        text = f.read()
    text = ' '.join(text.split())
    
    div_node = etree.Element('div')
        
    said_node = etree.Element('said')
    said_node.attrib['direct'] = 'false'
    said_node.text = ''
    just_flushed = False

    text = re.sub(r' +', ' ', text)

    nlp = spacy.load(args.language)
    tokens = nlp(text)

    if args.quote == 'uk':
        for idx, token in enumerate(tokens):
            
            # catch potential plural genitive
            plural_genitive = False
            if token.text[-1] == '’':
                try:
                    plural_genitive = (nlp(token.text[:-1])[0].tag_ == 'NNS')
                    plural_genitive = (plural_genitive and not tokens[idx + 1].is_sent_start)
                except:
                    pass
            
            # catch potential abbreviation
            abbreviation = False
            if token.text.endswith(('an’', 'in’', 'o’')):
                abbreviation = True
                abbreviation = (abbreviation and not tokens[idx + 1].is_sent_start)
            
            # opening quotation mark:
            if token.text == '‘':
                if len(said_node.text):
                    div_node.append(said_node)
                
                said_node = etree.Element('said')
                said_node.attrib['direct'] = 'true'
                said_node.attrib['who'] = 'unknown'
                said_node.text = token.text_with_ws
            
            elif token.text[-1] == '’' and not (plural_genitive or abbreviation):
                said_node.text += token.text_with_ws
                div_node.append(said_node)
                just_flushed = True
            else:
                if just_flushed:
                    said_node = etree.Element('said')
                    said_node.attrib['direct'] = 'false'
                    said_node.text = ''
                    just_flushed = False
                
                said_node.text += token.text_with_ws
        
        # don't forget last bit dangling:
        if said_node.text:
            div_node.append(said_node)

    elif args.quote == 'us':
        for idx, token in enumerate(tokens):
            
            if token.text == '“':
                if len(said_node.text):
                    div_node.append(said_node)
                
                said_node = etree.Element('said')
                said_node.attrib['direct'] = 'true'
                said_node.attrib['who'] = 'unknown'
                said_node.text = token.text_with_ws
            
            elif token.text[-1] == '”':
                said_node.text += token.text_with_ws
                div_node.append(said_node)
                just_flushed = True
            else:
                if just_flushed:
                    said_node = etree.Element('said')
                    said_node.attrib['direct'] = 'false'
                    said_node.text = ''
                    just_flushed = False
                
                said_node.text += token.text_with_ws
        
        # don't forget last bit dangling:
        if said_node.text:
            div_node.append(said_node)

    # append to body element:
    text_node[1].append(div_node)
    root.append(text_node)

    with open(args.outfile, 'w') as f:
        f.write(etree.tostring(root, xml_declaration=True,
                                pretty_print=True, encoding='utf-8').decode())

if __name__ == '__main__':
    main()