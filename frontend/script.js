const API_URL = "http://localhost:8000";
const PAGE_LIMIT = 50;

const state = {
  page: 1,
  total: 0,
  filters: {},
};

const form = document.querySelector("#produto-form");
const filterForm = document.querySelector("#filter-form");
const tbody = document.querySelector("#produtos-tbody");
const message = document.querySelector("#message");
const statusApi = document.querySelector("#status-api");
const formTitle = document.querySelector("#form-title");
const submitButton = document.querySelector("#submit-button");
const cancelButton = document.querySelector("#cancel-button");
const pageInfo = document.querySelector("#page-info");
const totalInfo = document.querySelector("#total-info");
const prevPageButton = document.querySelector("#prev-page");
const nextPageButton = document.querySelector("#next-page");

function showMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

async function requestJson(url, options = {}) {
  /** Envia uma requisição HTTP e converte a resposta JSON quando existir. */
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Erro HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function buildListUrl() {
  /** Monta a URL de listagem com paginação e filtros opcionais. */
  const params = new URLSearchParams({
    page: String(state.page),
    limit: String(PAGE_LIMIT),
  });

  Object.entries(state.filters).forEach(([key, value]) => {
    if (value !== "") {
      params.set(key, value);
    }
  });

  return `${API_URL}/produtos?${params.toString()}`;
}

function formatCurrency(value) {
  return Number(value).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function renderProdutos(produtos) {
  /** Atualiza o DOM da tabela com os produtos recebidos da API. */
  tbody.innerHTML = "";

  if (produtos.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="6">Nenhum produto encontrado.</td>';
    tbody.appendChild(row);
    return;
  }

  produtos.forEach((produto) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${produto.id}</td>
      <td>${produto.nome}</td>
      <td>${produto.categoria}</td>
      <td>${formatCurrency(produto.preco)}</td>
      <td>${produto.estoque}</td>
      <td>
        <button type="button" class="secondary" data-action="edit" data-id="${produto.id}">Editar</button>
        <button type="button" class="danger" data-action="delete" data-id="${produto.id}">Excluir</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function updatePagination() {
  const totalPages = Math.max(1, Math.ceil(state.total / PAGE_LIMIT));
  pageInfo.textContent = `Página ${state.page} de ${totalPages}`;
  totalInfo.textContent = `${state.total} produto(s) encontrado(s).`;
  prevPageButton.disabled = state.page <= 1;
  nextPageButton.disabled = state.page >= totalPages;
}

async function loadProdutos() {
  /** Busca produtos na API quando a página abre ou quando filtros/página mudam. */
  try {
    showMessage("Carregando produtos...");
    const data = await requestJson(buildListUrl());
    state.total = data.total;
    renderProdutos(data.items);
    updatePagination();
    showMessage("Produtos carregados.");
  } catch (error) {
    showMessage(error.message, true);
  }
}

function readFormData() {
  /** Lê o formulário e monta o JSON esperado pelos schemas Pydantic da API. */
  return {
    nome: document.querySelector("#nome").value.trim(),
    categoria: document.querySelector("#categoria").value,
    preco: document.querySelector("#preco").value,
    estoque: Number(document.querySelector("#estoque").value),
    descricao: document.querySelector("#descricao").value.trim() || null,
  };
}

function resetForm() {
  form.reset();
  document.querySelector("#produto-id").value = "";
  formTitle.textContent = "Cadastrar produto";
  submitButton.textContent = "Salvar";
  cancelButton.hidden = true;
}

async function fillFormForEdit(id) {
  /** Carrega um produto por ID e troca o formulário para o modo edição. */
  try {
    const produto = await requestJson(`${API_URL}/produtos/${id}`);
    document.querySelector("#produto-id").value = produto.id;
    document.querySelector("#nome").value = produto.nome;
    document.querySelector("#categoria").value = produto.categoria;
    document.querySelector("#preco").value = produto.preco;
    document.querySelector("#estoque").value = produto.estoque;
    document.querySelector("#descricao").value = produto.descricao || "";
    formTitle.textContent = `Editar produto #${produto.id}`;
    submitButton.textContent = "Atualizar";
    cancelButton.hidden = false;
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function deleteProduto(id) {
  /** Envia DELETE para a API e recarrega a página atual após a exclusão. */
  const confirmed = window.confirm(`Excluir o produto #${id}?`);
  if (!confirmed) {
    return;
  }

  try {
    await requestJson(`${API_URL}/produtos/${id}`, { method: "DELETE" });
    showMessage("Produto excluído.");
    await loadProdutos();
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function checkHealth() {
  /** Verifica o endpoint /health para sinalizar conexão API + banco. */
  try {
    await requestJson(`${API_URL}/health`);
    statusApi.textContent = "API conectada";
    statusApi.className = "status ok";
  } catch {
    statusApi.textContent = "API indisponível";
    statusApi.className = "status error";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const id = document.querySelector("#produto-id").value;
  const payload = readFormData();
  const isEditing = id !== "";

  try {
    await requestJson(isEditing ? `${API_URL}/produtos/${id}` : `${API_URL}/produtos`, {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    resetForm();
    showMessage(isEditing ? "Produto atualizado." : "Produto cadastrado.");
    await loadProdutos();
  } catch (error) {
    showMessage(error.message, true);
  }
});

filterForm.addEventListener("submit", (event) => {
  event.preventDefault();
  state.page = 1;
  state.filters = {
    categoria: document.querySelector("#filtro-categoria").value,
    preco_min: document.querySelector("#preco-min").value,
    preco_max: document.querySelector("#preco-max").value,
  };
  loadProdutos();
});

tbody.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }

  const id = button.dataset.id;
  if (button.dataset.action === "edit") {
    fillFormForEdit(id);
  }
  if (button.dataset.action === "delete") {
    deleteProduto(id);
  }
});

document.querySelector("#reload-button").addEventListener("click", loadProdutos);
document.querySelector("#clear-filter-button").addEventListener("click", () => {
  filterForm.reset();
  state.filters = {};
  state.page = 1;
  loadProdutos();
});
cancelButton.addEventListener("click", resetForm);
prevPageButton.addEventListener("click", () => {
  if (state.page > 1) {
    state.page -= 1;
    loadProdutos();
  }
});
nextPageButton.addEventListener("click", () => {
  const totalPages = Math.max(1, Math.ceil(state.total / PAGE_LIMIT));
  if (state.page < totalPages) {
    state.page += 1;
    loadProdutos();
  }
});

checkHealth();
loadProdutos();
