local caps = require("cmp_nvim_lsp").default_capabilities()

vim.lsp.config.lua_ls = {
  cmd          = { "lua-language-server" },
  filetypes    = { "lua" },
  root_markers = { ".luarc.json", ".luarc.jsonc", ".git" },
  capabilities = caps,
  settings     = {
    Lua = {
      runtime     = { version = "LuaJIT" },
      diagnostics = { globals = { "vim" } },
      workspace   = { library = vim.api.nvim_get_runtime_file("", true) },
      telemetry   = { enable = false },
    },
  },
}
vim.lsp.enable("lua_ls")

vim.lsp.config.pyright = {
  cmd          = { "pyright-langserver", "--stdio" },
  filetypes    = { "python" },
  root_markers = { "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", ".git" },
  capabilities = caps,
  settings     = {
    python = {
      analysis = {
        typeCheckingMode         = "basic",
        autoSearchPaths          = true,
        useLibraryCodeForTypes   = true,
        diagnosticMode           = "workspace",
      },
    },
  },
}
vim.lsp.enable("pyright")

vim.diagnostic.config({
  virtual_text   = { prefix = "●" },
  signs          = true,
  underline      = true,
  update_in_insert = false,
  severity_sort  = true,
  float          = { border = "rounded", source = "always" },
})

vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(ev)
    local b = ev.buf
    vim.keymap.set("n", "gd",         vim.lsp.buf.definition,    { buffer = b, desc = "Go to definition" })
    vim.keymap.set("n", "K",          vim.lsp.buf.hover,         { buffer = b, desc = "Hover" })
    vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename,        { buffer = b, desc = "Rename" })
    vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action,   { buffer = b, desc = "Code action" })
    vim.keymap.set("n", "gr",         vim.lsp.buf.references,    { buffer = b, desc = "References" })
    vim.keymap.set("n", "[d",         vim.diagnostic.goto_prev,  { buffer = b, desc = "Prev diagnostic" })
    vim.keymap.set("n", "]d",         vim.diagnostic.goto_next,  { buffer = b, desc = "Next diagnostic" })
  end,
})
