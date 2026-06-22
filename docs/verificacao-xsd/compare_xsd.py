# -*- coding: utf-8 -*-
"""
Comparação estrutural (semântica) de dois PREMIS v3 XSDs.

Compara o XSD oficial (../../premis-v3-0.xsd) com a transcrição anterior
(./premis-v3-0.transcrito.xsd). Ignora: xs:annotation/documentação, espaços,
grafia de prefixo (QNames são resolvidos a (namespace, localname)) e DEFAULTS de
cardinalidade/uso. Preserva: ordem do content-model (xs:sequence), choices,
cardinalidades, tipos, atributos e enumerações.

Uso:  python compare_xsd.py
"""
import os
from collections import Counter
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
OFFICIAL = os.path.normpath(os.path.join(HERE, '..', '..', 'premis-v3-0.xsd'))
TRANS = os.path.join(HERE, 'premis-v3-0.transcrito.xsd')

QNAME_ATTRS = {'type', 'base', 'ref', 'substitutionGroup', 'itemType', 'refer'}
IGNORE_ATTRS = {'id'}
DEFAULTS = {'minOccurs': '1', 'maxOccurs': '1', 'use': 'optional',
            'nillable': 'false', 'abstract': 'false', 'mixed': 'false'}


def ln(tag):
    if isinstance(tag, str) and tag.startswith('{'):
        return tag.split('}', 1)[1]
    return tag


def rqname(val, nsmap):
    val = val.strip()
    if ':' in val:
        p, loc = val.split(':', 1)
        return (nsmap.get(p), loc)
    return (nsmap.get(None), val)


def canon_attrs(el):
    out = {}
    for k, v in el.attrib.items():
        k = ln(k)
        if k in IGNORE_ATTRS:
            continue
        if k in QNAME_ATTRS:
            out[k] = ('QN',) + rqname(v, el.nsmap)
        elif k == 'memberTypes':
            out[k] = tuple(rqname(x, el.nsmap) for x in v.split())
        else:
            out[k] = v
    for dk, dv in DEFAULTS.items():
        if out.get(dk) == dv:
            del out[dk]
    return tuple(sorted(out.items(), key=lambda kv: kv[0]))


def canon(el):
    kids = []
    for c in el:
        if not isinstance(c.tag, str):
            continue
        if ln(c.tag) == 'annotation':
            continue
        kids.append(canon(c))
    return (ln(el.tag), canon_attrs(el), tuple(kids))


def components(root):
    comps, imports = {}, []
    for c in root:
        if not isinstance(c.tag, str):
            continue
        name = ln(c.tag)
        if name == 'annotation':
            continue
        if name in ('import', 'include', 'redefine'):
            imports.append((name, dict(canon_attrs(c))))
            continue
        comps[(name, c.get('name'))] = canon(c)
    return comps, imports


def fmt(node, indent=0):
    name, attrs, kids = node
    pad = '  ' * indent
    a = ' '.join('%s=%r' % (k, v) for k, v in attrs)
    res = [pad + name + ((' [' + a + ']') if a else '')]
    for k in kids:
        res.append(fmt(k, indent + 1))
    return '\n'.join(res)


def main():
    ro = etree.parse(OFFICIAL).getroot()
    rt = etree.parse(TRANS).getroot()
    co, io = components(ro)
    ct, it = components(rt)

    print('=' * 78)
    print('SCHEMA ROOT ATTRIBUTES')
    for a in ('targetNamespace', 'elementFormDefault', 'attributeFormDefault', 'version'):
        print('  %-22s official=%r   transcrito=%r' % (a, ro.get(a), rt.get(a)))

    print('\nIMPORT/INCLUDE')
    print('  official  :', io if io else '(nenhum)')
    print('  transcrito:', it if it else '(nenhum)')

    def kinds(d):
        return Counter(k[0] for k in d)
    ko, kt = kinds(co), kinds(ct)
    print('\nCONTAGEM DE COMPONENTES GLOBAIS (por tipo)')
    for k in sorted(set(ko) | set(kt)):
        print('  %-14s official=%3d   transcrito=%3d' % (k, ko.get(k, 0), kt.get(k, 0)))
    print('  %-14s official=%3d   transcrito=%3d' % ('TOTAL', len(co), len(ct)))

    ko_set, kt_set = set(co), set(ct)
    missing = sorted(ko_set - kt_set)
    extra = sorted(kt_set - ko_set)
    differ = [k for k in sorted(ko_set & kt_set) if co[k] != ct[k]]

    print('\nFALTANDO no transcrito: %d' % len(missing))
    for k in missing:
        print('   -', k)
    print('EXTRA no transcrito: %d' % len(extra))
    for k in extra:
        print('   +', k)
    print('MODELO DIFERENTE em ambos: %d' % len(differ))
    for k in differ:
        print('\n--- %s %r ---\n[OFICIAL]\n%s\n[TRANSCRITO]\n%s'
              % (k[0], k[1], fmt(co[k]), fmt(ct[k])))

    ok = not missing and not extra and not differ
    print('\nVEREDITO:', 'IDENTICOS estruturalmente' if ok else 'HA DIFERENCAS (ver acima)')

    print('\nCARREGAMENTO COMO XML SCHEMA (lxml):')
    for label, path in (('oficial', OFFICIAL), ('transcrito', TRANS)):
        try:
            etree.XMLSchema(etree.parse(path))
            print('  %-11s -> OK' % label)
        except Exception as e:
            print('  %-11s -> FALHOU: %s' % (label, e))


if __name__ == '__main__':
    main()
