# Verificação do XSD — procedência e equivalência

Data: 2026-06-22.

A ressalva registrada nas notas do projeto: o `premis-v3-0.xsd` usado nas sessões anteriores foi
**transcrito** a partir de texto colado num chat. Para produção, valia baixar
o XSD oficial e comparar. Isto é o registro dessa comparação.

## Procedência do arquivo oficial

- O endereço canônico `https://www.loc.gov/standards/premis/v3/premis.xsd` está atrás de um
  desafio JavaScript do **Cloudflare** ("Just a moment…"): `curl`, `Invoke-WebRequest` e
  fetch automático recebem **HTTP 403**. Só passa um navegador real.
- O oficial foi obtido do **repositório GitHub da própria Library of Congress** (conta oficial,
  não espelho de terceiros): `LibraryOfCongress/premis-v3-0`. O schema está num arquivo
  chamado `xsd` (sem extensão).
  - URL raw: `https://raw.githubusercontent.com/LibraryOfCongress/premis-v3-0/master/xsd`
  - tamanho: 52.845 bytes · `sha256 = 03b8a77a20b32b882ad799e12262671d07ad18210c60233f4e613a1289491cba`
  - salvo neste repositório como `premis-v3-0.xsd` (raiz) — é **este** o schema que o app usa.

## Comparação estrutural (não textual)

A diferença de tamanho (52 KB oficial vs ~30 KB transcrito) é quase toda `<xs:annotation>`
(documentação) e espaços em branco — nada que afete a validação. Por isso a comparação é
**estrutural**: parse com lxml, ignorando anotação e espaços, resolvendo QNames pelo
namespace (não pela grafia do prefixo) e normalizando defaults de `minOccurs`/`maxOccurs`/
`use`; mas **preservando** ordem das sequências, choices, cardinalidades, tipos, atributos
e enumerações.

Resultado (`compare_xsd.py`):

| Componentes globais | Oficial | Transcrito |
|---|---:|---:|
| element        | 189 | 189 |
| complexType    |  56 |  56 |
| simpleType     |   2 |   2 |
| attributeGroup |   1 |   1 |
| **TOTAL**      | **248** | **248** |

- Faltando no transcrito: **0** · Extra no transcrito: **0** · Modelo divergente: **0**
- `targetNamespace`, `elementFormDefault="qualified"`, `attributeFormDefault="unqualified"`
  iguais; nenhum `import`/`include` nos dois.
- Ambos carregam como **XML Schema válido** no lxml.

**Conclusão:** a transcrição era fiel; o app passou a usar o arquivo oficial mesmo assim,
por ser o correto para produção.

## Validação em uso (xmllint-wasm), conferida contra o xmllint nativo

Com o validador já integrado (`window.PremisXSD.validate`), em navegador real servido por http:

- Documentos gerados pelo app nos **4 tipos de objeto** (file, representation, bitstream,
  intellectualEntity) e nas **4 bases de rights** (copyright, license, statute, other):
  todos **válidos**.
- Documento propositalmente quebrado (objeto `file` sem `objectCharacteristics`): **inválido**,
  com erro estruturado (`object: Missing child element(s)… objectCharacteristics`, linha 3).
- **Cross-check independente:** o `sample-valid.xml` desta pasta foi validado pelo **xmllint
  nativo** (libxml2) contra o `premis-v3-0.xsd` oficial — resultado `validates`, exit 0.
  Ou seja, o motor WebAssembly do navegador concorda com o libxml2 nativo.

## Como reproduzir

```bash
# comparação estrutural oficial × transcrito
python docs/verificacao-xsd/compare_xsd.py

# cross-check do documento de exemplo com xmllint nativo (offline)
xmllint --noout --nonet --schema premis-v3-0.xsd docs/verificacao-xsd/sample-valid.xml
```

## Arquivos desta pasta

```
premis-v3-0.transcrito.xsd   a transcrição anterior (guardada para o registro)
compare_xsd.py               a comparação estrutural (reproduzível)
sample-valid.xml             documento de exemplo usado no cross-check com xmllint nativo
VERIFICACAO.md               este documento
```
