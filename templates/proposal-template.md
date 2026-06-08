# Proposal Template — Commercial Proposal

<!--
PURPOSE:
  Template for creating commercial proposals to send to clients
  after receiving and analyzing their briefing.

WORKFLOW POSITION:
  Briefing (.docx, client) → Proposal (THIS DOCUMENT) → Project Master (.md, internal)

  1. Client fills the briefing
  2. You analyze the briefing
  3. You use THIS template to create a commercial proposal (3 options)
  4. Client reviews, negotiates, approves one option
  5. Approved proposal + briefing → becomes input for the Project Master
  6. Project Master + Engineering Standards → implementation

OUTPUT FORMAT:
  This template is filled in Markdown for content structure.
  The final deliverable to the client is a designed PDF
  (created in Canva, Figma, or Word using this content as source).

LANGUAGE:
  - This template structure: English (consistency with other docs)
  - Final proposal sent to clients: Portuguese (PT) — match client audience
  - When filling for a real client, translate the section headers and
    placeholder content to Portuguese

CRITICAL PRINCIPLES:
  - The Essential package = what the client asked for in the briefing
  - The Professional package = Essential + value the client benefits from
    but didn't ask for (consultive upsell)
  - The Premium package = Professional + scale, automation, optimization
  - Be EXPLICIT about what is included AND what is NOT included
    (prevents disputes later)
  - Default payment: 50% on signing, 50% on delivery
  - Maintenance is ALWAYS quoted separately (monthly or annual)

AI AGENT INSTRUCTIONS:
  When helping fill this template for a real client:
  1. Read the client's briefing first (briefing answers)
  2. Read the project-master-template.md to understand what the
     project will eventually need
  3. Map each briefing answer to the appropriate proposal section
  4. For the Essential package: include EXACTLY what the client asked for
  5. For Professional and Premium: propose VALUABLE additions that:
     - Solve real problems implied by the briefing
     - Are not random features — each must have clear business value
     - Should be explained in client-friendly language (NOT technical jargon)
  6. NEVER invent prices — leave price placeholders for the human to fill
  7. NEVER promise specific deadlines without confirmation — use ranges
  8. Flag anything ambiguous in the briefing that needs clarification
     before the proposal is sent
  9. The output language for the final proposal MUST be Portuguese (PT)

REFERENCES:
  → briefing-template.md — Source of client requirements
  → project-master-template.md — Internal document created after proposal acceptance
  → 02-technology-radar.md — Technology choices that inform what's offered
  → 11-project-management.md — Delivery and project management
-->

---

## Document Control (Internal — remove from client-facing version)

- **Client:** `<CLIENT_NAME>`
- **Project Code:** `<INTERNAL_CODE>`
- **Proposal Version:** `1.0`
- **Created Date:** `<YYYY-MM-DD>`
- **Valid Until:** `<YYYY-MM-DD>` (typically 30 days from creation)
- **Briefing Reference:** `<DATE_BRIEFING_RECEIVED>`
- **Status:** `Draft | Sent | Under Negotiation | Approved | Rejected | Expired`

---

# PROPOSTA COMERCIAL

## [NOME DO PROJETO]

**Apresentado a:** [Nome do Cliente / Empresa]
**Data:** [DD de Mês de AAAA]
**Validade da Proposta:** [DD de Mês de AAAA]

---

## 1. SOBRE NÓS

> *Esta secção é fixa em todas as propostas — apresenta-te como profissional. Personaliza apenas se o cliente já te conhece bem.*

[Breve apresentação tua / da tua marca: 1-2 parágrafos]

**Exemplo de conteúdo a desenvolver:**
- Quem és e qual é a tua especialização
- Anos de experiência relevante
- Tipo de projetos que realizas
- O que te diferencia (foco em qualidade, código limpo, suporte próximo, etc.)
- 1-2 projetos anteriores relevantes (se aplicável)

---

## 2. RESUMO EXECUTIVO

> *Esta secção mostra ao cliente que percebeste o que ele precisa. É das mais importantes — gera confiança imediata.*

### 2.1 O Vosso Negócio

[2-3 linhas resumindo o negócio do cliente, baseado no briefing]

### 2.2 O Que Procuram

[Parágrafo claro descrevendo o problema/necessidade que o cliente apresentou no briefing. Deve sentir-se compreendido ao ler isto.]

### 2.3 A Nossa Proposta

[Parágrafo de alto nível explicando a abordagem que propõem. Apresentar as 3 opções como diferentes níveis de ambição:]

> *Apresentamos três opções de pacote, desenhadas para se adaptarem a diferentes níveis de investimento e ambição:*
>
> - **🥉 Pacote Essencial** — A solução base que responde diretamente ao vosso pedido inicial.
> - **🥈 Pacote Profissional** — A solução recomendada, que adiciona funcionalidades de elevado valor para o vosso negócio.
> - **🥇 Pacote Premium** — A solução completa, com automação avançada, otimizações de crescimento e suporte alargado.

---

## 3. ANÁLISE DAS NECESSIDADES

> *Esta secção lista as funcionalidades identificadas no briefing, organizadas por categoria. Mostra rigor analítico.*

### 3.1 Funcionalidades Essenciais (mencionadas no vosso briefing)

[Listar cada funcionalidade que o cliente marcou no briefing, em linguagem clara]

- **[Funcionalidade 1]:** [Breve descrição]
- **[Funcionalidade 2]:** [Breve descrição]
- **[Funcionalidade 3]:** [Breve descrição]

### 3.2 Funcionalidades Recomendadas (sugeridas pela nossa análise)

> *Aqui é onde fazes upsell consultivo. Cada item DEVE ter justificação de valor para o negócio.*

Após análise do vosso briefing e do vosso setor, identificámos funcionalidades adicionais que poderão trazer valor significativo:

- **[Funcionalidade A]:** [Por que recomendamos — qual problema resolve / que valor traz]
- **[Funcionalidade B]:** [Por que recomendamos]
- **[Funcionalidade C]:** [Por que recomendamos]

> 💡 *Exemplo: "Sistema de Newsletter — Permite manter contacto regular com os vossos clientes, criando um canal de comunicação direta e gratuita que aumenta as vendas recorrentes."*

---

## 4. PACOTES PROPOSTOS

> *O coração da proposta. Apresentar com clareza absoluta o que cada pacote inclui e exclui.*

### 4.1 Tabela Comparativa

| Funcionalidade / Característica | 🥉 Essencial | 🥈 Profissional | 🥇 Premium |
|---------------------------------|:------------:|:----------------:|:----------:|
| **DESIGN E IDENTIDADE**---------|:------------:|:----------------:|:----------:|
| Design responsivo (mobile-first)|      ✅     |        ✅        |     ✅     |
| Identidade visual personalizada |    Básica    |       ✅        |   Premium   |
| Animações e microinterações     |       —      |     Básicas      |  Avançadas |
| **CONTEÚDO E ESTRUTURA**--------|:------------:|:----------------:|:----------:|
| Páginas institucionais          |      [N]     |       [N+X]      | Ilimitadas |
| Multilíngue                     |       —      |         —        |     ✅     |
| Blog / Notícias                 |       —      |        ✅        |     ✅    |
| **FUNCIONALIDADES**-------------|:------------:|:----------------:|:----------:|
| [Funcionalidade do briefing 1]  |      ✅     |        ✅        |     ✅     |
| [Funcionalidade do briefing 2]  |      ✅     |        ✅        |     ✅     |
| [Funcionalidade recomendada A]  |       —     |        ✅        |     ✅     |
| [Funcionalidade recomendada B]  |       —     |         —         |     ✅     |
| **GESTÃO E BACKOFFICE**---------|:-----------:|:-----------------:|:-----------:|
| Painel de administração         |    Básico   |      Completo     |   Avançado  |
| Gestão de utilizadores          | 1 utilizador |       Até 5      |   Ilimitado |
| Estatísticas e relatórios       |    Básicas   |     Detalhadas   | Avançadas + exportação |
| **SEO E PERFORMANCE**-----------|:------------:|:----------------:|:-----------:|
| SEO técnico (meta tags, sitemap)|      ✅     |        ✅        |     ✅     |
| Otimização de velocidade        |   Standard   |     Avançada     |   Premium   |
| Integração Google Analytics     |      ✅     |        ✅        |     ✅     |
| Schema markup avançado          |       —     |        ✅        |     ✅     |
| **SEGURANÇA** ------------------|:------------:|:----------------:|:-----------:|
| HTTPS e certificado SSL         |      ✅     |        ✅        |     ✅     |
| Backups automáticos             |   Semanais   |     Diários      | Diários + retenção alargada |
| Proteção contra spam            |    Básica    |    Avançada      | Avançada + monitorização |
| **INTEGRAÇÕES** ----------------|:------------:|:----------------:|:----------:|
| [Integração 1, ex: Email]       |      ✅     |        ✅        |     ✅     |
| [Integração 2, ex: Stripe]      |       —     |        ✅        |     ✅     |
| [Integração 3, ex: ERP]         |       —     |         —         |     ✅     |
| **FORMAÇÃO E ENTREGA** ---------|:------------:|:----------------:|:-----------:|
| Documentação de utilização      |     Básica  |      Completa     | Completa + vídeos |
| Sessão de formação              |     1 hora  |      2 horas      | 4 horas + manual |
| Período de garantia (bug fixing)|    30 dias  |      60 dias      |    90 dias  |

> *Personaliza esta tabela ao projecto — remove categorias irrelevantes, adiciona específicas. Não tentes meter tudo, foca no que importa para este cliente.*

---

### 4.2 🥉 PACOTE ESSENCIAL

#### Descrição
[1-2 parágrafos explicando para quem é este pacote e que objectivos cumpre]

> *Exemplo: "O Pacote Essencial é a base sólida do vosso projeto. Inclui todas as funcionalidades que indicaram como essenciais no briefing inicial. É a opção ideal para começar com uma presença digital profissional, focada no essencial."*

#### O Que Está Incluído

**Desenvolvimento e Design**
- [Item específico 1]
- [Item específico 2]
- [Item específico 3]

**Funcionalidades**
- [Funcionalidade do briefing 1]
- [Funcionalidade do briefing 2]
- [Funcionalidade do briefing 3]

**Entrega**
- [Item de entrega 1]
- [Item de entrega 2]

#### O Que NÃO Está Incluído

> ⚠️ *Esta secção é CRÍTICA. Lista explicitamente o que está fora do scope para evitar disputas posteriores.*

- [Item NÃO incluído 1] — *disponível no Pacote Profissional*
- [Item NÃO incluído 2] — *disponível no Pacote Premium*
- [Item NÃO incluído 3] — *cotação à parte*

#### Prazo Estimado de Entrega
**[X-Y semanas]** após adjudicação e receção dos conteúdos por parte do cliente.

#### Investimento
**[€VALOR]** *(IVA não incluído)*

**Forma de Pagamento:**
- 50% na adjudicação: **[€VALOR]**
- 50% na entrega final: **[€VALOR]**

---

### 4.3 🥈 PACOTE PROFISSIONAL

> ⭐ **A nossa recomendação para a maioria dos projetos**

#### Descrição
[1-2 parágrafos explicando o valor adicional e para quem é ideal]

> *Exemplo: "O Pacote Profissional é a nossa recomendação. Inclui tudo o que está no Essencial, e adiciona funcionalidades que sabemos, pela experiência, fazerem diferença real no dia-a-dia do vosso negócio. É o equilíbrio ideal entre investimento e retorno."*

#### O Que Está Incluído

**Tudo o que está no Pacote Essencial, mais:**

**Funcionalidades Adicionais**
- **[Funcionalidade A]:** [Breve descrição do valor que traz]
- **[Funcionalidade B]:** [Breve descrição do valor que traz]
- **[Funcionalidade C]:** [Breve descrição do valor que traz]

**Otimizações**
- [Otimização 1]
- [Otimização 2]

**Entrega Reforçada**
- [Item de entrega adicional 1]
- [Item de entrega adicional 2]

#### O Que NÃO Está Incluído

- [Item NÃO incluído 1] — *disponível no Pacote Premium*
- [Item NÃO incluído 2] — *cotação à parte*

#### Prazo Estimado de Entrega
**[X-Y semanas]** após adjudicação e receção dos conteúdos.

#### Investimento
**[€VALOR]** *(IVA não incluído)*

**Forma de Pagamento:**
- 50% na adjudicação: **[€VALOR]**
- 50% na entrega final: **[€VALOR]**

---

### 4.4 🥇 PACOTE PREMIUM

#### Descrição
[1-2 parágrafos explicando o valor diferencial — automação, escala, suporte alargado]

> *Exemplo: "O Pacote Premium é a solução mais completa que oferecemos. Inclui tudo o que está nos pacotes anteriores, e adiciona automação avançada, integrações complexas e otimizações pensadas para crescimento. É a opção certa para quem quer uma solução robusta e preparada para escalar."*

#### O Que Está Incluído

**Tudo o que está no Pacote Profissional, mais:**

**Funcionalidades Avançadas**
- **[Funcionalidade Premium 1]:** [Breve descrição]
- **[Funcionalidade Premium 2]:** [Breve descrição]
- **[Funcionalidade Premium 3]:** [Breve descrição]

**Automação e Integrações**
- [Integração ou automação 1]
- [Integração ou automação 2]

**Suporte Alargado**
- [Item de suporte 1]
- [Item de suporte 2]

#### O Que NÃO Está Incluído

- [Item NÃO incluído 1] — *cotação à parte*
- [Item NÃO incluído 2] — *cotação à parte*

#### Prazo Estimado de Entrega
**[X-Y semanas]** após adjudicação e receção dos conteúdos.

#### Investimento
**[€VALOR]** *(IVA não incluído)*

**Forma de Pagamento:**
- 50% na adjudicação: **[€VALOR]**
- 50% na entrega final: **[€VALOR]**

---

## 5. METODOLOGIA DE TRABALHO

> *Mostra ao cliente como o trabalho é feito. Cria confiança e estabelece expectativas.*

### 5.1 Fases do Projeto

**Fase 1 — Descoberta e Planeamento** *(Semana 1)*
- Reunião de kick-off
- Definição detalhada de requisitos
- Apresentação do plano de execução

**Fase 2 — Design e Aprovação** *(Semana 2-3)*
- Criação dos mockups e wireframes
- Sessões de feedback
- Aprovação do design final

**Fase 3 — Desenvolvimento** *(Semana X-Y)*
- Implementação das funcionalidades
- Testes contínuos
- Pontos de validação intermédios

**Fase 4 — Testes e Refinamento** *(Semana Z)*
- Testes em ambientes reais
- Correção de problemas identificados
- Ajustes finais com base no feedback

**Fase 5 — Lançamento e Formação**
- Migração para ambiente final
- Sessão de formação
- Entrega da documentação
- Início do período de garantia

> *Adapta os tempos ao pacote escolhido. Nem todos os projectos seguem todas as fases.*

### 5.2 Comunicação Durante o Projeto

- **Updates regulares** sobre o progresso (semanais ou conforme acordado)
- **Reuniões de validação** nos pontos-chave do projeto
- **Canal direto de comunicação** (Email / WhatsApp / Reunião)
- **Documentação de decisões** importantes para referência futura

### 5.3 O Que Precisamos de Vós

Para que o projeto avance no prazo previsto, precisamos:

- **Conteúdos** (textos, imagens, logos) entregues nas datas acordadas
- **Acessos necessários** (domínio, hosting, contas de redes sociais, etc.)
- **Disponibilidade** para reuniões de validação nos pontos-chave
- **Decisões atempadas** quando solicitadas

---

## 6. APÓS O LANÇAMENTO

### 6.1 Período de Garantia

Após a entrega final, oferecemos um período de garantia para correção de bugs e problemas técnicos do desenvolvimento original:

- **Pacote Essencial:** 30 dias
- **Pacote Profissional:** 60 dias
- **Pacote Premium:** 90 dias

> *A garantia cobre problemas técnicos do que foi desenvolvido. Não inclui novas funcionalidades, alterações de scope ou problemas causados por terceiros (ex: alterações no servidor pelo cliente).*

### 6.2 Manutenção (Opcional)

A manutenção contínua é cotada à parte e pode ser contratada após o lançamento. Recomendamos manutenção contínua para garantir:

- **Atualizações de segurança** regulares
- **Atualizações tecnológicas** (frameworks, bibliotecas)
- **Backups verificados**
- **Monitorização de uptime e performance**
- **Suporte rápido** a problemas
- **Pequenas alterações** de conteúdo

**Modalidades disponíveis:**

| Plano | Inclui | Investimento |
|---|---|---|
| **Manutenção Mensal** | [Descrição do que está incluído] | **[€VALOR/mês]** |
| **Manutenção Anual** | [Descrição — geralmente com desconto] | **[€VALOR/ano]** |
| **Pontual** | Por tarefa, mediante orçamento | A cotar |

> *Apresenta a manutenção como um valor para o cliente, não como uma venda extra. Foca no risco de não ter manutenção (segurança, downtime, perda de tráfego).*

### 6.3 Hospedagem e Domínio

[Escolher uma das opções:]

**Opção A — Cliente gere:**
> Não está incluído neste orçamento. O cliente é responsável por contratar e gerir o alojamento e o registo de domínio. Podemos recomendar fornecedores de confiança.

**Opção B — Setup inicial incluído:**
> Incluímos o setup inicial num fornecedor à vossa escolha. A renovação anual e custos correntes ficam a cargo do cliente.

**Opção C — Gestão completa (parte da manutenção):**
> Disponível como parte do plano de manutenção contínua.

---

## 7. INVESTIMENTO RESUMIDO

| Pacote | Investimento (sem IVA) | Prazo |
|---|---:|---|
| 🥉 **Essencial** | **[€VALOR]** | [X] semanas |
| 🥈 **Profissional** ⭐ | **[€VALOR]** | [X] semanas |
| 🥇 **Premium** | **[€VALOR]** | [X] semanas |
| **Manutenção Mensal** *(opcional)* | **[€VALOR/mês]** | Após lançamento |

> 💡 *Nota: Todos os valores são em euros e não incluem IVA à taxa legal em vigor.*

---

## 8. TERMOS E CONDIÇÕES

### 8.1 Validade da Proposta

Esta proposta é válida por **30 dias** a partir da data de emissão. Após este prazo, os valores e prazos podem necessitar de revisão.

### 8.2 Adjudicação

A adjudicação do projeto formaliza-se através de:

- Aceitação por escrito (email ou documento assinado)
- Pagamento da primeira parcela (50% do valor total)

Após a adjudicação, é assinado um contrato de prestação de serviços com os termos detalhados.

### 8.3 Pagamentos

- **50% na adjudicação** — para início dos trabalhos
- **50% na entrega final** — após aprovação do projeto pelo cliente

### 8.4 Alterações ao Scope

Alterações ao scope acordado durante o projeto serão tratadas como:

- **Alterações menores** (até 2 horas de trabalho): incluídas no preço inicial
- **Alterações significativas**: orçamentadas à parte e necessitam de aprovação prévia

### 8.5 Propriedade Intelectual

- Após pagamento integral, **a propriedade do código e dos conteúdos desenvolvidos é transferida para o cliente**
- O desenvolvedor mantém o direito de utilizar o trabalho realizado em portfólio (sem divulgar dados confidenciais)
- Bibliotecas open-source utilizadas mantêm as suas licenças originais

### 8.6 Confidencialidade

Toda a informação partilhada pelo cliente durante o projeto é tratada com confidencialidade. Mediante pedido, podemos assinar um NDA específico antes da partilha de informação sensível.

### 8.7 Cancelamento

- **Cancelamento pelo cliente após adjudicação:** A primeira parcela não é reembolsável (cobre o trabalho já planeado e iniciado).
- **Cancelamento pelo desenvolvedor:** Em caso de impossibilidade de continuar (raro), reembolso proporcional ao trabalho não entregue.

### 8.8 Garantia

O período de garantia (30, 60 ou 90 dias conforme o pacote) cobre **bugs e problemas técnicos** do desenvolvimento original. Não cobre:

- Novas funcionalidades não previstas
- Alterações ao scope original
- Problemas causados por intervenções de terceiros
- Atualizações de bibliotecas/frameworks (parte da manutenção)

### 8.9 Limitação de Responsabilidade

A responsabilidade do desenvolvedor está limitada ao valor pago pelo cliente. Não nos responsabilizamos por perdas indiretas, lucros cessantes ou outros danos consequentes do uso ou impossibilidade de uso do produto entregue.

---

## 9. PRÓXIMOS PASSOS

Caso pretendam avançar:

1. **Confirmem o pacote escolhido** por email, whatsapp ou em reunião
2. **Marcamos uma reunião de kick-off** para detalhar requisitos e cronograma
3. **Enviamos o contrato e a fatura** da primeira parcela
4. **Após pagamento, iniciamos o projeto** na data acordada

Caso tenham dúvidas ou queiram discutir alterações à proposta, estamos disponíveis para uma reunião sem compromisso.

---

## 10. CONTACTOS

**[Nome]**
[Email]
[Telefone / WhatsApp]
[Website / LinkedIn]

---

> *Obrigado pela vossa confiança. Estamos disponíveis para qualquer esclarecimento.*

---

<!--
TEMPLATE COMPLETION CHECKLIST (for the human filling this template)

Before sending the proposal to the client, verify:

- [ ] Client name and project name correctly filled throughout
- [ ] Briefing was carefully analyzed — all client needs are reflected
- [ ] Essential package = exactly what client asked for
- [ ] Professional and Premium additions are JUSTIFIED with business value
- [ ] All prices are filled (no €VALUE placeholders left)
- [ ] All deadlines are realistic — added buffer for unknowns
- [ ] "What's NOT included" sections are filled — protects from disputes
- [ ] Maintenance options match what you can actually deliver
- [ ] Validity date is set (typically 30 days from today)
- [ ] Document Control section was REMOVED before sending to client
- [ ] AI Agent Instructions comments at the top were REMOVED
- [ ] All text is in Portuguese (PT)
- [ ] Tone is professional but human — read it out loud
- [ ] Numbers add up correctly (50% + 50% = total)
- [ ] Final formatting in Canva/Figma/Word maintains structure clarity
- [ ] PDF version is properly designed before sending
-->
