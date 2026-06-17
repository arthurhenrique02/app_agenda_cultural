# Plano de Implementação: Agenda Cultural Admin Desktop

## 1. Visão Geral
Criação de uma versão Desktop (Electron) focada exclusivamente no **Painel Administrativo** da Agenda Cultural. O objetivo é oferecer uma experiência dedicada para os administradores gerenciarem eventos e usuários fora do navegador.

## 2. Arquitetura Técnica
- **Localização:** `frontend/desktop`
- **Framework Desktop:** Electron
- **Frontend:** React + Vite + TypeScript (Migrado do `frontend/admin`)
- **Estilização:** CSS Vanilla (seguindo o padrão atual)
- **Roteamento:** `HashRouter` (necessário para compatibilidade com o protocolo `file://` do Electron)
- **API:** Integração com o backend FastAPI existente via REST/JWT.

## 3. Lista de Tarefas (Backlog)

### Fase 1: Setup e Infraestrutura
- [ ] Criar estrutura de diretório em `frontend/desktop`
- [ ] Inicializar projeto Vite + React + TypeScript
- [ ] Instalar Electron e dependências de desenvolvimento (`electron`, `electron-builder`, `vite-plugin-electron`)
- [ ] Configurar o processo principal do Electron (`main.ts`) para abrir a janela básica

### Fase 2: Migração de Lógica e UI
- [ ] Copiar componentes, páginas e serviços de `frontend/admin/src` para `frontend/desktop/src`
- [ ] Ajustar `App.tsx` para usar `HashRouter`
- [ ] Configurar variáveis de ambiente (`.env`) para conexão com a API
- [ ] Validar fluxo de Autenticação (Login/JWT) no ambiente desktop

### Fase 3: Refinamento e Build
- [ ] Ajustar menu nativo do Electron (remover menus padrão desnecessários)
- [ ] Configurar scripts de build no `package.json`
- [ ] Gerar primeiro executável (`.exe`) para teste

---

## 4. Acompanhamento de Progresso
*Veja o arquivo `frontend/desktop/PROGRESS.md` para o status detalhado de cada tarefa.*
