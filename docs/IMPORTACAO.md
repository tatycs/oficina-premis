# Importação na Oficina PREMIS

A aba **importar arquivo** (no painel "Origem") tem dois caminhos: importar um
`premis.xml` inteiro para edição, ou importar **CSV/JSON** de um sistema produtor
para criar entidades em lote. Tudo roda no navegador — nenhum arquivo sai da máquina.

## 1. Importar um `premis.xml` (PREMIS 3.0) e editar

Use isto para abrir um documento PREMIS existente, revisar e ajustar.

1. No painel **Origem**, clique em **importar arquivo**.
2. Em **Importar premis.xml**, clique em **escolher premis.xml** e selecione o arquivo.
3. O documento é carregado no **Modelo interno**: objects, events, agents e rights.
   - Os **vínculos** (que no XML são por identificador *Type/Value*) são religados
     automaticamente às entidades do próprio documento.
   - Aparece um resumo do que foi importado e, se houver, um aviso sobre vínculos
     **não trazidos** (ver limites abaixo).
4. Edite: em **Modelo interno**, cada card tem um botão **editar** que recarrega a
   entidade no formulário (mantendo o identificador). Altere e clique em
   **salvar alterações**. Ou use as abas (object/event/agent/rights) normalmente.
5. Em **Saída + validação**, clique em **verificar integridade** e depois **baixar .xml**.

> Importar **substitui** o conteúdo atual do modelo (há confirmação se já houver dados).

### O que é trazido
Todos os campos cobertos pelo construtor: os quatro tipos de object (file,
representation, bitstream, intellectualEntity) com suas características, fixity,
formato, storage, assinatura, environment, relationship; events com detalhe,
resultado e vínculos; agents com nome/tipo/versão/nota e vínculos
(inclusive `linkingRightsStatementIdentifier` e `linkingEnvironmentIdentifier`);
e rights (`rightsStatement`) nas quatro bases (copyright, license, statute, other).

Verificado por *round-trip*: um documento gerado pela ferramenta, importado e
gerado de novo, sai **idêntico** e válido contra o XSD oficial.

### Limites (o que NÃO é trazido)
- **Vínculos para fora do documento:** um vínculo cujo identificador não corresponde
  a nenhuma entidade do próprio arquivo é **omitido** (e listado no aviso). O modelo
  só representa vínculos entre entidades presentes.
- **`rightsExtension`, `agentExtension`, `objectCharacteristicsExtension` e demais
  `*Extension` (`xs:any`):** pontos de extensão para XML de schema externo, fora do
  escopo do construtor; não são importados.
- **`statuteInformation` repetido:** o construtor edita um por rights; ao importar,
  o primeiro é carregado.

## 2. Importar CSV/JSON (com template)

Use isto para criar várias entidades de uma vez a partir de uma planilha/exportação.
Disponível para **object**, **event** e **agent** (rights exige o formulário, por
causa da estrutura condicional por base de direito).

1. Selecione a aba da entidade (object/event/agent).
2. Clique em **baixar template CSV** ou **baixar template JSON**. O arquivo já vem
   com os cabeçalhos certos e uma linha de exemplo.
3. Preencha o template (uma linha por entidade) e salve.
4. Clique em **escolher CSV/JSON** e selecione o arquivo.
5. Confira o **mapeamento** coluna → campo (ele tenta adivinhar) e clique em
   **criar N entidade(s)**.

### Colunas dos templates
| Entidade | Colunas |
|---|---|
| object | `idType`, `idValue`, `formatName`, `originalName` |
| event  | `idType`, `idValue`, `eventType`, `dateTime` |
| agent  | `idType`, `idValue`, `name`, `type` |

O CSV/JSON cria entidades com os **campos básicos**; a estrutura completa
(sub-blocos repetíveis, assinatura, vínculos) é montada/editada no formulário.

### Exemplo de CSV (object)
```
idType,idValue,formatName,originalName
UUID,5b2c8d1e-0000-4aaa-bbbb-1234567890ab,MP3,objects/bird.mp3
```

### Exemplo de JSON (agent)
```json
[
  { "idType": "repository code", "idValue": "NRI", "name": "Not a Real Institution", "type": "organization" }
]
```

## Depois de importar
Reveja sempre em **Saída + validação**: a **camada 1** valida a estrutura contra o
XSD oficial; as **camadas 2 e 3** checam unicidade de identificadores, integridade
referencial e as expectativas do Archivematica. O download só é liberado com tudo
conforme.
