-- ─── Options ──────────────────────────────────────────────────────────────────
vim.opt.relativenumber = true
vim.opt.number         = true
vim.opt.tabstop        = 2
vim.opt.shiftwidth     = 2
vim.opt.expandtab      = true
vim.opt.smartindent    = true
vim.opt.wrap           = false
vim.opt.termguicolors  = true
vim.opt.signcolumn     = "yes"
vim.opt.updatetime     = 300
vim.opt.autoread       = true
vim.opt.clipboard      = "unnamedplus"
vim.opt.scrolloff      = 8
vim.opt.cursorline     = true

-- Сворачивание
vim.opt.foldmethod     = "expr"
vim.opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
vim.opt.foldenable     = false
vim.opt.foldlevel      = 99

-- ─── НОВОЕ: Загрузка общей палитры из ~/.config/colors.toml ──────────────────
local function load_colors()
  local f = io.open(vim.fn.expand("~/.config/colors.toml"), "r")
  if not f then
    vim.notify("colors.toml not found, using defaults", vim.log.levels.WARN)
    return {}
  end
  local colors = {}
  for line in f:lines() do
    local key, value = line:match("^(%w+)%s*=%s*\"(#[%x]+)\"")
    if key and value then
      colors[key] = value
    end
  end
  f:close()
  return colors
end

local C = load_colors()

-- Применение цветовой схемы
vim.cmd("highlight clear")
vim.cmd("set background=dark")

-- Устанавливаем цвета напрямую (без создания отдельного файла темы)
vim.api.nvim_set_hl(0, "Normal",       { fg = C.fg, bg = C.bg })
vim.api.nvim_set_hl(0, "Cursor",       { fg = C.curstext, bg = C.cursor })
vim.api.nvim_set_hl(0, "CursorLine",   { bg = "#1A1A1A" })
vim.api.nvim_set_hl(0, "Visual",       { bg = C.sel_bg, fg = C.sel_fg })
vim.api.nvim_set_hl(0, "Search",       { bg = C.sel_bg, fg = C.sel_fg })
vim.api.nvim_set_hl(0, "IncSearch",    { bg = C.brcyan, fg = C.black })
vim.api.nvim_set_hl(0, "LineNr",       { fg = C.brblack })
vim.api.nvim_set_hl(0, "CursorLineNr", { fg = C.white })
vim.api.nvim_set_hl(0, "SignColumn",   { bg = C.bg })
vim.api.nvim_set_hl(0, "Folded",       { fg = C.brblue, bg = "#1A1A1A" })
vim.api.nvim_set_hl(0, "StatusLine",   { fg = C.fg, bg = "#1A1A1A" })
vim.api.nvim_set_hl(0, "StatusLineNC", { fg = C.brblack, bg = "#0A0A0A" })

-- Синтаксис
vim.api.nvim_set_hl(0, "Comment",      { fg = C.brblack, italic = true })
vim.api.nvim_set_hl(0, "String",       { fg = C.green })
vim.api.nvim_set_hl(0, "Number",       { fg = C.yellow })
vim.api.nvim_set_hl(0, "Boolean",      { fg = C.magenta })
vim.api.nvim_set_hl(0, "Function",     { fg = C.blue })
vim.api.nvim_set_hl(0, "Keyword",      { fg = C.red })
vim.api.nvim_set_hl(0, "Identifier",   { fg = C.cyan })
vim.api.nvim_set_hl(0, "Statement",    { fg = C.red })
vim.api.nvim_set_hl(0, "Type",         { fg = C.green })
vim.api.nvim_set_hl(0, "Special",      { fg = C.magenta })
vim.api.nvim_set_hl(0, "Underlined",   { fg = C.cyan, underline = true })
vim.api.nvim_set_hl(0, "Error",        { fg = C.red, bold = true })
vim.api.nvim_set_hl(0, "Todo",         { fg = C.yellow, bold = true })

-- Диагностика
vim.api.nvim_set_hl(0, "DiagnosticError", { fg = C.red })
vim.api.nvim_set_hl(0, "DiagnosticWarn",  { fg = C.yellow })
vim.api.nvim_set_hl(0, "DiagnosticInfo",  { fg = C.blue })
vim.api.nvim_set_hl(0, "DiagnosticHint",  { fg = C.cyan })

-- Терминальные цвета (для :terminal)
vim.g.terminal_color_0  = C.black
vim.g.terminal_color_1  = C.red
vim.g.terminal_color_2  = C.green
vim.g.terminal_color_3  = C.yellow
vim.g.terminal_color_4  = C.blue
vim.g.terminal_color_5  = C.magenta
vim.g.terminal_color_6  = C.cyan
vim.g.terminal_color_7  = C.white
vim.g.terminal_color_8  = C.brblack
vim.g.terminal_color_9  = C.brred
vim.g.terminal_color_10 = C.brgreen
vim.g.terminal_color_11 = C.bryellow
vim.g.terminal_color_12 = C.brblue
vim.g.terminal_color_13 = C.brmagenta
vim.g.terminal_color_14 = C.brcyan
vim.g.terminal_color_15 = C.brwhite

-- ─── Keymaps ──────────────────────────────────────────────────────────────────
vim.g.mapleader = " "

local map = function(mode, lhs, rhs, opts)
  vim.keymap.set(mode, lhs, rhs, vim.tbl_extend("force", { noremap = true, silent = true }, opts or {}))
end

-- Общие
map("n", "<F12>", function()
  local cursor = vim.api.nvim_win_get_cursor(0)
  vim.cmd("%y+")
  vim.api.nvim_win_set_cursor(0, cursor)
  vim.notify("Скопировано в буфер обмена", vim.log.levels.INFO)
end, { desc = "Copy all lines to clipboard" })

map("n", "<leader>w", "<cmd>w<CR>", { desc = "Save" })
map("n", "<leader>q", "<cmd>q<CR>", { desc = "Quit" })
map("n", "<Esc>", "<cmd>nohlsearch<CR>")

-- Навигация между окнами
map("n", "<leader>h", "<C-w>h", { desc = "Window left" })
map("n", "<leader>j", "<C-w>j", { desc = "Window down" })
map("n", "<leader>k", "<C-w>k", { desc = "Window up" })
map("n", "<leader>l", "<C-w>l", { desc = "Window right" })

-- Создание копии окна
map("n", "<leader>H", ":leftabove vsplit<CR>",  { desc = "Copy window left" })
map("n", "<leader>L", ":rightbelow vsplit<CR>", { desc = "Copy window right" })
map("n", "<leader>K", ":topleft split<CR>",     { desc = "Copy window up" })
map("n", "<leader>J", ":botright split<CR>",    { desc = "Copy window down" })

-- Сворачивание
map("n", "<leader>[", "zM", { desc = "Fold all" })
map("n", "<leader>]", "zR", { desc = "Unfold all" })

-- Табы
map("n", "<leader>t", "<cmd>tabnew<CR>", { desc = "New tab" })
map("n", "<leader>1", "1gt", { desc = "Tab 1" })
map("n", "<leader>2", "2gt", { desc = "Tab 2" })
map("n", "<leader>3", "3gt", { desc = "Tab 3" })
map("n", "<leader>4", "4gt", { desc = "Tab 4" })
map("n", "<leader>5", "5gt", { desc = "Tab 5" })
map("n", "<leader>6", "6gt", { desc = "Tab 6" })
map("n", "<leader>7", "7gt", { desc = "Tab 7" })
map("n", "<leader>8", "8gt", { desc = "Tab 8" })
map("n", "<leader>9", "9gt", { desc = "Tab 9" })
map("n", "<leader>0", "10gt", { desc = "Tab 10" })

-- Поиск и замена
map("n", "<leader>f",  "<cmd>Telescope current_buffer_fuzzy_find<CR>", { desc = "Search in file" })
map("n", "<leader>sf", "<cmd>Telescope live_grep<CR>",                { desc = "Search in project" })
map("n", "<leader>sr", ":%s/", { desc = "Search and replace in file", silent = false })

-- Telescope
map("n", "<C-p>",   "<cmd>Telescope find_files<CR>", { desc = "Find files" })
map("n", "<C-S-p>", "<cmd>Telescope commands<CR>",   { desc = "Command palette" })

-- ─── Автообновление буфера ────────────────────────────────────────────────────
vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter", "CursorHold", "CursorHoldI" }, {
  pattern = "*",
  command = "checktime",
})

-- ─── Lazy.nvim bootstrap ──────────────────────────────────────────────────────
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- ─── Plugins ──────────────────────────────────────────────────────────────────
require("lazy").setup({

  -- НОВОЕ: tokyonight удалён, цвета заданы вручную выше

  -- Анимация курсора и прокрутки
  {
    "josstei/whisk.nvim",
    event = "VeryLazy",
    opts = {
      cursor = {
        duration = 150,
        easing = "ease-out",
        enabled = true,
      },
      scroll = {
        duration = 200,
        easing = "ease-in-out",
        enabled = true,
      },
    },
  },

  -- Файловый менеджер
  {
    "nvim-tree/nvim-tree.lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      local function on_attach(bufnr)
        local api = require("nvim-tree.api")
        api.config.mappings.default_on_attach(bufnr)

        local function edit_and_close()
          local node = api.tree.get_node_under_cursor()
          if node and node.type == "file" then
            api.node.open.edit(node)
            api.tree.close()
          else
            api.node.open.edit(node)
          end
        end

        vim.keymap.set("n", "<CR>", edit_and_close, { buffer = bufnr, noremap = true, silent = true })
        vim.keymap.set("n", "o",    edit_and_close, { buffer = bufnr, noremap = true, silent = true })
        vim.keymap.set("n", "<2-LeftMouse>", edit_and_close, { buffer = bufnr, noremap = true, silent = true })
      end

      require("nvim-tree").setup({
        on_attach     = on_attach,
        view          = { width = 30, side = "left" },
        disable_netrw = true,
        hijack_netrw  = true,
      })
      map("n", "<leader>e", "<cmd>NvimTreeToggle<CR>")
    end,
  },

  -- Статусбар
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup({
        options = {
          theme = {
            normal = {
              a = { fg = C.black, bg = C.green, gui = "bold" },
              b = { fg = C.fg, bg = "#1A1A1A" },
              c = { fg = C.brblack, bg = C.bg },
            },
            insert = {
              a = { fg = C.black, bg = C.blue, gui = "bold" },
              b = { fg = C.fg, bg = "#1A1A1A" },
              c = { fg = C.brblack, bg = C.bg },
            },
            visual = {
              a = { fg = C.black, bg = C.magenta, gui = "bold" },
              b = { fg = C.fg, bg = "#1A1A1A" },
              c = { fg = C.brblack, bg = C.bg },
            },
            replace = {
              a = { fg = C.black, bg = C.red, gui = "bold" },
              b = { fg = C.fg, bg = "#1A1A1A" },
              c = { fg = C.brblack, bg = C.bg },
            },
            command = {
              a = { fg = C.black, bg = C.yellow, gui = "bold" },
              b = { fg = C.fg, bg = "#1A1A1A" },
              c = { fg = C.brblack, bg = C.bg },
            },
            inactive = {
              a = { fg = C.brblack, bg = C.bg },
              b = { fg = C.brblack, bg = C.bg },
              c = { fg = C.brblack, bg = C.bg },
            },
          },
        },
      })
    end,
  },

  -- Fuzzy finder
  {
    "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      require("telescope").setup({
        defaults = {
          mappings = {
            i = { ["<Esc>"] = require("telescope.actions").close },
          },
        },
      })
    end,
  },

  -- Синтаксическая подсветка
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    event = { "BufReadPost", "BufNewFile" },
    config = function()
      require("nvim-treesitter").setup({
        ensure_installed = { "lua", "python", "bash", "markdown" },
        highlight        = { enable = true },
        indent           = { enable = true },
      })
    end,
  },

  -- Подсветка и навигация по ошибкам
  {
    "folke/trouble.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("trouble").setup()
    end,
  },

  -- Git-иконки в знаковой колонке
  {
    "lewis6991/gitsigns.nvim",
    config = function()
      require("gitsigns").setup({
        on_attach = function(bufnr)
          local gs = package.loaded.gitsigns
          local function bmap(mode, l, r, desc)
            vim.keymap.set(mode, l, r, { buffer = bufnr, desc = desc })
          end
          bmap("n", "]c", gs.next_hunk,        "Next hunk")
          bmap("n", "[c", gs.prev_hunk,        "Prev hunk")
          bmap("n", "<leader>gp", gs.preview_hunk, "Preview hunk")
          bmap("n", "<leader>gr", gs.reset_hunk,   "Reset hunk")
        end,
      })
    end,
  },

  -- Подсказки по хоткеям
  {
    "folke/which-key.nvim",
    event  = "VeryLazy",
    config = function() require("which-key").setup() end,
  },

  -- Автосохранение
  {
    "Pocco81/auto-save.nvim",
    config = function()
      require("auto-save").setup({
        enabled        = true,
        trigger_events = { "InsertLeave", "TextChanged" },
        condition      = function() return true end,
      })
    end,
  },

  -- Автодополнение
  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
      "L3MON4D3/LuaSnip",
      "saadparwaiz1/cmp_luasnip",
    },
    config = function()
      local cmp     = require("cmp")
      local luasnip = require("luasnip")
      cmp.setup({
        snippet = {
          expand = function(args) luasnip.lsp_expand(args.body) end,
        },
        mapping = cmp.mapping.preset.insert({
          ["<C-Space>"] = cmp.mapping.complete(),
          ["<CR>"]      = cmp.mapping.confirm({ select = true }),
          ["<Tab>"]     = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_next_item()
            elseif luasnip.expand_or_jumpable() then luasnip.expand_or_jump()
            else fallback() end
          end, { "i", "s" }),
          ["<S-Tab>"]   = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_prev_item()
            elseif luasnip.jumpable(-1) then luasnip.jump(-1)
            else fallback() end
          end, { "i", "s" }),
        }),
        sources = cmp.config.sources({
          { name = "nvim_lsp" },
          { name = "luasnip" },
          { name = "buffer" },
          { name = "path" },
        }),
      })
    end,
  },

  -- LSP
  {
    "neovim/nvim-lspconfig",
    dependencies = { "hrsh7th/cmp-nvim-lsp" },
    config = function()
      local caps = require("cmp_nvim_lsp").default_capabilities()

      -- Lua LSP
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

      -- Python LSP
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

      -- Диагностика UI
      vim.diagnostic.config({
        virtual_text   = { prefix = "●" },
        signs          = true,
        underline      = true,
        update_in_insert = false,
        severity_sort  = true,
        float          = { border = "rounded", source = "always" },
      })

      -- LSP keymaps
      vim.api.nvim_create_autocmd("LspAttach", {
        callback = function(ev)
          local b = ev.buf
          map("n", "gd",         vim.lsp.buf.definition,    { buffer = b, desc = "Go to definition" })
          map("n", "K",          vim.lsp.buf.hover,         { buffer = b, desc = "Hover" })
          map("n", "<leader>rn", vim.lsp.buf.rename,        { buffer = b, desc = "Rename" })
          map("n", "<leader>ca", vim.lsp.buf.code_action,   { buffer = b, desc = "Code action" })
          map("n", "gr",         vim.lsp.buf.references,    { buffer = b, desc = "References" })
          map("n", "[d",         vim.diagnostic.goto_prev,  { buffer = b, desc = "Prev diagnostic" })
          map("n", "]d",         vim.diagnostic.goto_next,  { buffer = b, desc = "Next diagnostic" })
        end,
      })
    end,
  },

  -- Autopairs
  {
    "windwp/nvim-autopairs",
    event = "InsertEnter",
    config = function()
      require("nvim-autopairs").setup()
    end,
  },
})
